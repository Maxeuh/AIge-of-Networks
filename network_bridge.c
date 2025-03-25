#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#ifndef SO_REUSEPORT
#define SO_REUSEPORT SO_REUSEADDR
#endif

// Détection du système d'exploitation
#if defined(_WIN32) || defined(_WIN64)
#define IS_WINDOWS 1
#include <winsock2.h>
#include <ws2tcpip.h>
#include <windows.h>
#include <iphlpapi.h>
#pragma comment(lib, "ws2_32.lib")
#pragma comment(lib, "iphlpapi.lib")
typedef SOCKET socket_t;
typedef int socklen_t;
#define SOCKET_ERROR_VALUE INVALID_SOCKET
#define CLOSE_SOCKET(s) closesocket(s)
#else
#define IS_WINDOWS 0
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <ifaddrs.h>
#include <signal.h>
#include <sys/select.h>
typedef int socket_t;
#define SOCKET_ERROR_VALUE -1
#define CLOSE_SOCKET(s) close(s)
#endif

// Définition des ports
#define LOCAL_PORT 9090     // Port pour recevoir les données de Python
#define BROADCAST_PORT 9091 // Port pour le broadcast sur le réseau
#define PYTHON_PORT 9092    // Port pour renvoyer les données à Python

// Taille du tampon pour les messages
#define BUFFER_SIZE 65507

// Mode de débogage
int is_debug = 1;

// Mode d'exécution (activer ou désactiver la communication)
int is_run_mode = 0;

typedef struct
{
    socket_t local_socket;                   // Socket pour communiquer avec Python
    socket_t broadcast_socket;               // Socket pour diffuser les messages sur le réseau
    int running;                             // Indicateur pour l'arrêt du programme
    struct sockaddr_in broadcast_addr;       // Adresse de broadcast du réseau
    char machine_id[37];                     // UUID pour identifier cette machine
    char interface_name[256];                // Nom de l'interface réseau
    char ip_address[INET_ADDRSTRLEN];        // Adresse IP de l'interface réseau
    char broadcast_address[INET_ADDRSTRLEN]; // Adresse de broadcast de l'interface réseau
} NetworkState;

NetworkState state;

#if IS_WINDOWS
// Gestionnaire d'événements pour Windows
BOOL WINAPI CtrlHandler(DWORD fdwCtrlType);
#endif

