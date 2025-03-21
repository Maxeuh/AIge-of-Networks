#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

#define PORT 23456 // Doit correspondre au port utilisé dans ourmain_linux.c
#define BUFFER_SIZE 1024

int main() {
    int sockfd;
    struct sockaddr_in server_addr;
    char buffer[BUFFER_SIZE];
    socklen_t addr_len = sizeof(server_addr);

    // Créer un socket UDP
    sockfd = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    if (sockfd < 0) {
        perror("Socket creation failed");
        return EXIT_FAILURE;
    }

    // Configurer l'adresse pour écouter les messages
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = htonl(INADDR_ANY); // Écoute sur toutes les interfaces
    server_addr.sin_port = htons(PORT);

    // Associer le socket à l'adresse et au port
    if (bind(sockfd, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
        perror("Bind failed");
        close(sockfd);
        return EXIT_FAILURE;
    }

    printf("Listening for broadcast messages on port %d...\n", PORT);

    // Boucle pour recevoir les messages
    while (1) {
        int recv_len = recvfrom(sockfd, buffer, BUFFER_SIZE - 1, 0, 
                                (struct sockaddr *)&server_addr, &addr_len);
        if (recv_len < 0) {
            perror("recvfrom failed");
            continue;
        }

        buffer[recv_len] = '\0'; // Terminer la chaîne reçue
        printf("Received broadcast message: %s\n", buffer);
    }

    close(sockfd);
    return 0;
}
