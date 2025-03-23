import socket
import threading
import json
import time

class NetworkController:
    """
    The goal of this class is to provide a way to interact with the other
    players on the network, by sending and receiving messages.
    This class sends messages locally to the C program using TCP,
    and receives messages from other games via UDP broadcasts.
    """

    def __init__(self) -> None:
        # TCP socket for sending to local relay
        self.__sock = None
        self.__address = ("127.0.0.1", 9090)
        self.__connected = False
        
        
        
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
        """Create a new TCP socket for communication with the relay"""
        if self.__sock:
            try:
                self.__sock.close()
            except:
                pass
        # Changed to TCP socket
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__connected = False

    def connect(self) -> bool:
        """
        Connect to the local relay program using TCP
        """
        if not self.__sock:
            self.__create_socket()
            
        if not self.__connected:
            try:
                self.__sock.connect(self.__address)
                self.__connected = True
                #print(f"Connected to relay at {self.__address[0]}:{self.__address[1]}")
                return True
            except Exception as e:
                print(f"TCP connection failed: {e}")
                return False
        return True

    def send(self, message: str) -> None:
        """
        Sends a message to the relay program using TCP.
        Handles large messages by adding length prefix.
        """
        if not self.__sock or not self.__connected:
            if not self.connect():
                print("Failed to connect, cannot send message")
                return
            
        try:
            # Encode the message
            data = message.encode()
            
            # Send message length as 4-byte integer
            message_len = len(data)
            self.__sock.sendall(message_len.to_bytes(4, byteorder='big'))
            
            # Send the actual message data
            self.__sock.sendall(data)
            
            #print(f"Sent {message_len} bytes via TCP")
        except Exception as e:
            print(f"Error sending TCP message: {e}")
            self.__connected = False
            self.__create_socket()  # Reset socket for next attempt

    def __listen_for_broadcasts(self):
        """Background thread that listens for UDP broadcasts from other games"""
        self.__udp_sock.settimeout(0.5)  # Short timeout for checking __running
        
        # Store our own IP addresses to filter out our broadcasts
        local_ip = socket.gethostbyname(socket.gethostname())
        localhost = "127.0.0.1"
        # Get all interface IPs to properly filter our own broadcasts
        own_ips = [localhost, local_ip]
        try:
            # Try to get all interface IPs
            for interface in socket.getaddrinfo(socket.gethostname(), None):
                if interface[4][0] not in own_ips:
                    own_ips.append(interface[4][0])
        except:
            pass
            
        #print(f"Listening for broadcasts on port 9091, own IPs: {own_ips}")
        
        while self.__running:
            try:
                data, addr = self.__udp_sock.recvfrom(1048576)  # 1MB buffer
                if data:
                    # Check if it's from ourselves
                    if addr[0] in own_ips:
                        continue
                        
                    decoded_data = data.decode()
                    #print(f"Received broadcast from {addr[0]}:{addr[1]}, {len(decoded_data)} bytes")
                    
                    # Add to received data queue
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
        """Closes both sockets and stops the receiver thread."""
        self.__running = False
        if self.__sock:
            try:
                self.__sock.close()
            except:
                pass
        if hasattr(self, '__udp_sock') and self.__udp_sock:
            try:
                self.__udp_sock.close()
            except:
                pass
        self.__connected = False
