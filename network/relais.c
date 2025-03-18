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

typedef struct {
    int client_socket;    // Socket pour la connexion client externe
    int python_socket;    // Socket pour la connexion au moteur Python
    int relay_socket;     // Socket pour la connexion à l'autre relais
    int is_connected_to_relay; // Indique si nous sommes connectés à l'autre relais
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

void print_usage(char *prog_name) {
    printf("Usage: %s <port_local_ecoute> <port_moteur_python> [ip_relais_distant port_relais_distant]\n", prog_name);
    printf("  port_local_ecoute   : Port sur lequel ce relais écoute les connexions client\n");
    printf("  port_moteur_python  : Port sur lequel le moteur Python local écoute\n");
    printf("  ip_relais_distant   :  Adresse IP du relais distant\n");
    printf("  port_relais_distant :  Port du relais distant\n");
    exit(1);
}

int connect_to_relay(const char *relay_ip, int relay_port) {
    int sock;
    struct sockaddr_in server_addr;
    
    sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock < 0) {
        perror("Erreur à la création du socket pour le relais distant");
        return -1;
    }
    
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(relay_port);
    server_addr.sin_addr.s_addr = inet_addr(relay_ip);
    
    // Tentative de connexion avec quelques essais
    int retries = 5;
    int connected = 0;
    
    while (retries > 0 && !connected) {
        if (connect(sock, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
            printf("Tentative de connexion au relais distant %s:%d (%d essais restants)...\n", 
                   relay_ip, relay_port, retries);
            retries--;
            sleep(2);  // Attendre 2 secondes avant de réessayer
        } else {
            connected = 1;
        }
    }
    
    if (!connected) {
        printf("Erreur de connexion au relais distant après plusieurs tentatives\n");
        close(sock);
        return -1;
    }
    
    printf("Connecté au relais distant %s:%d\n", relay_ip, relay_port);
    return sock;
}

int connect_to_python_engine(int python_port) {
    int sock;
    struct sockaddr_in server_addr;
    
    sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock < 0) {
        error("Erreur à la création du socket pour le moteur Python");
    }
    
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(python_port);
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
    
    printf("Connecté au moteur de jeu Python sur le port %d\n", python_port);
    return sock;
}

void *handle_client(void *arg) {
    connection_info *info = (connection_info *)arg;
    int client_socket = info->client_socket;
    int python_socket = info->python_socket;
    int relay_socket = info->relay_socket;
    int is_connected_to_relay = info->is_connected_to_relay;
    
    char buffer[BUFFER_SIZE];
    int bytes_read;

    fd_set read_fds;
    int max_fd = client_socket > python_socket ? client_socket : python_socket;
    
    if (is_connected_to_relay && relay_socket > max_fd) {
        max_fd = relay_socket;
    }
    max_fd += 1;

    while (server_running) {
        FD_ZERO(&read_fds);
        FD_SET(client_socket, &read_fds);
        FD_SET(python_socket, &read_fds);
        
        if (is_connected_to_relay) {
            FD_SET(relay_socket, &read_fds);
        }

        // Attendre activité sur l'un des sockets
        int activity = select(max_fd, &read_fds, NULL, NULL, NULL);

        if (activity < 0) {
            perror("Erreur select");
            break;
        }

        // Si le client externe a envoyé des données
        if (FD_ISSET(client_socket, &read_fds)) {
            bytes_read = recv(client_socket, buffer, BUFFER_SIZE - 1, 0);
            if (bytes_read <= 0) {
                printf("Client externe déconnecté\n");
                break;
            }
            buffer[bytes_read] = '\0';
            printf("Reçu du client externe: %s\n", buffer);

            // Transmettre au moteur Python
            send(python_socket, buffer, bytes_read, 0);
            
            // Si connecté à un relais, transmettre aussi au relais distant
            if (is_connected_to_relay) {
                send(relay_socket, buffer, bytes_read, 0);
            }
        }

        // Si le moteur Python a envoyé des données
        if (FD_ISSET(python_socket, &read_fds)) {
            bytes_read = recv(python_socket, buffer, BUFFER_SIZE - 1, 0);
            if (bytes_read <= 0) {
                printf("Moteur Python déconnecté\n");
                break;
            }
            buffer[bytes_read] = '\0';
            printf("Reçu du moteur Python: %s\n", buffer);

            // Transmettre au client externe
            send(client_socket, buffer, bytes_read, 0);
            
            // Si connecté à un relais, transmettre aussi au relais distant
            if (is_connected_to_relay) {
                send(relay_socket, buffer, bytes_read, 0);
            }
        }

        // Si le relais distant a envoyé des données
        if (is_connected_to_relay && FD_ISSET(relay_socket, &read_fds)) {
            bytes_read = recv(relay_socket, buffer, BUFFER_SIZE - 1, 0);
            if (bytes_read <= 0) {
                printf("Relais distant déconnecté\n");
                is_connected_to_relay = 0;
                close(relay_socket);
                continue;
            }
            buffer[bytes_read] = '\0';
            printf("Reçu du relais distant: %s\n", buffer);

            // Transmettre au client externe
            send(client_socket, buffer, bytes_read, 0);
            
            // Transmettre au moteur Python
            send(python_socket, buffer, bytes_read, 0);
        }
    }

    // Nettoyage
    close(client_socket);
    close(python_socket);
    if (is_connected_to_relay) {
        close(relay_socket);
    }
    free(info);
    return NULL;
}

