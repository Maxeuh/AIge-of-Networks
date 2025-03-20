import socket
import threading
import time
import sys
import random

# Configuration
UDP_PORT = 23456
IPC_PORT = 12347
LOCAL_IP = "127.0.0.1"  # For local testing
BROADCAST_IP = "172.20.15.255"  # Your broadcast address

# Track received messages for verification
received_messages = []
message_lock = threading.Lock()

def udp_listener():
    """Listen for UDP broadcasts that would come from another C client"""
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    # Try to bind to the UDP port - it might fail if C client is already bound
    try:
        udp_socket.bind(('', UDP_PORT))
        print("UDP listener started successfully")
    except OSError:
        print("Could not bind to UDP port - will listen through IPC instead")
        return
    
    print(f"Game client listening for broadcasts on UDP port {UDP_PORT}")
    
    while True:
        try:
            data, addr = udp_socket.recvfrom(1024)
            message = data.decode('utf-8')
            print(f"[GAME] Received broadcast: {message} from {addr}")
            
            with message_lock:
                received_messages.append(message)
                
        except Exception as e:
            print(f"Error in UDP listener: {e}")
            break
            
    udp_socket.close()

def ipc_listener():
    """Listen for messages from our C client via IPC"""
    try:
        # Create TCP server socket for receiving from C
        ipc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ipc_socket.bind((LOCAL_IP, IPC_PORT+1))  # Use IPC_PORT+1 to avoid conflict
        ipc_socket.listen(1)
        
        print(f"Waiting for C client to connect for game updates on port {IPC_PORT+1}")
        conn, addr = ipc_socket.accept()
        print(f"C client connected from {addr}")
        
        while True:
            data = conn.recv(1024)
            if not data:
                break
                
            message = data.decode('utf-8')
            print(f"[GAME] Received via IPC: {message}")
            
            with message_lock:
                received_messages.append(message)
                
            # Send acknowledgment
            conn.send("Received by game client".encode('utf-8'))
            
    except Exception as e:
        print(f"Error in IPC listener: {e}")
    finally:
        ipc_socket.close()

def send_game_commands():
    """Send game commands to C client via IPC"""
    try:
        # Connect to C client's IPC port
        ipc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ipc_socket.connect((LOCAL_IP, IPC_PORT))
        
        # Generate unique identifiers for our test messages
        test_id = random.randint(1000, 9999)
        
        for i in range(5):
            # Create a test message with ID so we can track it
            command = f"GAME_UPDATE:{test_id}:Player moved to coordinates X={i*10},Y={i*5}"
            print(f"[GAME] Sending command: {command}")
            
            ipc_socket.send(command.encode('utf-8'))
            
            # Wait for acknowledgment
            response = ipc_socket.recv(1024).decode('utf-8')
            print(f"[GAME] C client response: {response}")
            
            # Wait to see if our message comes back through broadcast
            time.sleep(3)
            
            # Check if our message was received back 
            with message_lock:
                found = False
                for msg in received_messages:
                    if str(test_id) in msg:
                        print(f"✅ FULL CYCLE VERIFIED: Message with ID {test_id} completed the full cycle!")
                        found = True
                        break
                
                if not found:
                    print(f"❌ Message with ID {test_id} did not complete the full cycle")
            
            time.sleep(2)
            
    except Exception as e:
        print(f"Error sending game commands: {e}")
    finally:
        ipc_socket.close()

def main():
    # Start UDP listener in a separate thread
    udp_thread = threading.Thread(target=udp_listener)
    udp_thread.daemon = True
    udp_thread.start()
    
    # Start IPC listener in a separate thread
    ipc_thread = threading.Thread(target=ipc_listener)
    ipc_thread.daemon = True
    ipc_thread.start()
    
    # Give time for listeners to start
    time.sleep(2)
    
    # Send game commands
    send_game_commands()
    
    # Keep main thread alive
    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()