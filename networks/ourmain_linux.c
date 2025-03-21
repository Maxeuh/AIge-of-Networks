#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <pthread.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>


#define PORT 23456
#define BROADCAST_IP "192.168.79.255"
#define IPC_PORT 12347
#define MAX_CLIENTS 10
#define UPDATE_INTERVAL 5000000 // 5 seconds in microseconds

// Structure to track connected clients
struct ClientInfo {
    struct sockaddr_in address;
    int active;
};

// Thread data structure
struct thread_data {
    int socket_fd;
    // Add other needed fields
};

// Game data structure
struct GameData {
    char message[256];
};

// Global variables
struct ClientInfo client_info[MAX_CLIENTS];
int sockfd; // Main UDP socket

// Add this function definition before the receive_messages function
void send_message_to_python_client(const char *message) {
    int ipc_client_socket;
    struct sockaddr_in python_addr;
    
    // Create a TCP socket to connect to Python client
    ipc_client_socket = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (ipc_client_socket < 0) {
        printf("IPC client socket creation failed: %d\n", errno);
        return;
    }
    
    // Set up address for Python client (listening on IPC_PORT+1)
    memset(&python_addr, 0, sizeof(python_addr));
    python_addr.sin_family = AF_INET;
    python_addr.sin_port = htons(IPC_PORT+1);
    python_addr.sin_addr.s_addr = inet_addr("127.0.0.1");
    
    // Try to connect to Python client
    if (connect(ipc_client_socket, (struct sockaddr*)&python_addr, sizeof(python_addr)) < 0) {
        // Python client might not be ready yet
        printf("Could not connect to Python client: %d\n", errno);
        close(ipc_client_socket);
        return;
    }
    
    // Send the message to Python client
    if (send(ipc_client_socket, message, strlen(message), 0) < 0) {
        printf("Failed to send message to Python client: %d\n", errno);
    } else {
        printf("Message forwarded to Python client: %s\n", message);
        
        // Receive acknowledgment (optional)
        char ack[256];
        int bytes = recv(ipc_client_socket, ack, sizeof(ack)-1, 0);
        if (bytes > 0) {
            ack[bytes] = '\0';
            printf("Python client acknowledgment: %s\n", ack);
        }
    }
    
    // Close the socket
    close(ipc_client_socket);
}

// Function to broadcast message to all clients
void broadcast_message(const char *message) {
    struct sockaddr_in broadcast_addr;
    memset(&broadcast_addr, 0, sizeof(broadcast_addr));
    broadcast_addr.sin_family = AF_INET;
    broadcast_addr.sin_port = htons(PORT);
    broadcast_addr.sin_addr.s_addr = inet_addr(BROADCAST_IP);
    
    // Send the broadcast
    if (sendto(sockfd, message, strlen(message), 0, 
              (struct sockaddr*)&broadcast_addr, sizeof(broadcast_addr)) < 0) {
        printf("Failed to broadcast message: %d\n", errno);
    } else {
        printf("Broadcast message sent: %s\n", message);
    }
}

// Function to receive messages from UDP
void *receive_messages(void *arg)
{
    int *serverSocket = (int *)arg; // Use the socket passed from main
    char buffer[1024];
    socklen_t recvfromlen;
    struct sockaddr_in clientAddr;
    recvfromlen = sizeof(clientAddr);

    printf("Receiving thread started on port %d\n", PORT);
    while (1)
    {
        // Receive data from client
        int recvBytes = recvfrom(*serverSocket, buffer, sizeof(buffer), 0,
                              (struct sockaddr *)&clientAddr, &recvfromlen);
        if (recvBytes < 0)
        {
            printf("recvfrom failed with error: %d\n", errno);
            continue; // Don't close the socket, just continue
        }
        
        buffer[recvBytes] = '\0'; // Null-terminate the received data
        printf("Received message from client: %s\n", buffer);

        // Forward received broadcast back to Python client
        send_message_to_python_client(buffer);
    }

    return NULL;
}

