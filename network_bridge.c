#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

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
#include <pthread.h>
typedef int socket_t;
#define SOCKET_ERROR_VALUE -1
#define CLOSE_SOCKET(s) close(s)
#endif

#define LOCAL_PORT 9090
#define BROADCAST_PORT 9091
#define BUFFER_SIZE 1024
// Pour afficher les messages de débogage, définir DEBUG_MODE à 1. Sinon, définir à 0.
#ifndef DEBUG_MODE
#define DEBUG_MODE 1
#endif

// Structures et types pour les threads (cross-platform)
#if IS_WINDOWS
typedef HANDLE thread_t;
typedef DWORD WINAPI thread_func_t(LPVOID);
#define THREAD_CREATE(thread, func, arg) \
    ((*thread = CreateThread(NULL, 0, func, arg, 0, NULL)) == NULL)
#define THREAD_JOIN(thread)                \
    WaitForSingleObject(thread, INFINITE); \
    CloseHandle(thread)
#define THREAD_RETURN DWORD
BOOL WINAPI CtrlHandler(DWORD fdwCtrlType);
#else
typedef pthread_t thread_t;
typedef void *(*thread_func_t)(void *);
#define THREAD_CREATE(thread, func, arg) pthread_create(thread, NULL, func, arg)
#define THREAD_JOIN(thread) pthread_join(thread, NULL)
#define THREAD_RETURN void *
#endif

typedef struct
{
    socket_t local_socket;
    socket_t broadcast_socket;
    int running;
    struct sockaddr_in broadcast_addr;
    char machine_id[37]; // UUID pour identifier cette machine
} NetworkState;

NetworkState state;

// Fonction pour déterminer l'adresse broadcast du réseau
void get_broadcast_address(struct sockaddr_in *broadcast_addr)
{
#if IS_WINDOWS
    // Implémentation Windows pour obtenir l'adresse de broadcast
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
            if (pAdapter->IpAddressList.IpAddress.String[0] != '0')
            {
                // Vérifier que ce n'est pas l'adresse loopback (127.0.0.1)
                if (strncmp(pAdapter->IpAddressList.IpAddress.String, "127.", 4) != 0)
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

                    if (DEBUG_MODE)
                    {
                        char ip_str[INET_ADDRSTRLEN];
                        char broadcast_str[INET_ADDRSTRLEN];

                        inet_ntop(AF_INET, &ipaddr, ip_str, INET_ADDRSTRLEN);
                        inet_ntop(AF_INET, &broadcast.s_addr, broadcast_str, INET_ADDRSTRLEN);

                        printf("**********************************\n");
                        printf("* AIge of Networks - Pont réseau *\n");
                        printf("**********************************\n");
                        printf("----------------------------------\n");
                        printf("Interface réseau: %s\n", pAdapter->Description);
                        printf("Adresse IP: %s\n", ip_str);
                        printf("Adresse de broadcast: %s\n", broadcast_str);
                        printf("----------------------------------\n");
                        printf("Machine ID: %s\n", state.machine_id);
                        printf("----------------------------------\n");
                    }

                    // Utiliser le premier adaptateur non-loopback
                    break;
                }
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

            if (DEBUG_MODE)
            {
                printf("Interface réseau: %s\n", ifa->ifa_name);
                printf("Adresse IP: %s\n", inet_ntoa(sa->sin_addr));
                printf("Adresse de broadcast: %s\n", inet_ntoa(broadcast_addr->sin_addr));
            }

            // Prendre la première interface non-loopback
            break;
        }
    }
    freeifaddrs(ifap);
#endif
}

// Thread pour écouter les messages venant de Python
THREAD_RETURN listen_from_python(void *arg)
{
    (void)arg;
    char buffer[BUFFER_SIZE];
    struct sockaddr_in client_addr;
    socklen_t client_len = sizeof(client_addr);
    int received_bytes;

    if (DEBUG_MODE)
    {
        printf("Écoute des messages de Python sur %s:%d\n", inet_ntoa(client_addr.sin_addr), LOCAL_PORT);
    }

    while (state.running)
    {
        received_bytes = recvfrom(state.local_socket, buffer, BUFFER_SIZE - 1, 0,
                                  (struct sockaddr *)&client_addr, &client_len);
        if (received_bytes > 0)
        {
            buffer[received_bytes] = '\0';

            // Ajouter l'ID de la machine au message
            char tagged_buffer[BUFFER_SIZE + 50];
            snprintf(tagged_buffer, sizeof(tagged_buffer), "{\"bridge_id\":\"%s\",\"data\":%s}",
                     state.machine_id, buffer);

            if (DEBUG_MODE)
            {
                printf("Reçu de Python: %s\n", buffer);
            }

            // Diffuser le message modifié sur le réseau
            sendto(state.broadcast_socket, tagged_buffer, strlen(tagged_buffer), 0,
                   (struct sockaddr *)&state.broadcast_addr, sizeof(state.broadcast_addr));

            if (DEBUG_MODE)
            {
                printf("Message diffusé sur le réseau\n");
            }
        }
#if IS_WINDOWS
        // Petite pause pour éviter de consommer trop de CPU sur Windows
        Sleep(10);
#else
        // Petite pause pour éviter de consommer trop de CPU sur Unix
        usleep(10000);
#endif
    }
#if IS_WINDOWS
    return 0;
#else
    return NULL;
#endif
}

