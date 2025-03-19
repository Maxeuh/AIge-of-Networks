#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <pthread.h>

#define PORT 12345
#define BUFFER_SIZE 1024

void *receive_messages(void *arg) {
    int sockfd = *((int *)arg);
    struct sockaddr_in sender_addr;
    socklen_t addr_len = sizeof(sender_addr);
    char buffer[BUFFER_SIZE];

    while (1) {
        memset(buffer, 0, BUFFER_SIZE);
        recvfrom(sockfd, buffer, BUFFER_SIZE, 0, (struct sockaddr *)&sender_addr, &addr_len);
        printf("\nMessage reçu: %s\n", buffer);
        printf("Vous: "); fflush(stdout); // Remettre l'affichage au bon endroit
    }
}

int main() {
    int sockfd;
    struct sockaddr_in my_addr, peer_addr;
    char buffer[BUFFER_SIZE];
    pthread_t recv_thread;

    // Création du socket UDP
    sockfd = socket(AF_INET, SOCK_DGRAM, 0);
    if (sockfd == -1) {
        perror("Erreur lors de la création du socket");
        exit(1);
    }

    // Configuration de l'adresse locale
    my_addr.sin_family = AF_INET;
    my_addr.sin_addr.s_addr = INADDR_ANY;  // Accepte les connexions sur toutes les interfaces
    my_addr.sin_port = htons(PORT);

    // Liaison du socket au port
    if (bind(sockfd, (struct sockaddr *)&my_addr, sizeof(my_addr)) == -1) {
        perror("Erreur lors de la liaison");
        close(sockfd);
        exit(1);
    }

    // Demander l'adresse IP du destinataire
    char peer_ip[INET_ADDRSTRLEN];
    printf("Entrez l'adresse IP de l'autre machine : ");
    scanf("%s", peer_ip);
    getchar(); // Éviter le problème avec fgets

    // Configuration de l'adresse du destinataire
    peer_addr.sin_family = AF_INET;
    peer_addr.sin_port = htons(PORT);
    inet_pton(AF_INET, peer_ip, &peer_addr.sin_addr);

    // Création d'un thread pour la réception des messages
    pthread_create(&recv_thread, NULL, receive_messages, &sockfd);

    // Envoi des messages
    while (1) {
        printf("Vous: ");
        fgets(buffer, BUFFER_SIZE, stdin);
        buffer[strcspn(buffer, "\n")] = 0; // Supprimer le \n

        sendto(sockfd, buffer, strlen(buffer), 0, (struct sockaddr *)&peer_addr, sizeof(peer_addr));
    }

    // Fermeture du socket
    close(sockfd);
    return 0;
}