int main(int argc, char *argv[]) {
    if (argc != 3 && argc != 5) {
        print_usage(argv[0]);
    }
    
    // Récupération des paramètres de la ligne de commande
    int local_port = atoi(argv[1]);
    int python_port = atoi(argv[2]);
    
    char *relay_ip = NULL;
    int relay_port = -1;
    int is_connected_to_relay = 0;
    int relay_socket = -1;
    
    if (argc == 5) {
        relay_ip = argv[3];
        relay_port = atoi(argv[4]);
    }
    
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
    address.sin_port = htons(local_port);
    
    // Attachement du socket au port
    if (bind(server_fd, (struct sockaddr *)&address, sizeof(address)) < 0) {
        error("Échec bind");
    }
    
    // Mise en écoute du socket
    if (listen(server_fd, MAX_CLIENTS) < 0) {
        error("Échec listen");
    }
    
    printf("Relais démarré. En attente de connexions sur le port %d...\n", local_port);
    printf("Moteur Python attendu sur 127.0.0.1:%d\n", python_port);
    
    // Si des paramètres de relais distant ont été fournis, tenter la connexion
    if (relay_ip != NULL && relay_port > 0) {
        relay_socket = connect_to_relay(relay_ip, relay_port);
        if (relay_socket >= 0) {
            is_connected_to_relay = 1;
            printf("Mode peer-to-peer activé avec le relais %s:%d\n", relay_ip, relay_port);
        }
    }
    
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
        python_socket = connect_to_python_engine(python_port);
        
        // Créer une structure pour passer les informations au thread
        connection_info *info = malloc(sizeof(connection_info));
        if (info == NULL) {
            perror("Erreur d'allocation mémoire");
            close(client_socket);
            close(python_socket);
            if (is_connected_to_relay) {
                close(relay_socket);
                is_connected_to_relay = 0;
            }
            continue;
        }
        
        info->client_socket = client_socket;
        info->python_socket = python_socket;
        info->relay_socket = relay_socket;
        info->is_connected_to_relay = is_connected_to_relay;
        
        // Créer un thread pour gérer cette connexion
        if (pthread_create(&thread_id, NULL, handle_client, (void *)info) < 0) {
            perror("Échec création thread");
            free(info);
            close(client_socket);
            close(python_socket);
            if (is_connected_to_relay) {
                close(relay_socket);
                is_connected_to_relay = 0;
            }
            continue;
        }
        
        // Détacher le thread pour qu'il se libère automatiquement
        pthread_detach(thread_id);
    }
    
    printf("Fermeture du serveur relais\n");
    close(server_fd);
    if (is_connected_to_relay) {
        close(relay_socket);
    }
    return 0;
}
