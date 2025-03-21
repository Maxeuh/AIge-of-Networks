import socket
import threading

# Fonction pour écouter les messages UDP
def udp_listener(host, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
            # Don't bind the socket, just use it to send
            # udp_socket.bind((host, port))  # Comment out or remove this line
            print(f"UDP Listener ready to receive", flush=True)
            
            while True:
                try:
                    data, addr = udp_socket.recvfrom(1024)  # Recevoir des messages UDP
                    if data:
                        print(f"Message reçu via UDP de {addr}: {data.decode()}", flush=True)
                except socket.error as e:
                    print("Erreur lors de la réception UDP :", e, flush=True)
                    break  # Sortir de la boucle si une erreur survient

    except Exception as e:
        print("Erreur lors de l'écoute UDP :", e, flush=True)

# Fonction pour écouter les messages TCP
def tcp_listener(sock):
    try:
        while True:
            data = sock.recv(1024)
            if data:
                print("Message reçu via TCP:", data.decode(), flush=True)
            else:
                break  # Sortir de la boucle si la connexion est fermée
    except socket.error as e:
        print("Erreur lors de la réception TCP :", e, flush=True)

def main():
    tcp_host = '127.0.0.1'
    tcp_port = 12347  # Port TCP/IPC
    tcp_receive_port = 12348  # Port to receive from C program
    udp_port = 23456  # Port UDP

    # Setup TCP server to receive messages from C program
    tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        tcp_server.bind((tcp_host, tcp_receive_port))
        tcp_server.listen(5)
        print(f"TCP server listening on port {tcp_receive_port}", flush=True)
        
        # Start TCP server listener thread
        tcp_server_thread = threading.Thread(target=tcp_server_listener, args=(tcp_server,))
        tcp_server_thread.daemon = True
        tcp_server_thread.start()
    except Exception as e:
        print(f"Failed to start TCP server: {e}", flush=True)

    # Démarrer le thread d'écoute UDP
    udp_thread = threading.Thread(target=udp_listener, args=(tcp_host, udp_port))
    udp_thread.daemon = True  # Permet de fermer le thread quand le programme principal se termine
    udp_thread.start()

    # Connexion TCP/IPC
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((tcp_host, tcp_port))
            print("Connecté au serveur IPC.", flush=True)

            # Démarrer le thread d'écoute TCP
            tcp_thread = threading.Thread(target=tcp_listener, args=(s,))
            tcp_thread.daemon = True  # Permet de fermer le thread quand le programme principal se termine
            tcp_thread.start()

            while True:
                message = input("Entrez une commande à envoyer (ou 'quit' pour quitter) : ")
                if message.lower() == 'quit':
                    break

                try:
                    s.sendall(message.encode())  # Envoyer le message
                except socket.error as e:
                    print("Erreur lors de l'envoi TCP :", e, flush=True)
                    break  # Quitter la boucle en cas d'erreur

    except Exception as e:
        print("Une erreur est survenue :", e, flush=True)

# Add this new function to handle incoming connections on the TCP server
def tcp_server_listener(server_socket):
    try:
        while True:
            client_socket, client_address = server_socket.accept()
            print(f"Connection from C program at {client_address}", flush=True)
            
            # Start a new thread to handle this client
            client_thread = threading.Thread(target=handle_c_program_connection, args=(client_socket,))
            client_thread.daemon = True
            client_thread.start()
    except Exception as e:
        print(f"TCP server error: {e}", flush=True)
    finally:
        server_socket.close()

# Add this function to handle each connection from the C program
def handle_c_program_connection(client_socket):
    try:
        data = client_socket.recv(1024)
        if data:
            message = data.decode()
            print(f"Message from C program: {message}", flush=True)
            
            # Send acknowledgment back
            client_socket.sendall("Message received by Python client".encode())
    except Exception as e:
        print(f"Error handling C program connection: {e}", flush=True)
    finally:
        client_socket.close()

if __name__ == '__main__':
    main()
