#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>

#define UDP_PORT 8080  // Port UDP d'écoute
#define BUFFER_SIZE 1024

int main() {
    int udp_sock;
    struct sockaddr_in udp_server_addr, udp_client_addr;
    char buffer[BUFFER_SIZE];
    socklen_t addr_len = sizeof(udp_client_addr);

    // 1️ Création du socket UDP
    if ((udp_sock = socket(AF_INET, SOCK_DGRAM, 0)) < 0) {
        perror("Erreur lors de la création du socket UDP");
        exit(EXIT_FAILURE);
    }

    // 2️ Configuration de l'adresse du serveur
    memset(&udp_server_addr, 0, sizeof(udp_server_addr));
    udp_server_addr.sin_family = AF_INET;
    udp_server_addr.sin_addr.s_addr = INADDR_ANY;
    udp_server_addr.sin_port = htons(UDP_PORT);

    // 3️ Liaison du socket au port
    if (bind(udp_sock, (struct sockaddr*)&udp_server_addr, sizeof(udp_server_addr)) < 0) {
        perror("Erreur lors de la liaison du socket UDP");
        exit(EXIT_FAILURE);
    }

    printf("Serveur C en attente de messages UDP sur le port %d...\n", UDP_PORT);

    while (1) {
        // 4️ Réception des données envoyées par l'autre ordinateur
        int recv_len = recvfrom(udp_sock, buffer, BUFFER_SIZE, 0, 
                                (struct sockaddr*)&udp_client_addr, &addr_len);
        if (recv_len < 0) {
            perror("Erreur lors de la réception");
            continue;
        }

        buffer[recv_len] = '\0'; // Assurer une terminaison correcte de la chaîne
        printf("Message reçu de l'autre ordinateur : %s\n", buffer);

        // 5️ Envoyer le message à Python via un socket local
        int tcp_sock;
        struct sockaddr_in tcp_server_addr;
        
        tcp_sock = socket(AF_INET, SOCK_STREAM, 0);
        if (tcp_sock < 0) {
            perror("Erreur lors de la création du socket TCP");
            continue;
        }

        tcp_server_addr.sin_family = AF_INET;
        tcp_server_addr.sin_addr.s_addr = inet_addr("127.0.0.1");
        tcp_server_addr.sin_port = htons(9090);  // Port local pour Python

        if (connect(tcp_sock, (struct sockaddr*)&tcp_server_addr, sizeof(tcp_server_addr)) < 0) {
            perror("Erreur lors de la connexion au serveur Python");
            close(tcp_sock);
            continue;
        }

        send(tcp_sock, buffer, strlen(buffer), 0);
        close(tcp_sock);
        printf("Message transmis à Python : %s\n", buffer);
    }

    close(udp_sock);
    return 0;
}
