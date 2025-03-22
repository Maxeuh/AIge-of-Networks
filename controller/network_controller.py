import socket
import threading
import json
import time

class NetworkController:
    """
    The goal of this class is to provide a way to interact with the other
    players on the network, by sending and receiving messages.
    This class sends messages locally to the C program that runs with the
    game, and receives messages from it, using UDP sockets.
    """

    def __init__(self) -> None:
        # UDP socket for sending to local relay
        self.__sock = None
        self.__address = ("127.0.0.1", 9090)
        self.__connected = False
        self.__create_socket()
        
        # UDP socket for receiving broadcasts from other machines
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
        """Create a new UDP socket with appropriate settings"""
        if self.__sock:
            try:
                self.__sock.close()
            except:
                pass
        # Changed to UDP socket
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__connected = True  # UDP doesn't need connection

    def connect(self) -> bool:
        """
        For UDP, we don't need to connect, but we keep this method for compatibility
        """
        if not self.__sock:
            self.__create_socket()
        return True

    def send(self, message: str) -> None:
        """
        Sends a message to the receiver.c program using UDP.
        Handles large messages by splitting them into chunks.
        """
        if not self.__sock:
            self.__create_socket()
            
        try:
            # Split message if needed
            MAX_CHUNK_SIZE = 60000  # Safe UDP packet size
            data = message.encode()
            
            if len(data) > MAX_CHUNK_SIZE:
                # For large messages like MAP_DATA, split into chunks
                chunks = [data[i:i+MAX_CHUNK_SIZE] for i in range(0, len(data), MAX_CHUNK_SIZE)]
                msg_id = int(time.time() * 1000)  # Unique message ID
                
                for i, chunk in enumerate(chunks):
                    # Format: CHUNK;msg_id;chunk_num;total_chunks;data
                    header = f"CHUNK;{msg_id};{i};{len(chunks)};".encode()
                    self.__sock.sendto(header + chunk, self.__address)
                    time.sleep(0.01)  # Prevent network congestion
                    print(f"Sent chunk {i+1}/{len(chunks)} of size {len(chunk)}")
            else:
                # For small messages, send directly
                self.__sock.sendto(data, self.__address)
        except Exception as e:
            print(f"Error sending UDP message: {e}")

    def receive(self) -> str:
        """
        This method is not used with UDP as we use the receiver thread instead
        """
        return ""

    def __listen_for_broadcasts(self):
        """Background thread that listens for UDP broadcasts from other games"""
        self.__udp_sock.settimeout(0.5)  # Short timeout for checking __running
        
        # Store our own IP addresses to filter out our broadcasts
        import socket
        local_ip = socket.gethostbyname(socket.gethostname())
        localhost = "127.0.0.1"
        own_ips = [local_ip, localhost]
        
        # Dictionary to store reassembled chunked messages
        chunked_messages = {}
        
        print(f"Listening for broadcasts on port 9091, own IPs: {own_ips}")
        
        while self.__running:
            try:
                data, addr = self.__udp_sock.recvfrom(1048576)  # 1MB buffer
                if data:
                    # Check if it's from ourselves
                    if addr[0] in own_ips:
                        continue
                        
                    decoded_data = data.decode()
                    print(f"Received broadcast from {addr[0]}:{addr[1]}")
                    
                    # Check if it's a chunked message
                    if decoded_data.startswith("CHUNK;"):
                        # Process chunking (this is handled by receiver.c in this architecture)
                        pass
                    else:
                        # Normal message, process directly
                        self.__received_data.append(decoded_data)
            except socket.timeout:
                # This is just for the timeout to check __running periodically
                pass
            except UnicodeDecodeError:
                print("Received binary data that couldn't be decoded")
            except Exception as e:
                print(f"UDP receive error: {e}")
    
    def get_received_broadcasts(self):
        """Returns and clears the list of received broadcasts"""
        data = self.__received_data.copy()
        self.__received_data.clear()
        return data
    
    def close(self) -> None:
        """Closes both UDP sockets and stops the receiver thread."""
        self.__running = False
        if self.__sock:
            self.__sock.close()
        if hasattr(self, '__udp_sock') and self.__udp_sock:
            self.__udp_sock.close()
        self.__connected = False
