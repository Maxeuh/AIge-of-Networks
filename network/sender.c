#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>

#define UDP_PORT 8080
#define BUFFER_SIZE 1024

int main(int argc, char *argv[]) {
    if (argc != 2) {
        printf("Usage: %s <IP_du_recepteur>\n", argv[0]);
        exit(1);
    }

    int sock;
    struct sockaddr_in dest_addr;
    char buffer[BUFFER_SIZE];

    // Création socket
    if ((sock = socket(AF_INET, SOCK_DGRAM, 0)) < 0) {
        perror("Erreur socket");
        exit(EXIT_FAILURE);
    }

    // Configuration adresse destination
    memset(&dest_addr, 0, sizeof(dest_addr));
    dest_addr.sin_family = AF_INET;
    dest_addr.sin_port = htons(UDP_PORT);
    dest_addr.sin_addr.s_addr = inet_addr(argv[1]);

    printf("Envoi de messages à %s:%d\n", argv[1], UDP_PORT);
    
    while (1) {
        printf("Entrez un message (ou 'quit' pour sortir): ");
        fgets(buffer, BUFFER_SIZE, stdin);
        buffer[strcspn(buffer, "\n")] = 0;

        if (strcmp(buffer, "quit") == 0) break;

        sendto(sock, buffer, strlen(buffer), 0,
               (struct sockaddr*)&dest_addr, sizeof(dest_addr));
    }

    close(sock);
    return 0;
}