import socket
import threading
import json

class NetworkController:
    """
    The goal of this class is to provide a way to interact with the other
    players on the network, by sending and receiving messages.
    This class sends messages locally to the C program that runs with the
    game, and receives messages from it, using TCP sockets and the port 9090.
    """

    def __init__(self) -> None:
        # TCP socket for sending to local relay
        self.__sock = None
        self.__address = ("127.0.0.1", 9090)
        self.__connected = False
        self.__create_socket()
        
        # New UDP socket for receiving broadcasts from other machines
        self.__udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__udp_sock.bind(('', 9091))  # Listen on all interfaces, port 9091
        
        # Start UDP receiver thread
        self.__running = True
        self.__received_data = []
        self.__receiver_thread = threading.Thread(target=self.__listen_for_broadcasts)
        self.__receiver_thread.daemon = True
        self.__receiver_thread.start()
        
    def __create_socket(self) -> None:
        """Create a new socket with appropriate settings"""
        if self.__sock:
            try:
                self.__sock.close()
            except:
                pass
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__sock.settimeout(1.0)

    def connect(self) -> bool:
        """
        Connects to the C program that runs the game.
        """
        if self.__connected:
            return True
            
        # Create a fresh socket for connection attempts
        self.__create_socket()
            
        try:
            #print(f"[DEBUG] Connecting to {self.__address[0]}:{self.__address[1]}...")
            self.__sock.connect(self.__address)
            self.__connected = True
            #print("[DEBUG] Connected successfully")
            return True
        except ConnectionRefusedError:
            #print("[DEBUG] Connection refused - is the receiver running?")
            return False
        except Exception as e:
            #print(f"[DEBUG] Connection error: {e}")
            return False

    def send(self, message: str) -> None:
        """
        Sends a message to the C program that runs the game.
        """
        #print(f"[DEBUG] Sending TCP: {message[:50]}...")  # Print first 50 chars
        
        if not self.__connected and not self.connect():
            #print("[DEBUG] Failed to connect")
            return
            
        try:
            self.__sock.sendall(message.encode())
            #print("[DEBUG] Message sent successfully")
        except Exception as e:
            #print(f"[DEBUG] Error sending message: {e}")
            self.__connected = False

    def receive(self) -> str:
        """
        Receives a message from the C program that runs the game.
        """
        if not self.__connected:
            return ""
            
        try:
            data = self.__sock.recv(1024)
            return data.decode()
        except socket.timeout:
            return ""
        except Exception as e:
            #print(f"[DEBUG] Error receiving message: {e}")
            self.__connected = False
            return ""

    def __listen_for_broadcasts(self):
        """Background thread that listens for UDP broadcasts from other games"""
        self.__udp_sock.settimeout(0.5)  # Short timeout for checking __running
        
        while self.__running:
            try:
                data, addr = self.__udp_sock.recvfrom(1048576)  # 1MB buffer
                if data:
                    # Store received data and log
                    decoded_data = data.decode()
                    print(f"Received broadcast from {addr[0]}:{addr[1]}")
                    # Don't process our own messages - check source IP
                    if addr[0] != "127.0.0.1":  # Not from ourselves
                        self.__received_data.append(decoded_data)
            except socket.timeout:
                # This is just for the timeout to check __running periodically
                pass
            except Exception as e:
                print(f"UDP receive error: {e}")
    
    def get_received_broadcasts(self):
        """Returns and clears the list of received broadcasts"""
        data = self.__received_data.copy()
        self.__received_data.clear()
        return data
    
    def close(self) -> None:
        """Closes both TCP and UDP sockets and stops the receiver thread."""
        self.__running = False
        if self.__sock:
            self.__sock.close()
        if hasattr(self, '__udp_sock') and self.__udp_sock:
            self.__udp_sock.close()
        self.__connected = False