// Fonction pour déterminer l'adresse broadcast du réseau
void get_broadcast_address(struct sockaddr_in *broadcast_addr)
{
// Implémentation Windows pour obtenir l'adresse de broadcast
#if IS_WINDOWS
    PIP_ADAPTER_INFO pAdapterInfo = NULL;
    PIP_ADAPTER_INFO pAdapter = NULL;
    DWORD dwRetVal = 0;
    ULONG ulOutBufLen = 0;

    // Obtenir la taille nécessaire du buffer
    GetAdaptersInfo(NULL, &ulOutBufLen);

    // Allouer la mémoire pour la structure de l'adaptateur
    pAdapterInfo = (IP_ADAPTER_INFO *)malloc(ulOutBufLen);

    // Obtenir les informations d'adaptateur
    dwRetVal = GetAdaptersInfo(pAdapterInfo, &ulOutBufLen);

    if (dwRetVal == NO_ERROR)
    {
        pAdapter = pAdapterInfo;
        while (pAdapter)
        {
            // Ignorer les adaptateurs sans adresse IP
            if (pAdapter->IpAddressList.IpAddress.String[0] != '0' &&
                strncmp(pAdapter->IpAddressList.IpAddress.String, "127.", 4) != 0)
            {
                struct in_addr ipaddr, netmask, broadcast;

                // Convertir IP et masque en valeurs binaires
                inet_pton(AF_INET, pAdapter->IpAddressList.IpAddress.String, &ipaddr);
                inet_pton(AF_INET, pAdapter->IpAddressList.IpMask.String, &netmask);

                // Calculer l'adresse de broadcast
                broadcast.s_addr = ipaddr.s_addr | ~(netmask.s_addr);

                // Configurer l'adresse de broadcast
                broadcast_addr->sin_family = AF_INET;
                broadcast_addr->sin_addr.s_addr = broadcast.s_addr;
                broadcast_addr->sin_port = htons(BROADCAST_PORT);

                // IMPORTANT : Stocker les informations dans NetworkState au lieu de les afficher
                strncpy(state.interface_name, pAdapter->Description, sizeof(state.interface_name) - 1);
                state.interface_name[sizeof(state.interface_name) - 1] = '\0';

                inet_ntop(AF_INET, &ipaddr, state.ip_address, sizeof(state.ip_address));
                inet_ntop(AF_INET, &broadcast_addr->sin_addr, state.broadcast_address, sizeof(state.broadcast_address));

                // Utiliser le premier adaptateur non-loopback
                break;
            }
            pAdapter = pAdapter->Next;
        }
    }

    if (pAdapterInfo)
    {
        free(pAdapterInfo);
    }
#else
    // Implémentation Unix (code existant)
    struct ifaddrs *ifap, *ifa;
    struct sockaddr_in *sa;
    struct sockaddr_in *netmask;

    getifaddrs(&ifap);
    for (ifa = ifap; ifa; ifa = ifa->ifa_next)
    {
        if (ifa->ifa_addr && ifa->ifa_addr->sa_family == AF_INET)
        {
            sa = (struct sockaddr_in *)ifa->ifa_addr;
            netmask = (struct sockaddr_in *)ifa->ifa_netmask;

            // Ignorer l'interface loopback (127.0.0.1)
            if ((sa->sin_addr.s_addr & 0xFF) == 127)
                continue;

            // Calculer l'adresse de broadcast
            broadcast_addr->sin_addr.s_addr = sa->sin_addr.s_addr | ~(netmask->sin_addr.s_addr);
            broadcast_addr->sin_family = AF_INET;
            broadcast_addr->sin_port = htons(BROADCAST_PORT);

            // IMPORTANT : Stocker les informations au lieu de les afficher
            strncpy(state.interface_name, ifa->ifa_name, sizeof(state.interface_name) - 1);
            state.interface_name[sizeof(state.interface_name) - 1] = '\0';

            strncpy(state.ip_address, inet_ntoa(sa->sin_addr), sizeof(state.ip_address) - 1);
            state.ip_address[sizeof(state.ip_address) - 1] = '\0';

            strncpy(state.broadcast_address, inet_ntoa(broadcast_addr->sin_addr), sizeof(state.broadcast_address) - 1);
            state.broadcast_address[sizeof(state.broadcast_address) - 1] = '\0';

            break;
        }
    }
    freeifaddrs(ifap);
#endif
}

#if !IS_WINDOWS
// Gestionnaire de signal pour arrêt propre (Unix uniquement)
void signal_handler(int signal)
{
    (void)signal;
    if (is_debug)
    {
        printf("\nSignal de terminaison reçu. Nettoyage...\n");
    }
    state.running = 0;
}
#endif

void generate_machine_id(char *id)
{
    // Créer un ID simple basé sur timestamp + nombre aléatoire
    srand((unsigned int)time(NULL));
    sprintf(id, "bridge-%lx-%x", (unsigned long)time(NULL), rand());
}

int main(int argc, char *argv[])
{
    // Vérifier les arguments de ligne de commande
    for (int i = 1; i < argc; ++i)
    {
        if (strcmp(argv[i], "--no-debug") == 0)
        {
            is_debug = 0;
        }
        else if (strcmp(argv[i], "--run") == 0)
        {
            is_run_mode = 1;
        }
    }

#if IS_WINDOWS
    // Initialisation de Winsock
    WSADATA wsaData;
    if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0)
    {
        fprintf(stderr, "Échec de l'initialisation de Winsock\n");
        return 1;
    }

    // Configurer l'encodage de la console sur UTF-8
    SetConsoleOutputCP(CP_UTF8);

    // Pour Windows, utilisez SetConsoleCtrlHandler pour gérer les signaux
    SetConsoleCtrlHandler((PHANDLER_ROUTINE)CtrlHandler, TRUE);
