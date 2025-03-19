#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <pthread.h>
#include <arpa/inet.h>

#define PORT 8080
#define BUFFER_SIZE 1024

int sock;
struct sockaddr_in peer_addr;
socklen_t addr_size;
int running = 1;

// Fonction pour recevoir les messages
void *receive_messages(void *arg) {
    char buffer[BUFFER_SIZE];

    while (running) {
        int recv_size = recvfrom(sock, buffer, BUFFER_SIZE, 0, (struct sockaddr *)&peer_addr, &addr_size);
        if (recv_size > 0) {
            buffer[recv_size] = '\0';
            printf("\nPair : %s\nVous : ", buffer);
            fflush(stdout);  // Force l'affichage
        }
    }
    return NULL;
}

// Fonction pour envoyer des messages
void *send_messages(void *arg) {
    char buffer[BUFFER_SIZE];

    while (running) {
        printf("Vous : ");
        fgets(buffer, BUFFER_SIZE, stdin);
        buffer[strcspn(buffer, "\n")] = 0;  // Supprimer le \n

        sendto(sock, buffer, strlen(buffer), 0, (struct sockaddr *)&peer_addr, addr_size);

        if (strcmp(buffer, "exit") == 0) {
            running = 0;  // Arrêter les threads
            break;
        }
    }
    return NULL;
}

void startChat(const char *peer_ip) {
    struct sockaddr_in my_addr;
    pthread_t recv_thread, send_thread;

    // Création du socket UDP
    if ((sock = socket(AF_INET, SOCK_DGRAM, 0)) < 0) {
        perror("Erreur de socket");
        exit(EXIT_FAILURE);
    }

    // Configuration de l'adresse locale (réception des messages)
    my_addr.sin_family = AF_INET;
    my_addr.sin_addr.s_addr = INADDR_ANY;
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
    addr_size = sizeof(peer_addr);

    printf("Chat UDP en P2P démarré ! Tapez vos messages (ou 'exit' pour quitter)\n");

    // Lancer les threads pour envoyer et recevoir simultanément
    pthread_create(&recv_thread, NULL, receive_messages, NULL);
    pthread_create(&send_thread, NULL, send_messages, NULL);

    // Attendre la fin des threads
    pthread_join(send_thread, NULL);
    pthread_join(recv_thread, NULL);

    close(sock);
}

int main() {
    char peer_ip[20];

    printf("Entrez l'IP du PC distant : ");
    scanf("%s", peer_ip);
    getchar();  // Capture le \n laissé par scanf

    startChat(peer_ip);
    return 0;
}
