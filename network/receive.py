import socket

# Configuration du serveur UDP
UDP_IP = "127.0.0.1"  # Adresse locale
UDP_PORT = 8080       # Même port que le programme C
BUFFER_SIZE = 1024    # Même taille de buffer que C

# Création du socket UDP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((UDP_IP, UDP_PORT))

# Configuration du socket en mode non-bloquant
server_socket.setblocking(False)

print(f"Python en attente de messages sur le port {UDP_PORT} (mode non-bloquant)...")

while True:
    try:
        # Réception des données en mode non-bloquant
        data, addr = server_socket.recvfrom(BUFFER_SIZE)
        if data:
            print(f"Message reçu de {addr}: {data.decode()}")
    except BlockingIOError:
        # Aucune donnée disponible, on continue
        continue
    except Exception as e:
        print(f"Erreur: {e}")
        continue