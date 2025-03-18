#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <fcntl.h>
#include <errno.h>

#define PORT 8080  // Port d'écoute
#define BUFFER_SIZE 1024  // Taille du buffer pour les données reçues

int main() {
    int sockfd;
    struct sockaddr_in server_addr, client_addr;
    char buffer[BUFFER_SIZE];
    socklen_t addr_len = sizeof(client_addr);

    // 1️⃣ Création du socket UDP
    if ((sockfd = socket(AF_INET, SOCK_DGRAM, 0)) < 0) {
        perror("Erreur lors de la création du socket UDP");
        exit(EXIT_FAILURE);
    }
    
    // Configuration du socket en mode non-bloquant
    int flags = fcntl(sockfd, F_GETFL, 0);
    if (flags == -1) {
        perror("Erreur lors de la récupération des flags du socket");
        exit(EXIT_FAILURE);
    }
    
    if (fcntl(sockfd, F_SETFL, flags | O_NONBLOCK) == -1) {
        perror("Erreur lors de la configuration en mode non-bloquant");
        exit(EXIT_FAILURE);
    }

    // 2️⃣ Configuration de l'adresse du serveur
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = INADDR_ANY;
    server_addr.sin_port = htons(PORT);

    // 3️⃣ Liaison du socket au port
    if (bind(sockfd, (struct sockaddr*)&server_addr, sizeof(server_addr)) < 0) {
        perror("Erreur lors de la liaison du socket");
        exit(EXIT_FAILURE);
    }

    printf("Serveur UDP en attente de messages sur le port %d (mode non-bloquant)...\n", PORT);

    while (1) {
        // 4️⃣ Réception des données envoyées par Python
        int recv_len = recvfrom(sockfd, buffer, BUFFER_SIZE, 0, 
                                (struct sockaddr*)&client_addr, &addr_len);
        if (recv_len < 0) {
            if (errno == EAGAIN || errno == EWOULDBLOCK) {
                // Aucune donnée disponible, aucune erreur réelle
                // On peut faire autre chose ici ou simplement attendre un peu
                usleep(10000);  // Attente de 10ms pour éviter une utilisation excessive du CPU
                continue;
            } else {
                perror("Erreur lors de la réception");
                continue;
            }
        }

        if (recv_len > 0) {
            buffer[recv_len] = '\0'; // Assurer une terminaison correcte de la chaîne
            printf("Message reçu de Python : %s\n", buffer);
        }
    }

    close(sockfd);
    return 0;
}
