#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>

#define UDP_PORT 8080
#define BUFFER_SIZE 1024

int main() {
    int sock;
    struct sockaddr_in broadcast_addr;
    char buffer[BUFFER_SIZE];

    // Création socket
    if ((sock = socket(AF_INET, SOCK_DGRAM, 0)) < 0) {
        perror("Erreur socket");
        exit(EXIT_FAILURE);
    }

    // Activation du broadcast
    int broadcast_enable = 1;
    if (setsockopt(sock, SOL_SOCKET, SO_BROADCAST, 
                   &broadcast_enable, sizeof(broadcast_enable)) < 0) {
        perror("Erreur activation broadcast");
        exit(EXIT_FAILURE);
    }

    // Configuration adresse broadcast
    memset(&broadcast_addr, 0, sizeof(broadcast_addr));
    broadcast_addr.sin_family = AF_INET;
    broadcast_addr.sin_port = htons(UDP_PORT);
    broadcast_addr.sin_addr.s_addr = inet_addr("255.255.255.255"); // Adresse broadcast

    printf("Mode broadcast activé. Tapez vos messages:\n");
    
    while (1) {
        printf("> ");
        fgets(buffer, BUFFER_SIZE, stdin);
        buffer[strcspn(buffer, "\n")] = 0;

        if (strcmp(buffer, "quit") == 0) break;

        // Envoi en broadcast
        if (sendto(sock, buffer, strlen(buffer), 0,
                   (struct sockaddr*)&broadcast_addr, sizeof(broadcast_addr)) < 0) {
            perror("Erreur envoi broadcast");
        }
    }

    close(sock);
    return 0;
}