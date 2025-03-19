#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <fcntl.h>
#include <errno.h>
#include <signal.h>

#define LOCAL_PORT 8082           // Changed port: use 8082 instead of 8080 for listening
#define BROADCAST_PORT 8080       // Port pour envoyer en broadcast
#define BROADCAST_IP "172.20.15.255" // Adresse de broadcast
#define LOCAL_IP "172.20.1.63"    // Adresse IP locale
#define BUFFER_SIZE 2048          // Taille du buffer

// Flag pour la gestion propre de la terminaison
volatile int running = 1;

// Gestionnaire de signal pour Ctrl+C
void handle_signal(int sig) {
    printf("\nSignal de terminaison reçu, arrêt en cours...\n");
    running = 0;
}

int main() {
    int recv_sock, broadcast_sock;
    struct sockaddr_in local_addr, broadcast_addr, client_addr;
    char buffer[BUFFER_SIZE];
    socklen_t addr_len = sizeof(client_addr);
    
    // Configuration du gestionnaire de signal
    signal(SIGINT, handle_signal);
    signal(SIGTERM, handle_signal);
    
    // Création du socket pour recevoir les messages du Python local
    if ((recv_sock = socket(AF_INET, SOCK_DGRAM, 0)) < 0) {
        perror("Erreur lors de la création du socket de réception");
        exit(EXIT_FAILURE);
    }
    
    // Configuration du socket en mode non-bloquant
    int flags = fcntl(recv_sock, F_GETFL, 0);
    if (flags == -1) {
        perror("Erreur lors de la récupération des flags");
        close(recv_sock);
        exit(EXIT_FAILURE);
    }
    
    if (fcntl(recv_sock, F_SETFL, flags | O_NONBLOCK) == -1) {
        perror("Erreur lors de la configuration en mode non-bloquant");
        close(recv_sock);
        exit(EXIT_FAILURE);
    }

    // Permettre la réutilisation de l'adresse
    int reuse = 1;
    if (setsockopt(recv_sock, SOL_SOCKET, SO_REUSEADDR, &reuse, sizeof(reuse)) < 0) {
        perror("Erreur lors de la configuration de SO_REUSEADDR");
        close(recv_sock);
        exit(EXIT_FAILURE);
    }
    
    // Configuration de l'adresse de réception
    memset(&local_addr, 0, sizeof(local_addr));
    local_addr.sin_family = AF_INET;
    local_addr.sin_addr.s_addr = inet_addr(LOCAL_IP);  // Écouter seulement sur notre interface
    local_addr.sin_port = htons(LOCAL_PORT);
    
    // Liaison du socket au port
    if (bind(recv_sock, (struct sockaddr*)&local_addr, sizeof(local_addr)) < 0) {
        perror("Erreur lors de la liaison du socket de réception");
        close(recv_sock);
        exit(EXIT_FAILURE);
    }
    
    // Création du socket pour l'envoi en broadcast
    if ((broadcast_sock = socket(AF_INET, SOCK_DGRAM, 0)) < 0) {
        perror("Erreur lors de la création du socket broadcast");
        close(recv_sock);
        exit(EXIT_FAILURE);
    }
    
    // Activation de l'option broadcast
    int broadcast_enable = 1;
    if (setsockopt(broadcast_sock, SOL_SOCKET, SO_BROADCAST, 
                  &broadcast_enable, sizeof(broadcast_enable)) < 0) {
        perror("Erreur lors de l'activation du mode broadcast");
        close(recv_sock);
        close(broadcast_sock);
        exit(EXIT_FAILURE);
    }
    
    // Configuration de l'adresse de broadcast
    memset(&broadcast_addr, 0, sizeof(broadcast_addr));
    broadcast_addr.sin_family = AF_INET;
    broadcast_addr.sin_addr.s_addr = inet_addr(BROADCAST_IP);  // Adresse broadcast
    broadcast_addr.sin_port = htons(BROADCAST_PORT);
    
    printf("Broadcast UDP configuré:\n");
    printf("- Écoute des messages du Python local sur %s:%d\n", LOCAL_IP, LOCAL_PORT);
    printf("- Envoi en broadcast sur %s:%d\n", BROADCAST_IP, BROADCAST_PORT);
    printf("Appuyez sur Ctrl+C pour quitter.\n");
    
    // Boucle principale
    while (running) {
        // Essayer de recevoir des données de Python
        int recv_len = recvfrom(recv_sock, buffer, BUFFER_SIZE - 1, 0,
                              (struct sockaddr*)&client_addr, &addr_len);
        
        if (recv_len > 0) {
            // Terminer correctement la chaîne
            buffer[recv_len] = '\0';
            
            char client_ip[INET_ADDRSTRLEN];
            inet_ntop(AF_INET, &(client_addr.sin_addr), client_ip, INET_ADDRSTRLEN);
            
            printf("Message reçu de %s:%d (%d octets): %s\n", 
                   client_ip, ntohs(client_addr.sin_port), recv_len, buffer);
            
            // Envoyer en broadcast
            if (sendto(broadcast_sock, buffer, recv_len, 0, 
                     (struct sockaddr*)&broadcast_addr, sizeof(broadcast_addr)) < 0) {
                perror("Erreur lors de l'envoi en broadcast");
            } else {
                printf("Message envoyé en broadcast: %s\n", buffer);
            }
        } else if (recv_len < 0 && errno != EAGAIN && errno != EWOULDBLOCK) {
            perror("Erreur lors de la réception");
        }
        
        // Pause pour éviter d'utiliser trop de CPU
        usleep(10000);  // 10ms
    }
    
    // Nettoyage
    close(recv_sock);
    close(broadcast_sock);
    printf("Programme terminé.\n");
    
    return 0;
}