// Function to send broadcast messages
void *send_messages(void *arg)
{
    int clientSocket;
    struct sockaddr_in serverAddr;
    char message[1024];
    int broadcast = 1; // Enable broadcast

    // Create a UDP socket
    clientSocket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    if (clientSocket < 0)
    {
        printf("socket creation failed with error: %d\n", errno);
        return NULL;
    }

    // Set the socket to allow broadcasts
    if (setsockopt(clientSocket, SOL_SOCKET, SO_BROADCAST, &broadcast, sizeof(broadcast)) < 0)
    {
        printf("setsockopt failed with error: %d\n", errno);
        close(clientSocket);
        return NULL;
    }

    memset(&serverAddr, 0, sizeof(serverAddr));
    serverAddr.sin_family = AF_INET;
    serverAddr.sin_addr.s_addr = inet_addr(BROADCAST_IP);
    serverAddr.sin_port = htons(PORT);

    while (1)
    {
        printf("Enter a message to broadcast: ");
        fgets(message, sizeof(message), stdin);

        // Send message to broadcast IP
        int sentBytes = sendto(clientSocket, message, strlen(message), 0,
                             (struct sockaddr *)&serverAddr, sizeof(serverAddr));
        if (sentBytes < 0)
        {
            printf("sendto failed with error: %d\n", errno);
            close(clientSocket);
            return NULL;
        }

        printf("Message broadcast to %s:%d\n", BROADCAST_IP, PORT);
    }
}

// Function to send game data to all connected clients
void send_to_all_clients(int sockfd, struct GameData *gameData, struct sockaddr_in *exclude_addr) {
    for (int i = 0; i < MAX_CLIENTS; i++) {
        if (client_info[i].active && 
           (exclude_addr == NULL || 
            memcmp(&client_info[i].address, exclude_addr, sizeof(struct sockaddr_in)) != 0)) {
            
            sendto(sockfd, (char *)gameData, sizeof(struct GameData), 0,
                   (struct sockaddr *)&client_info[i].address, sizeof(client_info[i].address));
            printf("Sending game message to client %d: %s\n", i, gameData->message);
        }
    }
}

// Function to handle incoming game data
void *handle_incoming_data(void *arg) {
    int sockfd = *((int *)arg);
    struct sockaddr_in client_addr;
    socklen_t client_addr_len = sizeof(client_addr);
    struct GameData received_data;

    while (1) {
        int recv_len = recvfrom(sockfd, (char *)&received_data, sizeof(struct GameData), 0, 
                   (struct sockaddr *)&client_addr, &client_addr_len);
                   
        if (recv_len > 0) {
            printf("Received game message from client: %s\n", received_data.message);
            
            // Echo the received message back to all clients except the sender
            send_to_all_clients(sockfd, &received_data, &client_addr);
        }
    }
    
    return NULL;
}

// Function to periodically send game state updates
void *send_game_state_periodically(void *arg) {
    int sockfd = *((int *)arg);
    struct GameData gameData;
    
    while (1) {
        strcpy(gameData.message, "Update message for all clients.");
        send_to_all_clients(sockfd, &gameData, NULL);
        usleep(UPDATE_INTERVAL);
    }
    
    return NULL;
}

// Function to handle IPC commands from Python
void *listen_for_ipc_commands(void *arg) {
    int ipc_sockfd = *((int *)arg);
    int client_sock;
    struct sockaddr_in client_addr;
    socklen_t client_addr_len = sizeof(client_addr);
    char buffer[1024];
    int bytes_read;

    while (1) {
        client_sock = accept(ipc_sockfd, (struct sockaddr *)&client_addr, &client_addr_len);
        if (client_sock < 0) {
            printf("Accept failed with error code: %d\n", errno);
            continue;
        }

        // Read data from the client
        while ((bytes_read = recv(client_sock, buffer, sizeof(buffer) - 1, 0)) > 0) {
            buffer[bytes_read] = '\0'; // Null-terminate the string
            printf("Received IPC command: %s\n", buffer);
            
            // Forward the received command via broadcast
            broadcast_message(buffer);
            
            // Send response to client
            const char *response = "Commande reçue avec succès";
            send(client_sock, response, strlen(response), 0);
        }

        close(client_sock);
    }
    
    return NULL;
}

