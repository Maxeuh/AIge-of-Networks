#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/select.h>

#define PORT 12345
#define BUFFER_SIZE 1024

int main() {
    int sockfd;
    struct sockaddr_in my_addr, peer_addr;
    char buffer[BUFFER_SIZE];

    // Création du socket UDP
    sockfd = socket(AF_INET, SOCK_DGRAM, 0);
    if (sockfd == -1) {
        perror("Erreur lors de la création du socket");
        exit(1);
    }

    // Configuration de l'adresse locale
    my_addr.sin_family = AF_INET;
    my_addr.sin_addr.s_addr = INADDR_ANY;
    my_addr.sin_port = htons(PORT);

    // Liaison du socket au port
    if (bind(sockfd, (struct sockaddr *)&my_addr, sizeof(my_addr)) == -1) {
        perror("Erreur lors de la liaison");
        close(sockfd);
        exit(1);
    }

    // Demander l'IP de l'autre machine
    char peer_ip[INET_ADDRSTRLEN];
    printf("Entrez l'adresse IP de l'autre machine : ");
    scanf("%s", peer_ip);
    getchar();  // Pour éviter un problème avec fgets après scanf

    // Configuration de l'adresse du destinataire
    peer_addr.sin_family = AF_INET;
    peer_addr.sin_port = htons(PORT);
    inet_pton(AF_INET, peer_ip, &peer_addr.sin_addr);

    printf("Prêt à envoyer et recevoir des messages...\n");

    // Multiplexage avec select()
    fd_set readfds;
    struct timeval timeout;
    socklen_t addr_len = sizeof(peer_addr);

    while (1) {
        FD_ZERO(&readfds);
        FD_SET(sockfd, &readfds);  // Ajouter le socket UDP
        FD_SET(STDIN_FILENO, &readfds);  // Ajouter l'entrée utilisateur (clavier)

        timeout.tv_sec = 5;  // Temps d'attente maximum (5 secondes)
        timeout.tv_usec = 0;

        // Attendre soit une entrée clavier, soit un message UDP
        int activity = select(sockfd + 1, &readfds, NULL, NULL, &timeout);

        if (activity == -1) {
            perror("Erreur avec select()");
            break;
        }

        // 📩 Vérifier si un message a été reçu
        if (FD_ISSET(sockfd, &readfds)) {
            memset(buffer, 0, BUFFER_SIZE);
            recvfrom(sockfd, buffer, BUFFER_SIZE, 0, (struct sockaddr *)&peer_addr, &addr_len);
            printf("\nMessage reçu: %s\nVous: ", buffer);
            fflush(stdout);
        }

        // ⌨️ Vérifier si l'utilisateur a tapé un message
        if (FD_ISSET(STDIN_FILENO, &readfds)) {
            fgets(buffer, BUFFER_SIZE, stdin);
            buffer[strcspn(buffer, "\n")] = 0;  // Supprimer le \n

            // Envoyer le message
            sendto(sockfd, buffer, strlen(buffer), 0, (struct sockaddr *)&peer_addr, sizeof(peer_addr));
        }
    }

    // Fermeture du socket
    close(sockfd);
    return 0;
}
