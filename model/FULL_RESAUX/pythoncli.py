import sys
import os
sys.path.append('/home/hblbechir/AIge-of-Networks')
from network.quiet_print import enable_quiet_print, disable_quiet_print

# Enable quiet printing at startup
enable_quiet_print()

import socket
import threading
import json
import sys
import time
import argparse
import subprocess

# Add project root to path
sys.path.append('/home/hblbechir/AIge-of-Networks')

# Correct import paths
from network.game_network import GameEventProcessor
from controller.menu_controller import MenuController
from controller.game_controller import GameController

# Debug flag to control verbose output
DEBUG_OUTPUT = False  # Set to False to suppress network messages

def debug_print(message, force=False):
    """Only print if debug output is enabled or forced"""
    if DEBUG_OUTPUT or force:
        print(message)

# Global variables
game_controller = None
player_number = 1
port_offset = 0

# Base ports (adjust as needed to match your C program)
BASE_PYTHON_PORT = 12345
BASE_C_PORT = 12346

def set_game_controller(controller):
    global game_controller
    game_controller = controller
    debug_print(f"Game controller registered with network client (Player {player_number})")

def set_player_number(number):
    global player_number
    player_number = number
    debug_print(f"Network client configured as Player {player_number}")

def set_port_offset(offset):
    global port_offset
    port_offset = offset
    debug_print(f"Network port offset set to {port_offset}")

def get_python_listen_port():
    return BASE_PYTHON_PORT + port_offset

def get_c_program_port():
    return BASE_C_PORT + port_offset

def send_to_c_program(message):
    """Send a message to the C program using socket"""
    try:
        c_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        c_socket.connect(('127.0.0.1', get_c_program_port()))
        c_socket.sendall(message.encode())
        response = c_socket.recv(1024).decode()
        c_socket.close()
        return response
    except Exception as e:
        debug_print(f"Network error: {e}")  # Use debug_print instead of print
        return None

# Add a test function
def send_test_message(message="TEST_MESSAGE"):
    """Send a test message to the C program"""
    try:
        c_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        c_socket.connect(('127.0.0.1', get_c_program_port()))
        c_socket.sendall(message.encode())
        response = c_socket.recv(1024).decode()
        c_socket.close()
        debug_print(f"Test message sent. Response: {response}")
        return True
    except Exception as e:
        debug_print(f"Error sending test message: {e}")  # Use debug_print
        return False

