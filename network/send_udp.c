#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>

#define UDP_IP "127.0.0.1"  // Adresse IP du serveur Python (en local)
#define UDP_PORT 8081       // Port différent pour éviter les collisions
#define BUFFER_SIZE 1024

int send_message_to_python(const char* message) {
    int sockfd;
    struct sockaddr_in dest_addr;
    
    // Création du socket UDP
    if ((sockfd = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)) == -1) {
        perror("Échec de la création du socket");
        return 0;
    }
    
    // Configuration de l'adresse de destination
    memset(&dest_addr, 0, sizeof(dest_addr));
    dest_addr.sin_family = AF_INET;
    dest_addr.sin_port = htons(UDP_PORT);
    
    if (inet_aton(UDP_IP, &dest_addr.sin_addr) == 0) {
        perror("inet_aton() a échoué");
        close(sockfd);
        return 0;
    }
    
    // Envoi du message
    if (sendto(sockfd, message, strlen(message), 0, 
               (struct sockaddr*)&dest_addr, sizeof(dest_addr)) == -1) {
        perror("sendto() a échoué");
        close(sockfd);
        return 0;
    }
    
    printf("Message envoyé: %s\n", message);
    close(sockfd);
    return 1;
}

int main() {
    char buffer[BUFFER_SIZE];
    
    printf("Client UDP C prêt à envoyer des messages à %s:%d\n", UDP_IP, UDP_PORT);
    printf("Tapez 'exit' pour quitter.\n");
    
    while (1) {
        printf("Message à envoyer au Python: ");
        fgets(buffer, BUFFER_SIZE, stdin);
        
        // Supprimer le caractère de nouvelle ligne à la fin
        buffer[strcspn(buffer, "\n")] = 0;
        
        if (strcmp(buffer, "exit") == 0) {
            printf("Fermeture du client...\n");
            break;
        }
        
        send_message_to_python(buffer);
    }
    
    return 0;
}