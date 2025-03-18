#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>

#define PORT 8080
#define SERVER_IP "127.0.0.1"
#define MESSAGE "Hello from the tester!"

int main() {
    int sockfd;
    struct sockaddr_in server_addr;
    char buffer[1024];

    // Création du socket UDP
    if ((sockfd = socket(AF_INET, SOCK_DGRAM, 0)) < 0) {
        perror("Erreur lors de la création du socket UDP");
        exit(EXIT_FAILURE);
    }

    // Configuration de l'adresse du serveur
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(PORT);
    if (inet_pton(AF_INET, SERVER_IP, &server_addr.sin_addr) <= 0) {
        perror("Adresse IP invalide");
        exit(EXIT_FAILURE);
    }

    // Envoi du message au serveur
    if (sendto(sockfd, MESSAGE, strlen(MESSAGE), 0, 
               (struct sockaddr*)&server_addr, sizeof(server_addr)) < 0) {
        perror("Erreur lors de l'envoi du message");
        exit(EXIT_FAILURE);
    }

    printf("Message envoyé au serveur : %s\n", MESSAGE);

    close(sockfd);
    return 0;
}
