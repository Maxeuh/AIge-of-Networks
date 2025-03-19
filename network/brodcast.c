#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <fcntl.h>
#include <errno.h>

#define UDP_RECEIVE_PORT 8080
#define UDP_SEND_PORT 9090
#define BUFFER_SIZE 1024

int main() {
    int udp_recv_sock, udp_send_sock;
    struct sockaddr_in udp_recv_addr, udp_client_addr, udp_send_addr;
    char buffer[BUFFER_SIZE];
    socklen_t addr_len = sizeof(udp_client_addr);

    // Socket réception (étape 2️⃣)
    if ((udp_recv_sock = socket(AF_INET, SOCK_DGRAM, 0)) < 0) {
        perror("Erreur socket réception");
        exit(EXIT_FAILURE);
    }

    // Socket envoi vers Python (étape 3️⃣)
    if ((udp_send_sock = socket(AF_INET, SOCK_DGRAM, 0)) < 0) {
        perror("Erreur socket envoi");
        exit(EXIT_FAILURE);
    }

    memset(&udp_recv_addr, 0, sizeof(udp_recv_addr));
    udp_recv_addr.sin_family = AF_INET;
    udp_recv_addr.sin_addr.s_addr = INADDR_ANY;
    udp_recv_addr.sin_port = htons(UDP_RECEIVE_PORT);

    if (bind(udp_recv_sock, (struct sockaddr*)&udp_recv_addr, sizeof(udp_recv_addr)) < 0) {
        perror("Erreur bind");
        exit(EXIT_FAILURE);
    }

    // Configuration pour envoi vers Python
    memset(&udp_send_addr, 0, sizeof(udp_send_addr));
    udp_send_addr.sin_family = AF_INET;
    udp_send_addr.sin_addr.s_addr = inet_addr("127.0.0.1");
    udp_send_addr.sin_port = htons(UDP_SEND_PORT);

    printf("En attente sur port %d, transfert vers Python sur port %d\n", 
           UDP_RECEIVE_PORT, UDP_SEND_PORT);

    while (1) {
        int recv_len = recvfrom(udp_recv_sock, buffer, BUFFER_SIZE, 0,
                               (struct sockaddr*)&udp_client_addr, &addr_len);
        
        if (recv_len > 0) {
            buffer[recv_len] = '\0';
            printf("Reçu: %s\n", buffer);
            
            // Transfert vers Python (étape 3️⃣)
            sendto(udp_send_sock, buffer, recv_len, 0,
                   (struct sockaddr*)&udp_send_addr, sizeof(udp_send_addr));
        }
    }

    close(udp_recv_sock);
    close(udp_send_sock);
    return 0;
}