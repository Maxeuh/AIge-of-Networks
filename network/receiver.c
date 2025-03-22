#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>

#define TCP_PORT 9090
#define UDP_BROADCAST_PORT 9091
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
    
    // Configure TCP server address
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = htonl(INADDR_ANY);  // Listen on all interfaces
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
    broadcast_addr.sin_port = htons(UDP_BROADCAST_PORT);
    
    printf("TCP server listening on port %d...\n", TCP_PORT);
    printf("Will broadcast received data to %s:%d\n", BROADCAST_ADDR, UDP_BROADCAST_PORT);
    
    while (1) {
        // Accept TCP connection from game client
        printf("Waiting for TCP connection...\n");
        if ((client_sock = accept(server_sock, (struct sockaddr *)&client_addr, &addr_len)) < 0) {
            perror("TCP accept failed");
            continue;
        }
        
        // Log client connection
        char client_ip[INET_ADDRSTRLEN];
        inet_ntop(AF_INET, &client_addr.sin_addr, client_ip, sizeof(client_ip));
        printf("Connected to client %s:%d\n", client_ip, ntohs(client_addr.sin_port));
        
        // Receive and relay messages
        while (1) {
            // Clear buffer
            memset(buffer, 0, BUFFER_SIZE);
            
            // First read the message length (4 bytes)
            uint32_t length = 0;
            int bytes_read = recv(client_sock, &length, 4, 0);
            
            if (bytes_read <= 0) {
                if (bytes_read == 0) {
                    printf("Client disconnected\n");
                } else {
                    perror("recv failed");
                }
                break;
            }
            
            // Convert network byte order to host byte order
            length = ntohl(length);
            printf("Expecting message of length: %u bytes\n", length);
            
            if (length > BUFFER_SIZE - 1) {
                printf("Message too large (%u bytes), max is %d\n", length, BUFFER_SIZE - 1);
                break;
            }
            
            // Now read the actual message data
            bytes_read = 0;
            int remaining = length;
            
            while (remaining > 0) {
                int n = recv(client_sock, buffer + bytes_read, remaining, 0);
                if (n <= 0) {
                    if (n == 0) {
                        printf("Client disconnected during message transfer\n");
                    } else {
                        perror("recv failed");
                    }
                    break;
                }
                bytes_read += n;
                remaining -= n;
            }
            
            if (remaining > 0) {
                // We didn't receive the complete message
                break;
            }
            
            // Ensure null termination
            buffer[bytes_read] = '\0';
            
            // Add this:
            printf("Complete message: %s\n", buffer);
            
            // Print just first 100 chars with indicator
            printf("Message preview: %.100s%s\n", buffer, 
                   strlen(buffer) > 100 ? "..." : "");
            
            // Log received message
            printf("Received %d bytes\n", bytes_read);
            
            // After receiving data in buffer
            char *semicolon = strchr(buffer, ';');
            if (semicolon) {
                // Extract message type from prefix
                int prefix_len = semicolon - buffer;
                char message_type[32] = {0};
                if (prefix_len < sizeof(message_type)) {
                    strncpy(message_type, buffer, prefix_len);
                    message_type[prefix_len] = '\0';
                }
                printf("Message type: %s\n", message_type);
                
                // The JSON data starts after the semicolon
                char *json_data = semicolon + 1;
                printf("JSON data: %s\n", json_data);
                
                // Use the existing JSON parsing for additional fields
                // ...
            } else {
                // Fall back to current JSON parsing if no semicolon
                // Parse message type from JSON
                char message_type[32] = {0};
                char *command_start = strstr(buffer, "\"command\":");
                if (command_start) {
                    // Move past "command":
                    command_start += 10; // Length of "\"command\":"
                    
                    // Find the start of the actual command value (after the quote)
                    char *value_start = strchr(command_start, '"');
                    if (value_start) {
                        value_start++; // Move past opening quote
                        
                        // Find the end quote
                        char *value_end = strchr(value_start, '"');
                        if (value_end) {
                            int type_len = value_end - value_start;
                            if (type_len < sizeof(message_type)) {
                                strncpy(message_type, value_start, type_len);
                                message_type[type_len] = '\0';
                                printf("Message type: %s\n", message_type);
                            }
                        }
                    }
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
        
        // Close client socket when connection ends
        close(client_sock);
    }
    
    // Close sockets (never reached in this example)
    close(server_sock);
    close(broadcast_sock);
    return 0;
}