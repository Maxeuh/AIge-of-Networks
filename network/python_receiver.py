import socket
import threading
import time
import select

class NetworkReceiver:
    def __init__(self, ip="127.0.0.1", port=8081, buffer_size=2048):
        """
        Initialize the network receiver that gets updates from the C layer.
        
        Args:
            ip: Local IP address to bind to (default: 127.0.0.1)
            port: Port to listen on (default: 8081)
            buffer_size: Maximum message size to receive
        """
        self.ip = ip
        self.port = port
        self.buffer_size = buffer_size
        self.socket = None
        self.running = False
        self.callback = None
        self.receive_thread = None
        
    def start(self, callback=None):
        """
        Start listening for messages from the C program.
        
        Args:
            callback: Function called when a message is received (gets message as argument)
        
        Returns:
            bool: True if started successfully, False otherwise
        """
        if self.running:
            print("Receiver is already running")
            return False
        
        try:
            self.callback = callback
            self.running = True
            
            # Create and configure the socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.bind((self.ip, self.port))
            self.socket.setblocking(False)
            
            # Start receiving thread
            self.receive_thread = threading.Thread(target=self._receive_loop)
            self.receive_thread.daemon = True
            self.receive_thread.start()
            
            print(f"Network receiver started on {self.ip}:{self.port}")
            return True
            
        except Exception as e:
            print(f"Failed to start network receiver: {e}")
            self.stop()
            return False
    
    def stop(self):
        """Stop the receiver and clean up resources."""
        self.running = False
        if self.receive_thread:
            self.receive_thread.join(timeout=1.0)
            self.receive_thread = None
            
        if self.socket:
            self.socket.close()
            self.socket = None
            
        print("Network receiver stopped")
    
    def _receive_loop(self):
        """Main receiving loop that runs in a separate thread."""
        while self.running:
            try:
                # Use select to wait for data with timeout (non-blocking)
                readable, _, _ = select.select([self.socket], [], [], 0.1)
                
                if self.socket in readable:
                    data, addr = self.socket.recvfrom(self.buffer_size)
                    message = data.decode('ascii')
                    
                    ip, port = addr
                    print(f"Received from {ip}:{port}: {message[:50]}{'...' if len(message) > 50 else ''}")
                    
                    # Call the callback if provided
                    if self.callback:
                        self.callback(message)
                        
            except Exception as e:
                print(f"Error in receive loop: {e}")
                time.sleep(0.1)  # Prevent CPU hogging in case of errors

def example_callback(message):
    """Example callback function to process received messages."""
    print(f"\nReceived network update: {message}")
    # Here you would update your game state based on the received message
    # For now, we just parse and print it
    
    if ":" in message:
        parts = message.split(":")
        if len(parts) >= 2:
            msg_type = parts[0]
            
            if msg_type == "POS":
                # Position update
                if len(parts) >= 4:
                    entity = parts[1]
                    x = parts[2]
                    y = parts[3]
                    print(f"Position update for {entity}: ({x}, {y})")
            
            elif msg_type == "ACT":
                # Action update
                if len(parts) >= 3:
                    entity = parts[1]
                    action = parts[2]
                    print(f"{entity} is performing action: {action}")
            
            elif msg_type == "EVT":
                # Game event
                event_type = parts[1]
                params = parts[2:] if len(parts) > 2 else []
                print(f"Game event {event_type} with parameters: {params}")

def main():
    """Run the network receiver."""
    receiver = NetworkReceiver(ip="127.0.0.1", port=8081)
    receiver.start(callback=example_callback)
    
    try:
        print("Network receiver running (press Ctrl+C to quit)...")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        receiver.stop()

if __name__ == "__main__":
    main()