# Fonction pour écouter les messages UDP
def udp_listener(host, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
            debug_print(f"UDP Listener ready to receive")
            
            while True:
                try:
                    data, addr = udp_socket.recvfrom(1024)  # Recevoir des messages UDP
                    if data:
                        debug_print(f"Message reçu via UDP de {addr}: {data.decode()}")
                except socket.error as e:
                    debug_print("Erreur lors de la réception UDP :", e)  # Use debug_print
                    break  # Sortir de la boucle si une erreur survient

    except Exception as e:
        debug_print("Erreur lors de l'écoute UDP :", e)  # Use debug_print

# Fonction pour écouter les messages TCP
def tcp_listener(sock):
    try:
        while True:
            data = sock.recv(1024)
            if data:
                debug_print("Message reçu via TCP:", data.decode())
            else:
                break  # Sortir de la boucle si la connexion est fermée
    except socket.error as e:
        debug_print("Erreur lors de la réception TCP :", e)  # Use debug_print

def main():
    """Main function for the Python client"""
    parser = argparse.ArgumentParser(description='Python client for game network')
    parser.add_argument('--player', type=int, default=1, help='Player number (1 or 2)')
    parser.add_argument('--port-offset', type=int, default=0, help='Port offset for network communication')
    parser.add_argument('--test-mode', action='store_true', help='Run in test mode with predefined actions')
    args = parser.parse_args()

    set_player_number(args.player)
    set_port_offset(args.port_offset)

    if args.test_mode:
        # Create controllers
        menu_controller = MenuController()
        game_controller = GameController(menu_controller, player_number=args.player)
        
        # Start network
        start_network(game_controller, args)
        
        # Wait a bit
        time.sleep(5)
        
        # Run test actions
        if args.player == 1:
            debug_print("Player 1 executing test moves...")  # Use debug_print
        else:
            debug_print("Player 2 waiting for updates...")  # Use debug_print
        
        # Keep program running
        while True:
            time.sleep(1)
        return

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    python_port = get_python_listen_port()
    server.bind(('0.0.0.0', python_port))
    server.listen(5)
    
    debug_print(f"Python client listening on port {python_port} (Player {player_number})")
    
    # Notify the C program that we're ready (first player only)
    if player_number == 1:
        try:
            response = send_to_c_program(f"PYTHON_READY:{player_number}")
            debug_print(f"C program response: {response}")
        except Exception as e:
            debug_print(f"Error notifying C program: {e}")
    
    # Main listening loop
    try:
        while True:
            client, addr = server.accept()
            debug_print(f"Connection from {addr}")
            
            # Handle the client in a new thread
            client_thread = threading.Thread(target=handle_client, args=(client,))
            client_thread.daemon = True
            client_thread.start()
    except KeyboardInterrupt:
        debug_print("Python client shutting down...")  # Use debug_print
    finally:
        server.close()

def handle_client(client_socket):
    """Handle client connection"""
    try:
        data = client_socket.recv(1024)
        if data:
            message = data.decode()
            debug_print(f"Received: {message[:50]}...")
            
            # Check if this is a game event
            if message.startswith("GAME_EVENT:"):
                success = handle_game_event(message)
                client_socket.sendall(f"EVENT_PROCESSED:{success}".encode())
            else:
                # Handle other message types
                client_socket.sendall("ACK".encode())
    except Exception as e:
        debug_print(f"Error handling client: {e}")  # Use debug_print
    finally:
        client_socket.close()

# Add this new function to handle incoming connections on the TCP server
def tcp_server_listener(server_socket):
    try:
        while True:
            client_socket, client_address = server_socket.accept()
            debug_print(f"Connection from C program at {client_address}")
            
            # Start a new thread to handle this client
            client_thread = threading.Thread(target=handle_c_program_connection, args=(client_socket,))
            client_thread.daemon = True
            client_thread.start()
    except Exception as e:
        print(f"TCP server error: {e}", flush=True)
    finally:
        server_socket.close()

# Add this function to handle each connection from the C program
def handle_c_program_connection(client_socket):
    try:
        data = client_socket.recv(1024)
        if data:
            message = data.decode()
            debug_print(f"Message from C program: {message}")
            
            # Check if this is a game event
            if not handle_game_event(message):
                # Not a game event, use default handling
                # Send acknowledgment back
                client_socket.sendall("Message received by Python client".encode())
            else:
                # It was a game event, send special acknowledgment
                client_socket.sendall("Game event processed".encode())
    except Exception as e:
        print(f"Error handling C program connection: {e}", flush=True)
    finally:
        client_socket.close()

def start_network(controller, args):
    """Initialize network connections for the game"""
    # Register the game controller globally
    set_game_controller(controller)
    
    # Set player number and port offset from args
    set_player_number(args.player)
    set_port_offset(args.port_offset)
    
    # Start TCP server listener in a separate thread
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    python_port = get_python_listen_port()
    server.bind(('0.0.0.0', python_port))
    server.listen(5)
    
    debug_print(f"Python client listening on port {python_port} (Player {args.player})")  # Use debug_print
    
    # Start TCP listener thread
    tcp_thread = threading.Thread(target=tcp_server_listener, args=(server,))
    tcp_thread.daemon = True
    tcp_thread.start()
    
    # Notify the C program that we're ready (first player only)
    if args.player == 1:
        try:
            response = send_to_c_program(f"PYTHON_READY:{args.player}")
            debug_print(f"C program response: {response}")  # Use debug_print
        except Exception as e:
            debug_print(f"Error notifying C program: {e}")  # Use debug_print

def handle_game_event(message):
    """Process a game event received from another player"""
    global game_controller
    
    try:
        # Parse the message format: GAME_EVENT:EVENT_TYPE:JSON_DATA
        parts = message.split(':', 2)
        if len(parts) < 3 or parts[0] != "GAME_EVENT":
            # Not a game event, ignore
            debug_print(f"Not a game event: {message[:50]}...")  # Use debug_print
            return False
            
        event_type = parts[1]
        event_data = json.loads(parts[2])
        
        debug_print(f"Received game event: {event_type}")  # Use debug_print
        debug_print(f"Event data: {event_data}")  # Use debug_print
        
        # If we have a game controller, process the event
        if game_controller:
            processor = GameEventProcessor(game_controller)
            return processor.process_event(event_type, event_data)
        else:
            debug_print("Warning: No game controller registered, cannot process event")  # Use debug_print
            return False
            
    except Exception as e:
        debug_print(f"Error processing game event: {e}")  # Use debug_print
        return False

if __name__ == '__main__':
    main()