#else
    // Configurer l'encodage de la console sur UTF-8
    setenv("LC_ALL", "C.UTF-8", 1);

    // Configurer le gestionnaire de signal pour Unix
    signal(SIGINT, signal_handler);
    signal(SIGTERM, signal_handler);
#endif

    struct sockaddr_in local_addr, broadcast_receiver_addr, python_addr;
    int broadcast_enable = 1;

    // Initialiser l'état
    state.running = 1;

    // Créer le socket pour Python
    state.local_socket = socket(AF_INET, SOCK_DGRAM, 0);
    if (state.local_socket == SOCKET_ERROR_VALUE)
    {
        perror("Impossible de créer le socket local");
#if IS_WINDOWS
        WSACleanup();
#endif
        return 1;
    }

    // Activer SO_REUSEADDR pour le socket local
    int reuseaddr = 1;
    if (setsockopt(state.local_socket, SOL_SOCKET, SO_REUSEADDR,
                   (char *)&reuseaddr, sizeof(reuseaddr)) < 0)
    {
        perror("Impossible de configurer SO_REUSEADDR sur le socket local");
        CLOSE_SOCKET(state.local_socket);
#if IS_WINDOWS
        WSACleanup();
#endif
        return 1;
    }

    // Activer SO_REUSEPORT pour le socket local
    int reuseport = 1;
    if (setsockopt(state.local_socket, SOL_SOCKET, SO_REUSEPORT,
                   (char *)&reuseport, sizeof(reuseport)) < 0)
    {
        perror("Impossible de configurer SO_REUSEPORT sur le socket local");
        CLOSE_SOCKET(state.local_socket);
#if IS_WINDOWS
        WSACleanup();
#endif
        return 1;
    }

    // Configurer l'adresse locale
    memset(&local_addr, 0, sizeof(local_addr));
    local_addr.sin_family = AF_INET;
    local_addr.sin_addr.s_addr = inet_addr("127.0.0.1");
    local_addr.sin_port = htons(LOCAL_PORT);

    // Lier le socket local
    if (bind(state.local_socket, (struct sockaddr *)&local_addr, sizeof(local_addr)) < 0)
    {
        perror("Impossible de lier le socket local");
        CLOSE_SOCKET(state.local_socket);
#if IS_WINDOWS
        WSACleanup();
#endif
        return 1;
    }

    // Créer le socket pour le broadcast
    state.broadcast_socket = socket(AF_INET, SOCK_DGRAM, 0);
    if (state.broadcast_socket == SOCKET_ERROR_VALUE)
    {
        perror("Impossible de créer le socket broadcast");
        CLOSE_SOCKET(state.local_socket);
#if IS_WINDOWS
        WSACleanup();
#endif
        return 1;
    }

    // Activer SO_REUSEADDR pour le socket broadcast
    if (setsockopt(state.broadcast_socket, SOL_SOCKET, SO_REUSEADDR,
                   (char *)&reuseaddr, sizeof(reuseaddr)) < 0)
    {
        perror("Impossible de configurer SO_REUSEADDR sur le socket broadcast");
        CLOSE_SOCKET(state.local_socket);
        CLOSE_SOCKET(state.broadcast_socket);
#if IS_WINDOWS
        WSACleanup();
#endif
        return 1;
    }

    // Activer SO_REUSEPORT pour le socket broadcast
    if (setsockopt(state.broadcast_socket, SOL_SOCKET, SO_REUSEPORT,
                   (char *)&reuseport, sizeof(reuseport)) < 0)
    {
        perror("Impossible de configurer SO_REUSEPORT sur le socket broadcast");
        CLOSE_SOCKET(state.local_socket);
        CLOSE_SOCKET(state.broadcast_socket);
#if IS_WINDOWS
        WSACleanup();
#endif
        return 1;
    }

    // Activer l'option broadcast
    if (setsockopt(state.broadcast_socket, SOL_SOCKET, SO_BROADCAST,
                   (char *)&broadcast_enable, sizeof(broadcast_enable)) < 0)
    {
        perror("Impossible de configurer les options du socket");
        CLOSE_SOCKET(state.local_socket);
        CLOSE_SOCKET(state.broadcast_socket);
#if IS_WINDOWS
        WSACleanup();
#endif
        return 1;
    }

    // Configurer l'adresse pour recevoir les broadcasts
    memset(&broadcast_receiver_addr, 0, sizeof(broadcast_receiver_addr));
    broadcast_receiver_addr.sin_family = AF_INET;
    broadcast_receiver_addr.sin_addr.s_addr = INADDR_ANY;
    broadcast_receiver_addr.sin_port = htons(BROADCAST_PORT);

    // Lier le socket broadcast
    if (bind(state.broadcast_socket, (struct sockaddr *)&broadcast_receiver_addr,
             sizeof(broadcast_receiver_addr)) < 0)
    {
        perror("Impossible de lier le socket broadcast");
        CLOSE_SOCKET(state.local_socket);
        CLOSE_SOCKET(state.broadcast_socket);
#if IS_WINDOWS
        WSACleanup();
#endif
        return 1;
    }

    // Générer l'ID de la machine
    generate_machine_id(state.machine_id);

    // Obtenir l'adresse broadcast
    get_broadcast_address(&state.broadcast_addr);

    // Configurer l'adresse du jeu Python local
    memset(&python_addr, 0, sizeof(python_addr));
    python_addr.sin_family = AF_INET;
    python_addr.sin_addr.s_addr = inet_addr("127.0.0.1");
    python_addr.sin_port = htons(PYTHON_PORT);

    if (is_debug)
    {
        printf("┌────────────────────────────────┐\n");
        printf("│ AIge of Networks - Pont réseau │\n");
        printf("└────────────────────────────────┘\n");
        printf("\n");
        printf("Interface réseau : %s\n", state.interface_name);
        printf("Adresse IP : %s\n", state.ip_address);
        printf("\n");
        printf("Adresse de réception : %s:%d\n", inet_ntoa(local_addr.sin_addr), LOCAL_PORT);
        printf("Adresse de broadcast: %s:%d\n", state.broadcast_address, BROADCAST_PORT);
        printf("Adresse d'envoi : %s:%d\n", inet_ntoa(python_addr.sin_addr), PYTHON_PORT);
        printf("\n");
        printf("Machine ID : %s\n", state.machine_id);
        printf("Mode d'exécution : %s\n", is_run_mode ? "Exécution (envoi et réception de données)" : "Écoute uniquement");
        printf("\n----------------------------------\n\n");
    }

    fd_set read_fds;
    int max_fd = (state.local_socket > state.broadcast_socket) ? state.local_socket : state.broadcast_socket;

    while (state.running)
    {
        FD_ZERO(&read_fds);
        FD_SET(state.local_socket, &read_fds);
        FD_SET(state.broadcast_socket, &read_fds);

        int activity = select(max_fd + 1, &read_fds, NULL, NULL, NULL);

        if (activity < 0)
        {
            perror("select error");
            break;
        }

        if (FD_ISSET(state.local_socket, &read_fds))
        {
            char buffer[BUFFER_SIZE];
            struct sockaddr_in client_addr;
            socklen_t client_len = sizeof(client_addr);
            int received_bytes = recvfrom(state.local_socket, buffer, BUFFER_SIZE - 1, 0,
                                          (struct sockaddr *)&client_addr, &client_len);

            if (received_bytes > 0)
            {
                buffer[received_bytes] = '\0';

                // Ajouter l'ID de la machine au message
                char tagged_buffer[BUFFER_SIZE + 100];
                snprintf(tagged_buffer, sizeof(tagged_buffer), "{\"bridge_id\":\"%s\",\"data\":%s}",
                         state.machine_id, buffer);

                if (is_debug)
                {
                    printf("Reçu de Python : %s\n", buffer);
                }

                // Diffuser le message modifié sur le réseau seulement en mode run
                if (is_run_mode)
                {
                    // Diffuser le message modifié sur le réseau
                    sendto(state.broadcast_socket, tagged_buffer, strlen(tagged_buffer), 0,
                           (struct sockaddr *)&state.broadcast_addr, sizeof(state.broadcast_addr));

                    if (is_debug)
                    {
                        printf("Message diffusé sur le réseau\n");
                    }
                }
            }
        }

        if (FD_ISSET(state.broadcast_socket, &read_fds))
        {
            char buffer[BUFFER_SIZE];
            struct sockaddr_in sender_addr;
            socklen_t sender_len = sizeof(sender_addr);
            int received_bytes = recvfrom(state.broadcast_socket, buffer, BUFFER_SIZE - 1, 0,
                                          (struct sockaddr *)&sender_addr, &sender_len);
            if (received_bytes > 0)
            {
                buffer[received_bytes] = '\0';

                // Vérifier si le message contient notre ID (envoyé par nous-même)
                if (strstr(buffer, state.machine_id) == NULL)
                {
                    if (is_debug)
                    {
                        printf("Reçu du réseau (%s) : %s\n",
                               inet_ntoa(sender_addr.sin_addr), buffer);
                    }

                    // Extraire les données du message pour Python (enlever notre wrapper)
                    char *data_start = strstr(buffer, "\"data\":");
                    if (data_start)
                    {
                        data_start += 7; // Dépasser "data":

                        // Retirer le "}" fermant si présent
                        char *closing_brace = strrchr(data_start, '}');
                        if (closing_brace)
                        {
                            *closing_brace = '\0';
                        }

                        // Transmettre seulement les données au jeu Python en mode run
                        if (is_run_mode)
                        {
                            sendto(state.local_socket, data_start, strlen(data_start), 0,
                                   (struct sockaddr *)&python_addr, sizeof(python_addr));

                            if (is_debug)
                            {
                                printf("Message transmis à Python\n");
                            }
                        }
                    }
                }
                else if (is_debug && is_run_mode)
                {
                    printf("Message ignoré (envoyé par nous-même)\n");
                }
            }
        }
    }

    // Nettoyer les ressources
    CLOSE_SOCKET(state.local_socket);
    CLOSE_SOCKET(state.broadcast_socket);

