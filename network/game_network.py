import socket
import json
import threading
from typing import Dict, Any

class GameEventSender:
    """Sends game events to the network via the C program"""
    
    def __init__(self):
        self.ipc_socket = None
        self.connected = False
        self.ipc_host = '127.0.0.1'
        self.ipc_port = 12347
        self.connect()
        
    def connect(self):
        """Connect to the C network client"""
        try:
            self.ipc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.ipc_socket.connect((self.ipc_host, self.ipc_port))
            self.connected = True
            print("Connected to network client")
        except Exception as e:
            print(f"Failed to connect to network client: {e}")
            self.connected = False
            
    def send_event(self, event_type: str, event_data: Dict[str, Any]) -> bool:
        """
        Send a game event to be broadcast to other players
        
        :param event_type: Type of event (MOVE, BUILD, ATTACK, etc.)
        :param event_data: Dictionary containing event details
        :return: True if sent successfully, False otherwise
        """
        if not self.connected:
            self.connect()
            if not self.connected:
                return False
                
        try:
            # Format as JSON with a clear prefix for message type
            message = f"GAME_EVENT:{event_type}:{json.dumps(event_data)}"
            self.ipc_socket.sendall(message.encode('utf-8'))
            return True
        except Exception as e:
            print(f"Failed to send game event: {e}")
            self.connected = False
            return False
    
    def close(self):
        """Close the connection"""
        if self.ipc_socket:
            self.ipc_socket.close()
            self.connected = False

class GameEventProcessor:
    """Processes game events received from the network"""
    
    def __init__(self, game_controller):
        self.game_controller = game_controller
    
    def process_event(self, event_type: str, event_data: Dict[str, Any]) -> bool:
        """Process a received game event"""
        try:
            print(f"Processing event: {event_type}")
            print(f"Event data: {event_data}")
            
            if event_type == "MOVE":
                return self._process_move_event(event_data)
            elif event_type == "BUILD":
                return self._process_build_event(event_data)
            elif event_type == "ATTACK":
                return self._process_attack_event(event_data)
            else:
                print(f"Unknown event type: {event_type}")
                return False
        except Exception as e:
            print(f"Error processing game event: {e}")
            return False
    
    def _process_move_event(self, event_data):
        """Process a movement event"""
        # Extract entity info
        entity_id = event_data.get("entity_id")
        player_id = event_data.get("player_id")
        new_position = event_data.get("new_position")
        
        if not entity_id or not new_position:
            return False
            
        # Find the entity in the game
        entity = self._find_entity(entity_id)
        if not entity:
            print(f"Entity not found: {entity_id}")
            return False
            
        # Update the entity's position
        try:
            from util.coordinate import Coordinate
            coordinate = Coordinate(new_position["x"], new_position["y"])
            entity._coordinate = coordinate  # Direct update to avoid triggering another event
            print(f"Updated entity {entity_id} position to {new_position}")
            return True
        except Exception as e:
            print(f"Error updating entity position: {e}")
            return False
    
    def _find_entity(self, entity_id):
        """Find an entity in the game by ID"""
        try:
            for player in self.game_controller.get_players():
                # Check units
                for unit in player.get_units():
                    if hasattr(unit, "get_id") and unit.get_id() == entity_id:
                        return unit
                
                # Check buildings
                for building in player.get_buildings():
                    if hasattr(building, "get_id") and building.get_id() == entity_id:
                        return building
        except Exception as e:
            print(f"Error finding entity: {e}")
        
        return None
    
    # Implement other event processors as needed
    def _process_build_event(self, event_data):
        """Process a building event"""
        print("Build event processing not yet implemented")
        return False
        
    def _process_attack_event(self, event_data):
        """Process an attack event"""
        print("Attack event processing not yet implemented")
        return False