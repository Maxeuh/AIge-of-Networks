#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <fcntl.h>
#include <errno.h>

#define UDP_RECEIVE_PORT 8080  // Port UDP pour recevoir les données
#define UDP_SEND_PORT 8081     // Port modifié pour correspondre à receive.py
#define BUFFER_SIZE 1024

int main() {
    int udp_recv_sock, udp_send_sock;
    struct sockaddr_in udp_recv_addr, udp_client_addr, udp_send_addr;
    char buffer[BUFFER_SIZE];
    socklen_t addr_len = sizeof(udp_client_addr);

    // 1️Création du socket UDP pour la réception
    if ((udp_recv_sock = socket(AF_INET, SOCK_DGRAM, 0)) < 0) {
        perror("Erreur lors de la création du socket UDP de réception");
        exit(EXIT_FAILURE);
    }

    // Configuration du socket en mode non-bloquant
    int flags = fcntl(udp_recv_sock, F_GETFL, 0);
    if (flags == -1) {
        perror("Erreur lors de la récupération des flags");
        exit(EXIT_FAILURE);
    }
    if (fcntl(udp_recv_sock, F_SETFL, flags | O_NONBLOCK) == -1) {
        perror("Erreur lors de la configuration en mode non-bloquant");
        exit(EXIT_FAILURE);
    }

    // ...existing code...

    while (1) {
        // 6️ Réception des données envoyées par l'autre ordinateur
        int recv_len = recvfrom(udp_recv_sock, buffer, BUFFER_SIZE, 0, 
                                (struct sockaddr*)&udp_client_addr, &addr_len);
        if (recv_len < 0) {
            if (errno == EAGAIN || errno == EWOULDBLOCK) {
                // Aucune donnée disponible, on attend un peu
                usleep(10000);  // 10ms
                continue;
            }
            perror("Erreur lors de la réception UDP");
            continue;
        }

        // ...existing code...
    }

    close(udp_recv_sock);
    close(udp_send_sock);
    return 0;
}