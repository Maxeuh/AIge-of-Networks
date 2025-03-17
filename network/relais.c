#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <pthread.h>
#include <signal.h>
#include <errno.h>
#include <sys/select.h>


#define MAX_CLIENTS 10
#define BUFFER_SIZE 4096
#define CLIENT_PORT 8082
#define PYTHON_PORT 8081

typedef struct {
    int client_socket;
    int python_socket;
} connection_info;

int server_running = 1;

void handle_signal(int sig) { 
    server_running = 0;
    printf("Arrêt du serveur en cours...\n");
}

void error(const char *msg) { 
    perror(msg);
    exit(1);
}

void *handle_client(void *arg) {
    connection_info *info = (connection_info *)arg;
    int client_socket = info->client_socket;
    int python_socket = info->python_socket;
    char buffer[BUFFER_SIZE];
    int bytes_read;

    fd_set read_fds;
    int max_fd = (client_socket > python_socket ? client_socket : python_socket) + 1;

    while (server_running) {
        FD_ZERO(&read_fds);
        FD_SET(client_socket, &read_fds);
        FD_SET(python_socket, &read_fds);

        // Attendre activité sur l'un des deux sockets
        int activity = select(max_fd, &read_fds, NULL, NULL, NULL);

        if (activity < 0) {
            perror("Erreur select");
            break;
        }

        // Si le client externe a envoyé des données :
        if (FD_ISSET(client_socket, &read_fds)) {
            bytes_read = recv(client_socket, buffer, BUFFER_SIZE - 1, 0);
            if (bytes_read <= 0) {
                printf("Client externe déconnecté\n");
                break;
            }
            buffer[bytes_read] = '\0';
            printf("Reçu du client externe: %s\n", buffer);

            // Transmettre immédiatement à Python :
            send(python_socket, buffer, bytes_read, 0);
        }

        // Si le moteur Python a envoyé des données en premier :
        if (FD_ISSET(python_socket, &read_fds)) {
            bytes_read = recv(python_socket, buffer, BUFFER_SIZE - 1, 0);
            if (bytes_read <= 0) {
                printf("Moteur Python déconnecté\n");
                break;
            }
            buffer[bytes_read] = '\0';
            printf("Reçu du moteur Python: %s\n", buffer);

            // Transmettre immédiatement au client externe :
            send(client_socket, buffer, bytes_read, 0);
        }
    }

    // Nettoyage :
    close(client_socket);
    close(python_socket);
    free(info);
    return NULL;
}

int connect_to_python_engine() {
    int sock;
    struct sockaddr_in server_addr;
    
    sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock < 0) {
        error("Erreur à la création du socket pour le moteur Python");
    }
    
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(PYTHON_PORT);
    server_addr.sin_addr.s_addr = inet_addr("127.0.0.1");
    
    // Tentative de connexion avec quelques essais
    int retries = 5;
    int connected = 0;
    
    while (retries > 0 && !connected) {
        if (connect(sock, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
            printf("Tentative de connexion au moteur Python (%d essais restants)...\n", retries);
            retries--;
            sleep(2);  // Attendre 2 secondes avant de réessayer
        } else {
            connected = 1;
        }
    }
    
    if (!connected) {
        error("Erreur de connexion au moteur Python après plusieurs tentatives");
    }
    
    printf("Connecté au moteur de jeu Python\n");
    return sock;
}

int main() {
    int server_fd, client_socket, python_socket;
    struct sockaddr_in address;
    int opt = 1;
    int addrlen = sizeof(address);
    pthread_t thread_id;
    
    // Configurer la gestion du signal pour l'arrêt du serveur
    signal(SIGINT, handle_signal);
    
    // Création du socket serveur
    if ((server_fd = socket(AF_INET, SOCK_STREAM, 0)) == 0) {
        error("Échec création socket");
    }
    
    // Configuration des options du socket
    if (setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt))) {
        error("Échec setsockopt");
    }
    
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(CLIENT_PORT);
    
    // Attachement du socket au port
    if (bind(server_fd, (struct sockaddr *)&address, sizeof(address)) < 0) {
        error("Échec bind");
    }
    
    // Mise en écoute du socket
    if (listen(server_fd, MAX_CLIENTS) < 0) {
        error("Échec listen");
    }
    
    printf("Relais démarré. En attente de connexions sur le port %d...\n", CLIENT_PORT);
    printf("Moteur Python attendu sur 127.0.0.1:%d\n", PYTHON_PORT);
    printf("Appuyez sur Ctrl+C pour arrêter le serveur\n");
    
    while (server_running) {
        fd_set read_fds;
        struct timeval timeout;
        
        FD_ZERO(&read_fds);
        FD_SET(server_fd, &read_fds);
        
        // Définir un timeout pour permettre de vérifier server_running
        timeout.tv_sec = 1;
        timeout.tv_usec = 0;
        
        int activity = select(server_fd + 1, &read_fds, NULL, NULL, &timeout);
        
        if (activity < 0 && errno != EINTR) {
            perror("Erreur de select");
            break;
        }
        
        // Si aucune activité, vérifier server_running et continuer
        if (activity <= 0) {
            continue;
        }
        
        if ((client_socket = accept(server_fd, (struct sockaddr *)&address, (socklen_t*)&addrlen)) < 0) {
            perror("Échec accept");
            continue;
        }
        
        printf("Nouvelle connexion client acceptée\n");
        
        // Connexion au moteur Python
        python_socket = connect_to_python_engine();
        
        // Créer une structure pour passer les informations au thread
        connection_info *info = malloc(sizeof(connection_info));
        if (info == NULL) {
            perror("Erreur d'allocation mémoire");
            close(client_socket);
            close(python_socket);
            continue;
        }
        
        info->client_socket = client_socket;
        info->python_socket = python_socket;
        
        // Créer un thread pour gérer cette connexion
        if (pthread_create(&thread_id, NULL, handle_client, (void *)info) < 0) {
            perror("Échec création thread");
            free(info);
            close(client_socket);
            close(python_socket);
            continue;
        }
        
        // Détacher le thread pour qu'il se libère automatiquement
        pthread_detach(thread_id);
    }
    
    printf("Fermeture du serveur relais\n");
    close(server_fd);
    return 0;
}