// Thread pour écouter les messages du réseau
THREAD_RETURN listen_from_network(void *arg)
{
    (void)arg;
    char buffer[BUFFER_SIZE];
    struct sockaddr_in sender_addr;
    socklen_t sender_len = sizeof(sender_addr);
    int received_bytes;
    struct sockaddr_in python_addr;

    // Configurer l'adresse du jeu Python local
    memset(&python_addr, 0, sizeof(python_addr));
    python_addr.sin_family = AF_INET;
    python_addr.sin_addr.s_addr = inet_addr("127.0.0.1");
    python_addr.sin_port = htons(LOCAL_PORT);

    if (DEBUG_MODE)
    {
        printf("Écoute des messages broadcast sur %s:%d\n", inet_ntoa(state.broadcast_addr.sin_addr), BROADCAST_PORT);
    }

    while (state.running)
    {
        received_bytes = recvfrom(state.broadcast_socket, buffer, BUFFER_SIZE - 1, 0,
                                  (struct sockaddr *)&sender_addr, &sender_len);
        if (received_bytes > 0)
        {
            buffer[received_bytes] = '\0';

            // Vérifier si le message contient notre ID (envoyé par nous-même)
            if (strstr(buffer, state.machine_id) == NULL)
            {
                if (DEBUG_MODE)
                {
                    printf("Reçu du réseau (%s): %s\n",
                           inet_ntoa(sender_addr.sin_addr), buffer);
                }

                // Extraire les données du message pour Python (enlever notre wrapper)
                char *data_start = strstr(buffer, "\"data\":");
                if (data_start)
                {
                    data_start += 7; // Dépasser "data":

                    // Transmettre seulement les données au jeu Python
                    sendto(state.local_socket, data_start, strlen(data_start), 0,
                           (struct sockaddr *)&python_addr, sizeof(python_addr));

                    if (DEBUG_MODE)
                    {
                        printf("Message transmis à Python\n");
                    }
                }
            }
            else if (DEBUG_MODE)
            {
                printf("Message ignoré (envoyé par nous-même)\n");
            }
        }
#if IS_WINDOWS
        // Petite pause pour éviter de consommer trop de CPU sur Windows
        Sleep(10);
#else
        // Petite pause pour éviter de consommer trop de CPU sur Unix
        usleep(10000);
#endif
    }
#if IS_WINDOWS
    return 0;
#else
    return NULL;
#endif
}