#if IS_WINDOWS
    WSACleanup();
#endif

    if (is_debug)
    {
        printf("Pont réseau arrêté.\n");
    }
    return 0;
}

#if IS_WINDOWS
// Gestionnaire d'événements pour Windows
BOOL WINAPI CtrlHandler(DWORD fdwCtrlType)
{
    switch (fdwCtrlType)
    {
    case CTRL_C_EVENT:
    case CTRL_CLOSE_EVENT:
    case CTRL_BREAK_EVENT:
    case CTRL_LOGOFF_EVENT:
    case CTRL_SHUTDOWN_EVENT:
        if (is_debug)
        {
            printf("\nSignal de terminaison reçu. Nettoyage...\n");
        }
        state.running = 0;

        // Forcer le réveil de select() en fermant les sockets
        if (state.local_socket != SOCKET_ERROR_VALUE)
        {
            CLOSE_SOCKET(state.local_socket);
            state.local_socket = SOCKET_ERROR_VALUE;
        }

        if (state.broadcast_socket != SOCKET_ERROR_VALUE)
        {
            CLOSE_SOCKET(state.broadcast_socket);
            state.broadcast_socket = SOCKET_ERROR_VALUE;
        }

        // Indiquer que nous avons géré l'événement
        return TRUE;
    default:
        return FALSE;
    }
}
#endif