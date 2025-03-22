import socket
import threading
import json
from typing import Dict, Any
import time

class NetworkManager:
    """Manages network communication for the game"""
    
    def __init__(self, game_controller=None):
        self.game_controller = game_controller
        self.listen_thread = None
        self.running = True
        self.python_listen_port = 12348
        self.c_program_port = 12347
    
    def start(self):
        """Start the network manager"""
        # Start listener thread
        self.listen_thread = threading.Thread(target=self._listen_for_messages)
        self.listen_thread.daemon = True
        self.listen_thread.start()
        print("Network manager started")
    
    def _listen_for_messages(self):
        """Listen for messages from the C program"""
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            server.bind(('0.0.0.0', self.python_listen_port))
            server.listen(5)
            server.settimeout(1.0)  # 1 second timeout for clean shutdown
            print(f"Listening for game events on port {self.python_listen_port}")
            
            while self.running:
                try:
                    client, addr = server.accept()
                    # Handle the message in a new thread
                    thread = threading.Thread(target=self._handle_message, args=(client,))
                    thread.daemon = True
                    thread.start()
                except socket.timeout:
                    continue  # Just a timeout, check if we should still be running
                except Exception as e:
                    print(f"Error accepting connection: {e}")
        except Exception as e:
            print(f"Error in listener thread: {e}")
        finally:
            server.close()
    
    def _handle_message(self, client_socket):
        """Handle a received message"""
        try:
            data = client_socket.recv(1024)
            if data:
                message = data.decode()
                print(f"Network message received: {message[:50]}...")
                
                # Send acknowledgment
                client_socket.send(b"Message received by Python")
                
                # Process the message
                self._process_message(message)
        except Exception as e:
            print(f"Error handling message: {e}")
        finally:
            client_socket.close()
    
    def _process_message(self, message):
        """Process a received network message"""
        try:
            # Format: P<player_id>|<message_content>
            if '|' in message:
                parts = message.split('|', 1)
                player_prefix = parts[0]
                content = parts[1]
                
                # Ignore messages from ourselves
                if self.game_controller and player_prefix != f"P{self.game_controller.player_number}":
                    print(f"Processing message from another player: {content[:30]}...")
                    
                    # Determine message type and handle accordingly
                    if content.startswith("GAME_EVENT:"):
                        self._handle_game_event(content)
                    else:
                        print(f"Unknown message type: {content[:20]}...")
            else:
                print(f"Invalid message format: {message[:30]}...")
        except Exception as e:
            print(f"Error processing message: {e}")
    
    def _handle_game_event(self, event_message):
        """Handle a game event message"""
        # Parse the message format: GAME_EVENT:EVENT_TYPE:JSON_DATA
        parts = event_message.split(':', 2)
        if len(parts) < 3:
            print(f"Invalid game event format: {event_message[:30]}...")
            return
            
        event_type = parts[1]
        try:
            event_data = json.loads(parts[2])
            
            # Update the game state based on the event
            if self.game_controller:
                self._update_game_state(event_type, event_data)
        except json.JSONDecodeError as e:
            print(f"Error parsing event data: {e}")
    
    def _update_game_state(self, event_type, event_data):
        """Update the game state based on the event"""
        from network.game_network import GameEventProcessor
        processor = GameEventProcessor(self.game_controller)
        processor.process_event(event_type, event_data)
    
    def send_game_event(self, event_type, event_data):
        """Send a game event to other players"""
        try:
            message = f"GAME_EVENT:{event_type}:{json.dumps(event_data)}"
            
            # Send via socket
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(('127.0.0.1', self.c_program_port))
            s.send(message.encode())
            response = s.recv(1024)
            s.close()
            
            return True
        except Exception as e:
            print(f"Error sending game event: {e}")
            return False
    
    def stop(self):
        """Stop the network manager"""
        self.running = False
        if self.listen_thread and self.listen_thread.is_alive():
            self.listen_thread.join(2.0)  # Wait up to 2 seconds