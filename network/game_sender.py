import socket
import json
import threading
import time
from typing import List, Dict, Any, Tuple

from network.game_data import get_items_data


class GameSender:
    """
    A class to send game data to clients using UDP protocol.
    Acts as the server side of the networking component.
    """
    
    def __init__(self, host: str = '127.0.0.1', port: int = 12345, client_port: int = 12345):
        """
        Initialize the UDP game sender.
        
        Args:
            host: IP address to bind to (default: localhost)
            port: Port to use for communication (default: 12345)
            client_port: Port the client is listening on (default: same as server)
        """
        self.host = host
        self.port = port
        self.socket = None
        self.running = False
        self.clients = [('127.0.0.1', client_port)]  # Add default client immediately
        self.game_controller = None
        self.send_thread = None
        self.frame_counter = 0
    
    def setup(self, game_controller):
        """
        Set up the UDP socket and store game controller reference.
        
        Args:
            game_controller: Reference to the game controller
        """
        self.game_controller = game_controller
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            print(f"Game sender initialized on {self.host}:{self.port}")
            return True
        except socket.error as e:
            print(f"Socket creation error: {e}")
            return False
    
    def start(self):
        """Start the sender thread to periodically send game data."""
        if self.game_controller is None:
            print("Error: Game controller not set. Call setup() first.")
            return False
        
        self.running = True
        self.send_thread = threading.Thread(target=self._send_loop)
        self.send_thread.daemon = True
        self.send_thread.start()
        return True
    
    def stop(self):
        """Stop the sender thread and close the socket."""
        self.running = False
        if self.send_thread:
            self.send_thread.join(timeout=1.0)
        
        if self.socket:
            self.socket.close()
            self.socket = None
    
    def _send_loop(self):
        """Background thread that sends game data periodically."""
        last_data_hash = None
        
        while self.running:
            try:
                game_data = self._prepare_game_data()
                
                # Only send if data has changed
                current_hash = hash(str(game_data))
                if current_hash != last_data_hash:
                    self._broadcast_data(game_data)
                    print("Sent updated game data")
                    last_data_hash = current_hash
                else:
                    print("Game state unchanged, skipping update")
                    
                time.sleep(0.1)
            except Exception as e:
                print(f"Error in send loop: {e}")
    
    def _prepare_game_data(self) -> Dict[str, Any]:
        """
        Prepare the game data to be sent.
        
        Returns:
            Dict containing game state information
        """
        self.frame_counter += 1
        
        items_data = get_items_data(self.game_controller)
        
        # Create the data packet with frame number, timestamp, and items
        data_packet = {
            "frame": self.frame_counter,
            "timestamp": time.time(),
            "items": items_data
        }
        
        return data_packet
    
    def _broadcast_data(self, data: Dict[str, Any]):
        """
        Broadcast data to default client, handling large packets.
        
        Args:
            data: Dictionary of game data to send
        """
        try:
            # Serialize data to JSON
            json_data = json.dumps(data).encode('utf-8')
            total_size = len(json_data)
            
            # Check if data is too large
            if total_size > 8192:  # Safe UDP packet size
                print(f"Data size ({total_size} bytes) exceeds safe UDP packet size. Sending compressed data.")
                
                # Option 1: Compress the data
                import zlib
                compressed_data = zlib.compress(json_data)
                print(f"Compressed from {total_size} to {len(compressed_data)} bytes")
                
                # Add header to indicate this is compressed data
                header = b"COMPRESSED:"
                data_to_send = header + compressed_data
                
                # Send to each client
                for client in self.clients:
                    try:
                        self.socket.sendto(data_to_send, client)
                        print(f"Compressed data sent to {client}")
                    except Exception as e:
                        print(f"Error sending to {client}: {e}")
            else:
                # Data is small enough to send directly
                for client in self.clients:
                    try:
                        self.socket.sendto(json_data, client)
                        print(f"Data sent to {client} ({total_size} bytes)")
                    except Exception as e:
                        print(f"Error sending to {client}: {e}")
                    
        except (socket.error, json.JSONDecodeError) as e:
            print(f"Error sending data: {e}")
    
    # Keep registration for backward compatibility
    def handle_client_registration(self):
        """Just a stub - we don't need registration anymore"""
        pass