#if !IS_WINDOWS
// Gestionnaire de signal pour arrêt propre (Unix uniquement)
void signal_handler(int signal)
{
    if (DEBUG_MODE)
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
#undef DEBUG_MODE
#define DEBUG_MODE 0
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

    thread_t python_thread, network_thread;
    struct sockaddr_in local_addr, broadcast_receiver_addr;
    int broadcast_enable = 1;

    // Initialiser l'état
    state.running = 1;

    // Créer le socket pour Python
    state.local_socket = socket(AF_INET, SOCK_DGRAM, 0);
    if (state.local_socket == SOCKET_ERROR_VALUE)
    {
#if IS_WINDOWS
        fprintf(stderr, "Impossible de créer le socket local (Erreur: %d)\n", WSAGetLastError());
        WSACleanup();
#else
        perror("Impossible de créer le socket local");
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
#if IS_WINDOWS
        fprintf(stderr, "Impossible de lier le socket local (Erreur: %d)\n", WSAGetLastError());
        CLOSE_SOCKET(state.local_socket);
        WSACleanup();
#else
        perror("Impossible de lier le socket local");
        CLOSE_SOCKET(state.local_socket);
#endif
        return 1;
    }

    // Créer le socket pour le broadcast
    state.broadcast_socket = socket(AF_INET, SOCK_DGRAM, 0);
    if (state.broadcast_socket == SOCKET_ERROR_VALUE)
    {
#if IS_WINDOWS
        fprintf(stderr, "Impossible de créer le socket broadcast (Erreur: %d)\n", WSAGetLastError());
        CLOSE_SOCKET(state.local_socket);
        WSACleanup();
#else
        perror("Impossible de créer le socket broadcast");
        CLOSE_SOCKET(state.local_socket);
#endif
        return 1;
    }

    // Activer l'option broadcast
    if (setsockopt(state.broadcast_socket, SOL_SOCKET, SO_BROADCAST,
                   (char *)&broadcast_enable, sizeof(broadcast_enable)) < 0)
    {
#if IS_WINDOWS
        fprintf(stderr, "Impossible de configurer les options du socket (Erreur: %d)\n", WSAGetLastError());
        CLOSE_SOCKET(state.local_socket);
        CLOSE_SOCKET(state.broadcast_socket);
        WSACleanup();
#else
        perror("Impossible de configurer les options du socket");
        CLOSE_SOCKET(state.local_socket);
        CLOSE_SOCKET(state.broadcast_socket);
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
#if IS_WINDOWS
        fprintf(stderr, "Impossible de lier le socket broadcast (Erreur: %d)\n", WSAGetLastError());
        CLOSE_SOCKET(state.local_socket);
        CLOSE_SOCKET(state.broadcast_socket);
        WSACleanup();
#else
        perror("Impossible de lier le socket broadcast");
        CLOSE_SOCKET(state.local_socket);
        CLOSE_SOCKET(state.broadcast_socket);
#endif
        return 1;
    }

    // Générer l'ID de la machine
    generate_machine_id(state.machine_id);

    // Obtenir l'adresse broadcast
    get_broadcast_address(&state.broadcast_addr);

    if (DEBUG_MODE)
    {
        printf("**********************************\n");
        printf("* AIge of Networks - Pont réseau *\n");
        printf("**********************************\n");
        printf("----------------------------------\n");
        printf("Interface réseau: %s\n", inet_ntoa(state.broadcast_addr.sin_addr));
        printf("Adresse de broadcast: %s\n", inet_ntoa(state.broadcast_addr.sin_addr));
        printf("----------------------------------\n");
        printf("Machine ID: %s\n", state.machine_id);
        printf("----------------------------------\n");
    }

    // Démarrer les threads d'écoute
    if (THREAD_CREATE(&python_thread, listen_from_python, NULL) != 0)
    {
#if IS_WINDOWS
        fprintf(stderr, "Impossible de créer le thread d'écoute Python (Erreur: %lu)\n", GetLastError());
        CLOSE_SOCKET(state.local_socket);
        CLOSE_SOCKET(state.broadcast_socket);
        WSACleanup();
#else
        perror("Impossible de créer le thread d'écoute Python");
        CLOSE_SOCKET(state.local_socket);
        CLOSE_SOCKET(state.broadcast_socket);
#endif
        return 1;
    }

    if (THREAD_CREATE(&network_thread, listen_from_network, NULL) != 0)
    {
#if IS_WINDOWS
        fprintf(stderr, "Impossible de créer le thread d'écoute réseau (Erreur: %lu)\n", GetLastError());
        state.running = 0;
        THREAD_JOIN(python_thread);
        CLOSE_SOCKET(state.local_socket);
        CLOSE_SOCKET(state.broadcast_socket);
        WSACleanup();
#else
        perror("Impossible de créer le thread d'écoute réseau");
        state.running = 0;
        THREAD_JOIN(python_thread);
        CLOSE_SOCKET(state.local_socket);
        CLOSE_SOCKET(state.broadcast_socket);
#endif
        return 1;
    }

    if (DEBUG_MODE)
    {
        printf("Pont réseau en fonctionnement. Appuyez sur Ctrl+C pour arrêter.\n");
    }

    // Attendre que les threads se terminent
    THREAD_JOIN(python_thread);
    THREAD_JOIN(network_thread);

    // Nettoyer les ressources
    CLOSE_SOCKET(state.local_socket);
    CLOSE_SOCKET(state.broadcast_socket);

#if IS_WINDOWS
    WSACleanup();
#endif

    if (DEBUG_MODE)
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
        if (DEBUG_MODE)
        {
            printf("\nSignal de terminaison reçu. Nettoyage...\n");
        }
        state.running = 0;
        return TRUE;
    default:
        return FALSE;
    }
}
#endif