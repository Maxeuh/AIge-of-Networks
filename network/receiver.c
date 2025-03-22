#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>

#define PORT 9090
#define BUFFER_SIZE 1048576
#define MAX_CONNECTIONS 5

int main() {
    int server_sock, client_sock;
    struct sockaddr_in server_addr, client_addr;
    char buffer[BUFFER_SIZE];
    socklen_t addr_len = sizeof(client_addr);
    
    // Create TCP socket
    if ((server_sock = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
        perror("Socket creation failed");
        exit(EXIT_FAILURE);
    }
    
    // Set socket option to reuse address
    int opt = 1;
    if (setsockopt(server_sock, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt)) < 0) {
        perror("Setsockopt failed");
        close(server_sock);
        exit(EXIT_FAILURE);
    }
    
    memset(&server_addr, 0, sizeof(server_addr));
    
    // Configure server address - changed to localhost only
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = inet_addr("127.0.0.1"); // Changed from INADDR_ANY to localhost
    server_addr.sin_port = htons(PORT);
    
    // Bind socket to address
    if (bind(server_sock, (const struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
        perror("Bind failed");
        close(server_sock);
        exit(EXIT_FAILURE);
    }
    
    // Listen for incoming connections
    if (listen(server_sock, MAX_CONNECTIONS) < 0) {
        perror("Listen failed");
        close(server_sock);
        exit(EXIT_FAILURE);
    }
    
    printf("TCP server listening on 127.0.0.1:%d...\n", PORT);
    
    // Accept connection from client
    printf("Waiting for connection...\n");
    if ((client_sock = accept(server_sock, (struct sockaddr *)&client_addr, &addr_len)) < 0) {
        perror("Accept failed");
        close(server_sock);
        exit(EXIT_FAILURE);
    }
    
    // Log client connection
    char client_ip[INET_ADDRSTRLEN];
    inet_ntop(AF_INET, &client_addr.sin_addr, client_ip, sizeof(client_ip));
    printf("Connected to client %s:%d\n", client_ip, ntohs(client_addr.sin_port));
    
    // Receive messages from client
    while (1) {
        // Clear buffer
        memset(buffer, 0, BUFFER_SIZE);
        
        // Receive data
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
        
        // Simple message type parsing
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
    }
    
    // Close sockets
    close(client_sock);
    close(server_sock);
    return 0;
}