#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>

#define PORT 8080
#define BUFFER_SIZE 1024

void startChat(const char *peer_ip) {
    int sock;
    struct sockaddr_in my_addr, peer_addr;
    char buffer[BUFFER_SIZE];
    socklen_t addr_size = sizeof(peer_addr);

    // Création du socket UDP
    if ((sock = socket(AF_INET, SOCK_DGRAM, 0)) < 0) {
        perror("Erreur de socket");
        exit(EXIT_FAILURE);
    }

    // Configuration de l'adresse locale (réception des messages)
    my_addr.sin_family = AF_INET;
    my_addr.sin_addr.s_addr = INADDR_ANY;  // Accepter tous les messages
    my_addr.sin_port = htons(PORT);

    if (bind(sock, (struct sockaddr *)&my_addr, sizeof(my_addr)) < 0) {
        perror("Erreur de bind");
        close(sock);
        exit(EXIT_FAILURE);
    }

    // Configuration de l'adresse du pair (envoi des messages)
    peer_addr.sin_family = AF_INET;
    peer_addr.sin_port = htons(PORT);
    inet_pton(AF_INET, peer_ip, &peer_addr.sin_addr);

    printf("Chat UDP démarré ! Tapez vos messages (ou 'exit' pour quitter)\n");

    // Boucle principale pour envoyer et recevoir des messages
    while (1) {
        // Lire l'entrée utilisateur
        printf("Vous : ");
        fgets(buffer, BUFFER_SIZE, stdin);
        buffer[strcspn(buffer, "\n")] = 0;  // Supprimer \n

        // Envoyer le message au pair
        sendto(sock, buffer, strlen(buffer), 0, (struct sockaddr *)&peer_addr, addr_size);

        // Vérifier si l'utilisateur veut quitter
        if (strcmp(buffer, "exit") == 0) break;

        // Recevoir un message du pair
        int recv_size = recvfrom(sock, buffer, BUFFER_SIZE, 0, (struct sockaddr *)&peer_addr, &addr_size);
        if (recv_size < 0) {
            perror("Erreur de réception");
            break;
        }

        buffer[recv_size] = '\0';
        printf("Pair : %s\n", buffer);
    }

    close(sock);
}

int main() {
    char peer_ip[20];

    printf("Entrez l'IP du PC distant : ");
    scanf("%s", peer_ip);
    getchar();  // Consommer le \n restant

    startChat(peer_ip);
    return 0;
}
