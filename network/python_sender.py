import socket
import time

class NetworkSender:
    def __init__(self, ip="172.20.1.63", port=8082):
        """
        Initialize the network sender that sends updates to the C layer.
        
        Args:
            ip: IP address of the C program (default: 172.20.1.63)
            port: Port the C program is listening on (default: 8082)
        """
        self.ip = ip
        self.port = port
        self.socket = None
        self._create_socket()
        
    def _create_socket(self):
        """Create and configure the UDP socket."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            print(f"Network sender initialized, target: {self.ip}:{self.port}")
        except Exception as e:
            print(f"Failed to create socket: {e}")
            self.socket = None
    
    def send(self, message):
        """
        Send a message to the C layer for broadcasting.
        
        Args:
            message: String message to send
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.socket:
            print("Socket not initialized, attempting to recreate")
            self._create_socket()
            if not self.socket:
                return False
        
        try:
            self.socket.sendto(message.encode('ascii'), (self.ip, self.port))
            print(f"Sent: {message[:50]}{'...' if len(message) > 50 else ''}")
            return True
        except Exception as e:
            print(f"Error sending message: {e}")
            return False
    
    def close(self):
        """Close the socket and free resources."""
        if self.socket:
            self.socket.close()
            self.socket = None
            print("Network sender closed")
    
    # Helper methods for common game updates
    
    def send_position(self, entity_id, x, y):
        """Send entity position update."""
        message = f"POS:{entity_id}:{x}:{y}"
        return self.send(message)
    
    def send_action(self, entity_id, action):
        """Send entity action update."""
        message = f"ACT:{entity_id}:{action}"
        return self.send(message)
    
    def send_event(self, event_type, *args):
        """Send game event with variable parameters."""
        message = f"EVT:{event_type}"
        for arg in args:
            message += f":{arg}"
        return self.send(message)

def main():
    """Run a test of the network sender."""
    sender = NetworkSender()
    
    try:
        # Send some test messages
        sender.send_position("player1", 100, 200)
        time.sleep(1)
        
        sender.send_action("player1", "attack")
        time.sleep(1)
        
        sender.send_event("collision", "player1", "enemy5")
        time.sleep(1)
        
        # Custom message
        sender.send("CUSTOM:This is a test message")
        time.sleep(1)
        
        # Test message input loop
        print("\nEnter messages to send (or 'exit' to quit):")
        while True:
            message = input("> ")
            if message.lower() == "exit":
                break
                
            sender.send(message)
            
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        sender.close()

if __name__ == "__main__":
    main()