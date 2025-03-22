#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <signal.h>
#include <zlib.h>  // You'll need to install zlib development files

#define SERVER_IP "127.0.0.1"
#define PORT 12345
#define BUFFER_SIZE 81920
#define DECOMP_BUFFER_SIZE 1048576  // 1MB decompression buffer

int running = 1;

void handle_sigint(int sig) {
    printf("Shutting down client...\n");
    running = 0;
}

// Simple function to display raw data
void print_raw_data(const char* data, int length) {
    printf("Received %d bytes of data\n", length);
    printf("First 100 characters: ");
    
    int display_len = length < 100 ? length : 100;
    for (int i = 0; i < display_len; i++) {
        putchar(data[i]);
    }
    printf("\n");
}

// Function to decompress zlib data
int decompress_data(const unsigned char* compressed, int comp_length, 
                   unsigned char* decompressed, int max_length) {
    z_stream strm;
    strm.zalloc = Z_NULL;
    strm.zfree = Z_NULL;
    strm.opaque = Z_NULL;
    strm.avail_in = comp_length;
    strm.next_in = (Bytef*)compressed;
    strm.avail_out = max_length;
    strm.next_out = decompressed;
    
    inflateInit(&strm);
    inflate(&strm, Z_FINISH);
    inflateEnd(&strm);
    
    return max_length - strm.avail_out;
}

int main() {
    int sock;
    struct sockaddr_in server_addr;
    char buffer[BUFFER_SIZE];
    unsigned char decomp_buffer[DECOMP_BUFFER_SIZE];
    socklen_t addr_len;
    
    // Set up signal handler
    signal(SIGINT, handle_sigint);
    
    // Create socket
    if ((sock = socket(AF_INET, SOCK_DGRAM, 0)) < 0) {
        perror("Socket creation failed");
        exit(EXIT_FAILURE);
    }
    
    // Configure server address for game data
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(PORT);
    inet_pton(AF_INET, SERVER_IP, &server_addr.sin_addr);
    
    // Bind socket to receive data on the port
    if (bind(sock, (struct sockaddr*)&server_addr, sizeof(server_addr)) < 0) {
        perror("Bind failed");
        close(sock);
        exit(EXIT_FAILURE);
    }
    
    printf("Client listening on %s:%d\n", SERVER_IP, PORT);
    printf("Waiting for game data...\n");
    printf("Press Ctrl+C to exit\n");
    
    // Main reception loop
    while (running) {
        addr_len = sizeof(server_addr);
        int n = recvfrom(sock, buffer, BUFFER_SIZE, 0, 
                        (struct sockaddr*)&server_addr, &addr_len);
        
        if (n > 0) {
            buffer[n] = '\0';
            printf("\n--- New game data received (%d bytes) ---\n", n);
            
            // Check if data is compressed
            if (n > 11 && strncmp(buffer, "COMPRESSED:", 11) == 0) {
                printf("Received compressed data, decompressing...\n");
                int decomp_length = decompress_data((unsigned char*)buffer + 11, 
                                                   n - 11, decomp_buffer, 
                                                   DECOMP_BUFFER_SIZE);
                decomp_buffer[decomp_length] = '\0';
                printf("Decompressed %d bytes to %d bytes\n", n - 11, decomp_length);
                print_raw_data((char*)decomp_buffer, decomp_length);
            } else {
                // Regular uncompressed data
                print_raw_data(buffer, n);
            }
        }
        
        usleep(100000);  // 100ms sleep
    }
    
    close(sock);
    return 0;
}