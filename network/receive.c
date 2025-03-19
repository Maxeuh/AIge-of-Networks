#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/socket.h>

#define PORT 8080                // Keep as 8080 to match broadcast_sender's output port
#define PYTHON_PORT 8081         // Port pour transmettre à Python
#define INITIAL_BUFFER_SIZE 1024 // Taille initiale du buffer
#define LOCAL_IP "172.20.1.63"   // Adresse IP locale

int main() {
    int sockfd, python_sockfd;
    struct sockaddr_in server_addr, client_addr, python_addr;
    char* buffer = NULL;
    size_t current_buffer_size = INITIAL_BUFFER_SIZE;
    socklen_t addr_len = sizeof(client_addr);

    // Allouer le buffer initial
    buffer = (char*)malloc(current_buffer_size);
    if (!buffer) {
        perror("Erreur d'allocation de mémoire pour le buffer");
        exit(EXIT_FAILURE);
    }

    // 1️⃣ Création du socket UDP pour la réception
    if ((sockfd = socket(AF_INET, SOCK_DGRAM, 0)) < 0) {
        perror("Erreur lors de la création du socket UDP");
        free(buffer);
        exit(EXIT_FAILURE);
    }
    
    // Configuration du socket en mode non-bloquant
    int current_socket_flags = fcntl(sockfd, F_GETFL, 0);
    if (current_socket_flags == -1) {
        perror("Erreur lors de la récupération des flags du socket");
        free(buffer);
        exit(EXIT_FAILURE);
    }
    
    int nonblocking_flag = O_NONBLOCK;
    int new_socket_flags = current_socket_flags | nonblocking_flag;
    
    if (fcntl(sockfd, F_SETFL, new_socket_flags) == -1) {
        perror("Erreur lors de la configuration en mode non-bloquant");
        free(buffer);
        exit(EXIT_FAILURE);
    }

    // Permettre la réutilisation de l'adresse
    int reuse = 1;
    if (setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, &reuse, sizeof(reuse)) < 0) {
        perror("Erreur lors de la configuration de SO_REUSEADDR");
        free(buffer);
        close(sockfd);
        exit(EXIT_FAILURE);
    }

    // 2️⃣ Configuration de l'adresse du serveur (récepteur)
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = INADDR_ANY; // Écouter sur toutes les interfaces
    server_addr.sin_port = htons(PORT);

    // 3️⃣ Liaison du socket au port
    if (bind(sockfd, (struct sockaddr*)&server_addr, sizeof(server_addr)) < 0) {
        perror("Erreur lors de la liaison du socket");
        free(buffer);
        close(sockfd);
        exit(EXIT_FAILURE);
    }

    // Créer le socket pour communiquer avec Python
    if ((python_sockfd = socket(AF_INET, SOCK_DGRAM, 0)) < 0) {
        perror("Erreur lors de la création du socket pour Python");
        free(buffer);
        close(sockfd);
        exit(EXIT_FAILURE);
    }

    // Configuration de l'adresse Python
    memset(&python_addr, 0, sizeof(python_addr));
    python_addr.sin_family = AF_INET;
    python_addr.sin_addr.s_addr = inet_addr("127.0.0.1"); // Localhost pour Python
    python_addr.sin_port = htons(PYTHON_PORT);

    printf("Serveur UDP en attente de messages broadcast sur le port %d (mode non-bloquant)...\n", PORT);
    printf("Messages reçus seront transmis à Python sur 127.0.0.1:%d\n", PYTHON_PORT);

    // Pour vérifier la taille du message entrant
    char peek_buffer[1];
    int peek_flag = MSG_PEEK | MSG_TRUNC;

    while (1) {
        // Vérifier d'abord la taille du message disponible sans le consommer
        int pending_msg_size = recvfrom(sockfd, peek_buffer, 1, peek_flag, 
                                       (struct sockaddr*)&client_addr, &addr_len);
                               
        if (pending_msg_size < 0) {
            if (errno == EAGAIN || errno == EWOULDBLOCK) {
                // Aucune donnée disponible
                usleep(10000);  // Attente de 10ms pour éviter une utilisation excessive du CPU
                continue;
            } else {
                perror("Erreur lors de la vérification du message");
                continue;
            }
        }
        
        // Si le message est plus grand que notre buffer actuel, le redimensionner
        if (pending_msg_size > current_buffer_size - 1) { // -1 pour le caractère nul
            size_t new_buffer_size = pending_msg_size + 1; // +1 pour le caractère nul
            char* new_buffer = (char*)realloc(buffer, new_buffer_size);
            
            if (!new_buffer) {
                perror("Échec de réallocation du buffer");
                continue;
            }
            
            buffer = new_buffer;
            current_buffer_size = new_buffer_size;
            printf("Buffer redimensionné à %zu octets\n", current_buffer_size);
        }

        // 4️⃣ Réception des données
        int recv_len = recvfrom(sockfd, buffer, current_buffer_size - 1, 0, 
                              (struct sockaddr*)&client_addr, &addr_len);
                              
        if (recv_len < 0) {
            if (errno == EAGAIN || errno == EWOULDBLOCK) {
                // Aucune donnée disponible
                usleep(10000);  // Attente de 10ms
                continue;
            } else {
                perror("Erreur lors de la réception");
                continue;
            }
        }

        if (recv_len > 0) {
            buffer[recv_len] = '\0'; // Assurer une terminaison correcte de la chaîne
            
            char client_ip[INET_ADDRSTRLEN];
            inet_ntop(AF_INET, &(client_addr.sin_addr), client_ip, INET_ADDRSTRLEN);
            
            printf("Message reçu de %s:%d (%d octets): %s\n", 
                   client_ip, ntohs(client_addr.sin_port), recv_len, buffer);
                   
            // Transférer le message à Python
            if (sendto(python_sockfd, buffer, recv_len, 0, 
                     (struct sockaddr*)&python_addr, sizeof(python_addr)) < 0) {
                perror("Erreur lors de l'envoi à Python");
            } else {
                printf("Message transféré à Python\n");
            }
        }
    }

    // Nettoyage (bien que jamais atteint dans cette boucle infinie)
    free(buffer);
    close(sockfd);
    close(python_sockfd);
    return 0;
}
