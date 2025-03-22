import socket


class NetworkController:
    """
    The goal of this class is to provide a way to interact with the other
    players on the network, by sending and receiving messages.
    This class sends messages locally to the C program that runs with the
    game, and receives messages from it, using TCP sockets and the port 9090.
    """

    def __init__(self) -> None:
        self.__sock = None
        self.__address = ("127.0.0.1", 9090)
        self.__connected = False
        self.__create_socket()
        
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
            print(f"[DEBUG] Connecting to {self.__address[0]}:{self.__address[1]}...")
            self.__sock.connect(self.__address)
            self.__connected = True
            print("[DEBUG] Connected successfully")
            return True
        except ConnectionRefusedError:
            print("[DEBUG] Connection refused - is the receiver running?")
            return False
        except Exception as e:
            print(f"[DEBUG] Connection error: {e}")
            return False

    def send(self, message: str) -> None:
        """
        Sends a message to the C program that runs the game.
        """
        print(f"[DEBUG] Sending TCP: {message[:50]}...")  # Print first 50 chars
        
        if not self.__connected and not self.connect():
            print("[DEBUG] Failed to connect")
            return
            
        try:
            self.__sock.sendall(message.encode())
            print("[DEBUG] Message sent successfully")
        except Exception as e:
            print(f"[DEBUG] Error sending message: {e}")
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
            print(f"[DEBUG] Error receiving message: {e}")
            self.__connected = False
            return ""

    def close(self) -> None:
        """
        Closes the socket.
        """
        self.__sock.close()
        self.__connected = False
