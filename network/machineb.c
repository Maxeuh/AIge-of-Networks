#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>

#define TCP_PORT 9090
#define UDP_PORT 9091
#define BUFFER_SIZE 1048576
#define MAX_CONNECTIONS 5
#define BROADCAST_ADDR "255.255.255.255"  // Global broadcast

int main() {
    int server_sock, client_sock, broadcast_sock;
    struct sockaddr_in server_addr, client_addr, broadcast_addr;
    char buffer[BUFFER_SIZE];
    socklen_t addr_len = sizeof(client_addr);
    
    // Create TCP socket for receiving from game
    if ((server_sock = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
        perror("TCP socket creation failed");
        exit(EXIT_FAILURE);
    }
    
    // Set socket option to reuse address
    int opt = 1;
    if (setsockopt(server_sock, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt)) < 0) {
        perror("Setsockopt for TCP failed");
        close(server_sock);
        exit(EXIT_FAILURE);
    }
    
    memset(&server_addr, 0, sizeof(server_addr));
    
    // Configure TCP server address - localhost only
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = inet_addr("127.0.0.1");
    server_addr.sin_port = htons(TCP_PORT);
    
    // Bind TCP socket to address
    if (bind(server_sock, (const struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
        perror("TCP bind failed");
        close(server_sock);
        exit(EXIT_FAILURE);
    }
    
    // Listen for incoming TCP connections
    if (listen(server_sock, MAX_CONNECTIONS) < 0) {
        perror("TCP listen failed");
        close(server_sock);
        exit(EXIT_FAILURE);
    }
    
    // Create UDP socket for broadcasting
    if ((broadcast_sock = socket(AF_INET, SOCK_DGRAM, 0)) < 0) {
        perror("UDP socket creation failed");
        close(server_sock);
        exit(EXIT_FAILURE);
    }
    
    // Set socket option to allow broadcasting
    if (setsockopt(broadcast_sock, SOL_SOCKET, SO_BROADCAST, &opt, sizeof(opt)) < 0) {
        perror("Setsockopt for UDP broadcast failed");
        close(server_sock);
        close(broadcast_sock);
        exit(EXIT_FAILURE);
    }
    
    // Configure broadcast address
    memset(&broadcast_addr, 0, sizeof(broadcast_addr));
    broadcast_addr.sin_family = AF_INET;
    broadcast_addr.sin_addr.s_addr = inet_addr(BROADCAST_ADDR);
    broadcast_addr.sin_port = htons(UDP_PORT);
    
    printf("TCP server listening on 127.0.0.1:%d...\n", TCP_PORT);
    printf("Will broadcast received data to %s:%d\n", BROADCAST_ADDR, UDP_PORT);
    
    // Accept TCP connection from game client
    printf("Waiting for TCP connection...\n");
    if ((client_sock = accept(server_sock, (struct sockaddr *)&client_addr, &addr_len)) < 0) {
        perror("TCP accept failed");
        close(server_sock);
        close(broadcast_sock);
        exit(EXIT_FAILURE);
    }
    
    // Log client connection
    char client_ip[INET_ADDRSTRLEN];
    inet_ntop(AF_INET, &client_addr.sin_addr, client_ip, sizeof(client_ip));
    printf("Connected to client %s:%d\n", client_ip, ntohs(client_addr.sin_port));
    
    // Receive messages from game client and broadcast them
    while (1) {
        // Clear buffer
        memset(buffer, 0, BUFFER_SIZE);
        
        // Receive data from game
        printf("Waiting to receive data...\n");
        int bytes_read = recv(client_sock, buffer, BUFFER_SIZE - 1, 0);
        printf("bytes_read = %d\n", bytes_read);
        
        if (bytes_read <= 0) {
            if (bytes_read == 0) {
                printf("Client disconnected\n");
            } else {
                perror("recv failed");
            }
            break;
        }
        
        // Ensure null termination
        buffer[bytes_read] = '\0';
        
        // Log received message
        printf("Received: %s\n", buffer);
        
        // Parse message type
        char message_type[32] = {0};
        char *separator = strchr(buffer, ';');
        
        if (separator) {
            int type_len = separator - buffer;
            if (type_len < sizeof(message_type)) {
                strncpy(message_type, buffer, type_len);
                message_type[type_len] = '\0';
                printf("Message type: %s\n", message_type);
                printf("Content: %s\n", separator + 1);
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
    close(client_sock);
    close(server_sock);
    close(broadcast_sock);
    return 0;
}