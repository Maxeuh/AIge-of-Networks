import threading
import time
import typing
if typing.TYPE_CHECKING:
    from controller.game_controller import GameController
    from view.view_2_5D import View2_5D

class DataSender:
    """
    Periodically gathers map data and sends it to the C relay via UDP.
    """
    def __init__(self, game_controller: 'GameController', view, interval: float = 1.0):
        """
        Initialize the data sender.
        
        :param game_controller: The game controller instance
        :param view: The view instance
        :param interval: Time between updates in seconds
        """
        self.game_controller = game_controller
        self.view = view
        self.interval = interval
        self.running = False
        self.thread = None

    def start(self):
        """Start the periodic sending thread"""
        self.running = True
        self.thread = threading.Thread(target=self._send_loop)
        self.thread.daemon = True  # Thread will exit when main program exits
        self.thread.start()
        print("Data sender started - streaming map data to C relay")
        
    def stop(self):
        """Stop the periodic sending thread"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)
            
    def _send_loop(self):
        """Main loop that gathers and sends data periodically"""
        print("Data sender thread started")
        while self.running:
            try:
                # Send a test message first to confirm connectivity
                test_message = {"test": "Hello from game engine!", "timestamp": time.time()}
                success = self.game_controller.send_data_to_c_relay(test_message)
                if success:
                    print("Test message sent successfully to relay")
                else:
                    print("Failed to send test message")
                    
                # Then try to gather and send real data
                print("Gathering map data...")
                map_data = self.view.gather_map_items()
                print(f"Gathered {len(map_data) if map_data else 0} map items")
                
                if not map_data:
                    print("No map data found, skipping send")
                    time.sleep(self.interval)
                    continue
                
                # Convert dictionary keys from tuples to strings
                formatted_data = {f"{x},{y}": letter for (x, y), letter in map_data.items()}
                
                # Add timestamp and metadata
                message = {
                    "timestamp": time.time(),
                    "map_size": self.game_controller.get_map().get_size(),
                    "items": formatted_data
                }
                
                print(f"Sending data to relay: {len(formatted_data)} items")
                success = self.game_controller.send_data_to_c_relay(message)
                if success:
                    print("Data sent successfully to 127.0.0.1:8080")
                else:
                    print("Failed to send map data to C relay")
                    
            except Exception as e:
                print(f"ERROR in data sender: {e}")
                import traceback
                traceback.print_exc()
                
            time.sleep(self.interval)

def create_data_sender(game_controller, view, interval=1.0):
    """
    Create and start a data sender.
    
    :param game_controller: The game controller instance
    :param view: The view instance  
    :param interval: Time between updates in seconds
    :return: Running DataSender instance
    """
    sender = DataSender(game_controller, view, interval)
    sender.start()
    return sender

