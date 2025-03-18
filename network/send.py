import socket
import time

UDP_IP = "127.0.0.1"  # Adresse IP du serveur C (en local)
UDP_PORT = 8080       # Port sur lequel le serveur écoute

def send_message_to_c(message):
    """Envoie un message au programme C via UDP."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(message.encode('utf-8'), (UDP_IP, UDP_PORT))
        print(f"Message envoyé: {message}")
        return True
    except Exception as e:
        print(f"Erreur lors de l'envoi du message: {e}")
        return False
    finally:
        sock.close()

def main():
    """Fonction principale qui permet d'envoyer des messages interactivement."""
    print(f"Client UDP Python prêt à envoyer des messages à {UDP_IP}:{UDP_PORT}")
    print("Tapez 'exit' pour quitter.")
    
    while True:
        message = input("Message à envoyer au C: ")
        
        if message.lower() == "exit":
            print("Fermeture du client...")
            break
            
        send_message_to_c(message)

if __name__ == "__main__":
    main()