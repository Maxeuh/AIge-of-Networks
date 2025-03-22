from controller.menu_controller import MenuController
from controller.game_controller import GameController
import subprocess
import os
import threading
import time
import sys
import argparse
from model.FULL_RESAUX import pythoncli
import signal
import atexit
from network.c_program_runner import CNetworkRunner

# Create a global reference to the C program runner
c_runner = None

def parse_arguments():
    """Parse command line arguments for game instance"""
    parser = argparse.ArgumentParser(description='AIge of Networks Game')
    parser.add_argument('--player', type=int, default=1, choices=[1, 2],
                      help='Player number (1 or 2)')
    parser.add_argument('--port-offset', type=int, default=0,
                      help='Port offset for this instance')
    parser.add_argument('--network-only', action='store_true',
                      help='Start only the network components, not the game')
    parser.add_argument('--debug-network', action='store_true',
                      help='Show detailed network messages')
    return parser.parse_args()

def cleanup():
    """Clean up resources before exit"""
    global c_runner
    if c_runner:
        c_runner.stop()

# Register the cleanup function
atexit.register(cleanup)

def start_network(game_controller, args):
    """Start network components with specified parameters"""
    global c_runner
    
    # Set player number and port offset in the Python client
    pythoncli.set_player_number(args.player)
    pythoncli.set_port_offset(args.port_offset)
    
    # Find the right C program path based on platform
    c_program_path = os.path.join(os.path.dirname(__file__), 'model/FULL_RESAUX/ourmain')
    if not os.path.exists(c_program_path):
        # Try Linux-specific path
        c_program_path = os.path.join(os.path.dirname(__file__), 'model/FULL_RESAUX/ourmain_linux')
        if not os.path.exists(c_program_path):
            print("Error: Could not find C network program!")
            return
    
    # Start C program with arguments if first player
    if args.player == 1 or args.network_only:
        # Use our special C program runner with filtered output
        c_runner = CNetworkRunner(c_program_path, args.port_offset, debug=args.debug_network)
        success = c_runner.start()
        
        if success and args.debug_network:
            print(f"Started network C program (Player {args.player}, Port Offset: {args.port_offset})")
        elif not success:
            print(f"Failed to start network C program")
    
    # Wait for C program to initialize
    time.sleep(1)
    
    # Register game controller with network client
    if game_controller:
        pythoncli.set_game_controller(game_controller)
    
    # Start network thread with minimal output
    def run_network():
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        
        if not args.debug_network:
            # Create a null device for unwanted output
            class NullWriter:
                def write(self, s): pass
                def flush(self): pass
            
            # Redirect Python client output
            sys.stdout = NullWriter()
            sys.stderr = NullWriter()
        
        try:
            # Run network client
            pythoncli.main()
        finally:
            # Restore stdout/stderr
            sys.stdout = original_stdout
            sys.stderr = original_stderr
    
    network_thread = threading.Thread(target=run_network)
    network_thread.daemon = True
    network_thread.start()
    
    if args.debug_network:
        print(f"Started network client thread (Player {args.player})")

def main():
    """Main function to start the game"""
    # Parse arguments
    args = parse_arguments()
    
    # Create controllers with proper dependency handling
    if not args.network_only:
        # Create menu controller first - without parameters
        menu_controller = MenuController()
        
        # Create game controller with menu controller
        game_controller = GameController(menu_controller, player_number=args.player)
        
        # Update menu controller with game controller
        menu_controller.set_game_controller(game_controller)
        
        # Start network components
        start_network(game_controller, args)
        
        print(f"Starting game as Player {args.player}")
        # Menu controller is already initialized - just start it
        menu_controller.start()
    else:
        # You need a temporary MenuController even for network-only mode
        menu_controller = MenuController()
        game_controller = GameController(menu_controller, player_number=args.player)
        start_network(game_controller, args)

if __name__ == "__main__":
    main()