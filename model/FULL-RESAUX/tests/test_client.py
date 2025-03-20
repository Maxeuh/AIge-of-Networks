import socket
import threading
import time
import sys

# Configuration
UDP_PORT = 23456
IPC_PORT = 12347
SERVER_IP = "127.0.0.1"  # Local server
BROADCAST_IP = "172.20.15.255"  # Your broadcast address

class TestResult:
    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        
    def log_test(self, name, passed, message=""):
        self.tests_run += 1
        result = "✅ PASSED" if passed else "❌ FAILED"
        if passed:
            self.tests_passed += 1
        
        print(f"Test {self.tests_run}: {name} - {result}")
        if message:
            print(f"   {message}")
            
    def summary(self):
        print(f"\n--- Test Summary: {self.tests_passed}/{self.tests_run} tests passed ---")
        return self.tests_passed == self.tests_run

# Global test results
results = TestResult()

# UDP listener thread
def udp_listener():
    """Listen for UDP broadcasts from the server"""
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    udp_socket.bind(('', UDP_PORT))
    
    print("UDP listener started, waiting for messages...")
    
    # Set a timeout so the thread can exit
    udp_socket.settimeout(15)
    
    try:
        while True:
            try:
                data, addr = udp_socket.recvfrom(1024)
                message = data.decode('utf-8')
                print(f"UDP received: {message} from {addr}")
                
                # Record receipt of periodic update message
                if "Update message for all clients" in message:
                    results.log_test("Periodic Update Message", True, 
                                    f"Received update message: {message}")
            except socket.timeout:
                break
    except Exception as e:
        print(f"Error in UDP listener: {e}")
    finally:
        udp_socket.close()
        
def test_udp_broadcast():
    """Test sending UDP broadcast messages"""
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    
    try:
        test_message = "Test broadcast message from Python client"
        udp_socket.sendto(test_message.encode('utf-8'), (BROADCAST_IP, UDP_PORT))
        results.log_test("UDP Broadcast Send", True, 
                        f"Sent broadcast message to {BROADCAST_IP}:{UDP_PORT}")
        time.sleep(0.5)  # Wait for message to be processed
    except Exception as e:
        results.log_test("UDP Broadcast Send", False, f"Error: {e}")
    finally:
        udp_socket.close()

def test_game_data_send():
    """Test sending game data"""
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    try:
        # Create a message that looks like GameData struct
        game_message = "Game data message from Python client"
        udp_socket.sendto(game_message.encode('utf-8'), (SERVER_IP, UDP_PORT))
        results.log_test("Game Data Send", True, 
                        f"Sent game data message to {SERVER_IP}:{UDP_PORT}")
        time.sleep(0.5)  # Wait for message to be processed
    except Exception as e:
        results.log_test("Game Data Send", False, f"Error: {e}")
    finally:
        udp_socket.close()

def test_ipc_communication():
    """Test IPC communication with the C server"""
    try:
        # Create TCP socket for IPC
        ipc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ipc_socket.connect((SERVER_IP, IPC_PORT))
        
        # Send command
        test_command = "TEST_COMMAND:param1,param2"
        ipc_socket.send(test_command.encode('utf-8'))
        
        # Receive response with timeout
        ipc_socket.settimeout(2)
        response = ipc_socket.recv(1024).decode('utf-8')
        
        if response:
            results.log_test("IPC Communication", True, 
                          f"Sent: '{test_command}', Received: '{response}'")
        else:
            results.log_test("IPC Communication", False, "No response received")
            
    except Exception as e:
        results.log_test("IPC Communication", False, f"Error: {e}")
    finally:
        ipc_socket.close()

def main():
    # Start UDP listener in a separate thread
    udp_thread = threading.Thread(target=udp_listener)
    udp_thread.daemon = True
    udp_thread.start()
    
    # Give UDP listener time to start
    time.sleep(1)
    
    # Run tests
    test_udp_broadcast()
    test_game_data_send()
    test_ipc_communication()
    
    # Wait for UDP listener to receive messages
    udp_thread.join(10)
    
    # Print test summary
    if results.summary():
        print("All tests passed successfully.")
    else:
        print("Some tests failed.")

if __name__ == "__main__":
    main()