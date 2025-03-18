#include <stdio.h>
#include <stdlib.h>
#include <winsock2.h>
#include <string.h>

#pragma comment(lib, "ws2_32.lib")  // Lien avec la bibliothèque Winsock

#define PORT 8080
#define BUFFER_SIZE 1024

void startChat(const char *ip_address) {
    WSADATA wsa;
    SOCKET sock;
    struct sockaddr_in peer_addr, my_addr;
    char buffer[BUFFER_SIZE];
    int peer_addr_size = sizeof(peer_addr);

    // Initialisation de Winsock
    if (WSAStartup(MAKEWORD(2,2), &wsa) != 0) {
        printf("Erreur Winsock. Code : %d\n", WSAGetLastError());
        exit(EXIT_FAILURE);
    }

    // Création du socket UDP
    if ((sock = socket(AF_INET, SOCK_DGRAM, 0)) == INVALID_SOCKET) {
        printf("Erreur de création du socket. Code : %d\n", WSAGetLastError());
        WSACleanup();
        exit(EXIT_FAILURE);
    }

    // Configuration de l'adresse locale (réception des messages)
    my_addr.sin_family = AF_INET;
    my_addr.sin_addr.s_addr = INADDR_ANY; // Accepte toutes les connexions
    my_addr.sin_port = htons(PORT);

    if (bind(sock, (struct sockaddr *)&my_addr, sizeof(my_addr)) == SOCKET_ERROR) {
        printf("Échec du bind. Code : %d\n", WSAGetLastError());
        closesocket(sock);
        WSACleanup();
        exit(EXIT_FAILURE);
    }

    // Configuration de l'adresse du pair (envoi des messages)
    peer_addr.sin_family = AF_INET;
    peer_addr.sin_port = htons(PORT);
    peer_addr.sin_addr.s_addr = inet_addr(ip_address);

    printf("Chat UDP en P2P démarré ! Tapez vos messages (ou 'exit' pour quitter)\n");

    // Boucle de chat
    while (1) {
        // Lecture de l'entrée utilisateur
        printf("Vous : ");
        fgets(buffer, BUFFER_SIZE, stdin);
        buffer[strcspn(buffer, "\n")] = 0;  // Supprime le \n

        // Envoi du message
        sendto(sock, buffer, strlen(buffer), 0, (struct sockaddr *)&peer_addr, sizeof(peer_addr));

        // Quitter si l'utilisateur tape "exit"
        if (strcmp(buffer, "exit") == 0) break;

        // Réception du message du pair
        int recv_size = recvfrom(sock, buffer, BUFFER_SIZE, 0, (struct sockaddr *)&peer_addr, &peer_addr_size);
        if (recv_size == SOCKET_ERROR) {
            printf("Erreur de réception. Code : %d\n", WSAGetLastError());
            break;
        }

        buffer[recv_size] = '\0';
        printf("Pair : %s\n", buffer);
    }

    // Nettoyage
    closesocket(sock);
    WSACleanup();
}

int main() {
    char ip_address[20];

    printf("Entrez l'IP du PC distant : ");
    scanf("%s", ip_address);
    getchar();  // Capture le \n laissé par scanf

    startChat(ip_address);
    return 0;
}
