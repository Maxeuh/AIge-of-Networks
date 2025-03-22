#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>

#define UDP_RECEIVE_PORT 9090
#define UDP_BROADCAST_PORT 9091
#define BUFFER_SIZE 1048576
#define BROADCAST_ADDR "255.255.255.255"  // Global broadcast

int main() {
    int receive_sock, broadcast_sock;
    struct sockaddr_in receive_addr, client_addr, broadcast_addr;
    char buffer[BUFFER_SIZE];
    socklen_t addr_len = sizeof(client_addr);
    
    // Create UDP socket for receiving from game
    if ((receive_sock = socket(AF_INET, SOCK_DGRAM, 0)) < 0) {
        perror("UDP receive socket creation failed");
        exit(EXIT_FAILURE);
    }
    
    // Set socket option to reuse address
    int opt = 1;
    if (setsockopt(receive_sock, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt)) < 0) {
        perror("Setsockopt for UDP failed");
        close(receive_sock);
        exit(EXIT_FAILURE);
    }
    
    memset(&receive_addr, 0, sizeof(receive_addr));
    
    // Configure UDP server address - localhost only
    receive_addr.sin_family = AF_INET;
    receive_addr.sin_addr.s_addr = htonl(INADDR_ANY);  // Listen on all interfaces
    receive_addr.sin_port = htons(UDP_RECEIVE_PORT);
    
    // Bind UDP socket to address
    if (bind(receive_sock, (const struct sockaddr *)&receive_addr, sizeof(receive_addr)) < 0) {
        perror("UDP bind failed");
        close(receive_sock);
        exit(EXIT_FAILURE);
    }
    
    // Create UDP socket for broadcasting
    if ((broadcast_sock = socket(AF_INET, SOCK_DGRAM, 0)) < 0) {
        perror("UDP broadcast socket creation failed");
        close(receive_sock);
        exit(EXIT_FAILURE);
    }
    
    // Set socket option to allow broadcasting
    if (setsockopt(broadcast_sock, SOL_SOCKET, SO_BROADCAST, &opt, sizeof(opt)) < 0) {
        perror("Setsockopt for UDP broadcast failed");
        close(receive_sock);
        close(broadcast_sock);
        exit(EXIT_FAILURE);
    }
    
    // Configure broadcast address
    memset(&broadcast_addr, 0, sizeof(broadcast_addr));
    broadcast_addr.sin_family = AF_INET;
    broadcast_addr.sin_addr.s_addr = inet_addr(BROADCAST_ADDR);
    broadcast_addr.sin_port = htons(UDP_BROADCAST_PORT);
    
    printf("UDP receiver listening on port %d...\n", UDP_RECEIVE_PORT);
    printf("Will broadcast received data to %s:%d\n", BROADCAST_ADDR, UDP_BROADCAST_PORT);
    
    // Receive messages from game client and broadcast them
    while (1) {
        // Clear buffer
        memset(buffer, 0, BUFFER_SIZE);
        
        // Receive data from game via UDP
        printf("Waiting to receive data...\n");
        int bytes_read = recvfrom(receive_sock, buffer, BUFFER_SIZE - 1, 0,
                                 (struct sockaddr*)&client_addr, &addr_len);
        
        if (bytes_read <= 0) {
            perror("recvfrom failed");
            continue;
        }
        
        // Ensure null termination
        buffer[bytes_read] = '\0';
        
        // Log received message
        char client_ip[INET_ADDRSTRLEN];
        inet_ntop(AF_INET, &client_addr.sin_addr, client_ip, sizeof(client_ip));
        printf("Received %d bytes from %s:%d\n", bytes_read, 
               client_ip, ntohs(client_addr.sin_port));
        
        // Parse message type
        char message_type[32] = {0};
        char *separator = strchr(buffer, ';');
        
        if (separator) {
            int type_len = separator - buffer;
            if (type_len < sizeof(message_type)) {
                strncpy(message_type, buffer, type_len);
                message_type[type_len] = '\0';
                printf("Message type: %s\n", message_type);
            }
        }
        
        // Broadcast the received data
        int broadcast_result = sendto(broadcast_sock, buffer, bytes_read, 0, 
                                     (struct sockaddr*)&broadcast_addr, sizeof(broadcast_addr));
        
        if (broadcast_result < 0) {
            perror("UDP broadcast failed");
        } else {
            printf("Broadcasted %d bytes\n", broadcast_result);
        }
    }
    
    // Close sockets
    close(receive_sock);
    close(broadcast_sock);
    return 0;
}