int main()
{
    // Initialize client_info array
    for (int i = 0; i < MAX_CLIENTS; i++) {
        client_info[i].active = 0;
    }

    // Create main UDP socket for game communication
    sockfd = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    if (sockfd < 0) {
        printf("Socket creation failed with error code: %d\n", errno);
        return EXIT_FAILURE;
    }

    // Set socket to broadcast mode
    int broadcast = 1;
    if (setsockopt(sockfd, SOL_SOCKET, SO_BROADCAST, &broadcast, sizeof(broadcast)) < 0) {
        printf("Setsockopt failed with error code: %d\n", errno);
        close(sockfd);
        return EXIT_FAILURE;
    }

    // Create socket for IPC with Python
    int ipc_sockfd = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (ipc_sockfd < 0) {
        printf("IPC Socket creation failed with error code: %d\n", errno);
        close(sockfd);
        return EXIT_FAILURE;
    }

    // Configure IPC socket
    struct sockaddr_in ipc_addr;
    memset(&ipc_addr, 0, sizeof(ipc_addr));
    ipc_addr.sin_family = AF_INET;
    ipc_addr.sin_addr.s_addr = htonl(INADDR_ANY);
    ipc_addr.sin_port = htons(IPC_PORT);

    // Enable address reuse for IPC socket
    int reuse = 1;
    if (setsockopt(ipc_sockfd, SOL_SOCKET, SO_REUSEADDR, &reuse, sizeof(reuse)) < 0) {
        printf("Setsockopt failed with error code: %d\n", errno);
        close(ipc_sockfd);
        close(sockfd);
        return EXIT_FAILURE;
    }

    // Bind IPC socket
    if (bind(ipc_sockfd, (struct sockaddr *)&ipc_addr, sizeof(ipc_addr)) < 0) {
        printf("IPC Socket bind failed with error code: %d\n", errno);
        close(ipc_sockfd);
        close(sockfd);
        return EXIT_FAILURE;
    }

    // Listen for connections on IPC socket
    if (listen(ipc_sockfd, 1) < 0) {
        printf("IPC Socket listen failed with error code: %d\n", errno);
        close(ipc_sockfd);
        close(sockfd);
        return EXIT_FAILURE;
    }

    // Bind main UDP socket
    struct sockaddr_in server_addr;
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = htonl(INADDR_ANY);
    server_addr.sin_port = htons(PORT);

    if (bind(sockfd, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
        printf("Bind failed with error code: %d\n", errno);
        close(ipc_sockfd);
        close(sockfd);
        return EXIT_FAILURE;
    }

    // Create threads
    pthread_t receive_thread_id, send_thread_id, listen_thread_id, update_thread_id, ipc_thread_id;
    
    // Start thread for receiving messages
    if (pthread_create(&receive_thread_id, NULL, receive_messages, &sockfd) != 0) {
        printf("Error creating receive thread\n");
        close(ipc_sockfd);
        close(sockfd);
        return EXIT_FAILURE;
    }
    
    // Start thread for sending messages
    if (pthread_create(&send_thread_id, NULL, send_messages, NULL) != 0) {
        printf("Error creating send thread\n");
        close(ipc_sockfd);
        close(sockfd);
        return EXIT_FAILURE;
    }
    
    // Start thread for handling incoming game data
    if (pthread_create(&listen_thread_id, NULL, handle_incoming_data, &sockfd) != 0) {
        printf("Error creating game data thread\n");
        close(ipc_sockfd);
        close(sockfd);
        return EXIT_FAILURE;
    }
    
    // Start thread for periodic game state updates
    if (pthread_create(&update_thread_id, NULL, send_game_state_periodically, &sockfd) != 0) {
        printf("Error creating update thread\n");
        close(ipc_sockfd);
        close(sockfd);
        return EXIT_FAILURE;
    }
    
    // Start thread for IPC communication with Python
    if (pthread_create(&ipc_thread_id, NULL, listen_for_ipc_commands, &ipc_sockfd) != 0) {
        printf("Error creating IPC thread\n");
        close(ipc_sockfd);
        close(sockfd);
        return EXIT_FAILURE;
    }
    
    printf("All threads started successfully\n");
    
    // Main thread sleep loop to keep program running
    while (1) {
        sleep(5);
    }

    // This code will never be reached due to the infinite loop above
    pthread_join(receive_thread_id, NULL);
    pthread_join(send_thread_id, NULL);
    pthread_join(listen_thread_id, NULL);
    pthread_join(update_thread_id, NULL);
    pthread_join(ipc_thread_id, NULL);
    
    close(ipc_sockfd);
    close(sockfd);
    
    return 0;
}