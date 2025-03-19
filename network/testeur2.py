import socket
import time

def test_send():
    # Configuration du client UDP
    UDP_IP = "127.0.0.1"  # Adresse locale
    UDP_PORT = 8080       # Port du receive_send.c
    
    # Création du socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Messages de test
    test_messages = [
        "Test message 1",
        "Hello World!",
        "Message de test 3",
        "Test final"
    ]
    
    # Envoi des messages
    for message in test_messages:
        print(f"Envoi du message: {message}")
        client_socket.sendto(message.encode(), (UDP_IP, UDP_PORT))
        time.sleep(1)  # Attente d'une seconde entre chaque message
    
    client_socket.close()

if __name__ == "__main__":
    test_send()