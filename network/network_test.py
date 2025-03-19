import socket
import threading
import time
import sys
import select
import os
import signal
import subprocess

class NetworkTester:
    def __init__(self):
        """Initialize the network tester."""
        self.running = False
        self.sender_socket = None
        self.receiver_socket = None
        self.receiver_thread = None
        
        # Configuration
        self.c_sender_ip = "172.20.1.63"
        self.c_sender_port = 8082
        self.receiver_ip = "127.0.0.1"
        self.receiver_port = 8081
        self.buffer_size = 2048
        
        # Statistics
        self.sent_messages = 0
        self.received_messages = 0
        self.start_time = 0
        
    def initialize_sender(self):
        """Initialize the message sender."""
        try:
            self.sender_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            print(f"Sender initialized, targeting {self.c_sender_ip}:{self.c_sender_port}")
            return True
        except Exception as e:
            print(f"Error initializing sender: {e}")
            return False
    
    def initialize_receiver(self):
        """Initialize the message receiver."""
        try:
            self.receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.receiver_socket.bind((self.receiver_ip, self.receiver_port))
            self.receiver_socket.setblocking(False)
            print(f"Receiver listening on {self.receiver_ip}:{self.receiver_port}")
            return True
        except Exception as e:
            print(f"Error initializing receiver: {e}")
            if self.receiver_socket:
                self.receiver_socket.close()
            return False
            
    def start(self):
        """Start the network test."""
        if self.running:
            print("Test is already running")
            return False
            
        if not self.initialize_sender() or not self.initialize_receiver():
            self.stop()
            return False
            
        self.running = True
        self.start_time = time.time()
        
        # Start receiver thread
        self.receiver_thread = threading.Thread(target=self._receiver_loop)
        self.receiver_thread.daemon = True
        self.receiver_thread.start()
        
        print("Network test started")
        return True
        
    def stop(self):
        """Stop the network test."""
        self.running = False
        
        if self.receiver_thread:
            self.receiver_thread.join(timeout=2.0)
            
        if self.sender_socket:
            self.sender_socket.close()
            self.sender_socket = None
            
        if self.receiver_socket:
            self.receiver_socket.close()
            self.receiver_socket = None
            
        # Print final statistics
        self._print_stats()
        print("Network test stopped")
        
    def _receiver_loop(self):
        """Thread function for receiving messages."""
        while self.running:
            try:
                ready = select.select([self.receiver_socket], [], [], 0.5)
                if ready[0]:
                    data, addr = self.receiver_socket.recvfrom(self.buffer_size)
                    message = data.decode('ascii')
                    self.received_messages += 1
                    
                    print(f"\nMessage received from {addr[0]}:{addr[1]}")
                    print(f"Content: {message}")
                    self._parse_message(message)
                    
                    # Print stats every 5 messages
                    if self.received_messages % 5 == 0:
                        self._print_stats()
            except Exception as e:
                print(f"Error in receiver: {e}")
                time.sleep(0.1)
    
    def _parse_message(self, message):
        """Parse and display a received message."""
        if not message or ":" not in message:
            print(f"Unknown format: {message}")
            return
            
        parts = message.split(":")
        msg_type = parts[0]
        
        try:
            if msg_type == "POS" and len(parts) >= 4:
                print(f"Position update: {parts[1]} at ({parts[2]}, {parts[3]})")
            elif msg_type == "ACT" and len(parts) >= 3:
                print(f"Action: {parts[1]} performs {parts[2]}")
            elif msg_type == "EVT" and len(parts) >= 2:
                print(f"Event: {parts[1]} with params {parts[2:] if len(parts) > 2 else []}")
            else:
                print(f"Custom message or unknown format: {message}")
        except Exception as e:
            print(f"Error parsing message: {e}")
    
    def _print_stats(self):
        """Print network test statistics."""
        elapsed = time.time() - self.start_time
        if elapsed > 0:
            print("\n--- Network Statistics ---")
            print(f"Runtime: {elapsed:.1f} seconds")
            print(f"Messages sent: {self.sent_messages}")
            print(f"Messages received: {self.received_messages}")
            print(f"Send rate: {self.sent_messages/elapsed:.2f} msgs/sec")
            print(f"Receive rate: {self.received_messages/elapsed:.2f} msgs/sec")
            print(f"Success rate: {(self.received_messages/max(1, self.sent_messages))*100:.1f}%")
            print("------------------------")
    
    def send_message(self, message):
        """Send a message to the C broadcaster."""
        if not self.running or not self.sender_socket:
            print("Cannot send: test not running")
            return False
            
        try:
            self.sender_socket.sendto(message.encode('ascii'), (self.c_sender_ip, self.c_sender_port))
            self.sent_messages += 1
            print(f"Sent [{self.sent_messages}]: {message}")
            return True
        except Exception as e:
            print(f"Error sending message: {e}")
            return False
    
    def run_automated_test(self, message_count=5, delay=1.0):
        """Run an automated test with predefined messages."""
        if not self.running:
            print("Test not running")
            return
            
        test_messages = [
            "POS:player1:100:200", 
            "ACT:player2:attack",
            "EVT:score:player1:50",
            "POS:enemy1:500:300",
            "EVT:gameover:player2:win",
            "CUSTOM:This is a test message with special chars: !@#$%^"
        ]
        
        print(f"\nRunning automated test with {message_count} messages")
        for i in range(message_count):
            msg_index = i % len(test_messages)
            self.send_message(test_messages[msg_index])
            time.sleep(delay)
            
        print("Automated test completed")
    
    def run_interactive_mode(self):
        """Run an interactive test mode."""
        print("\nInteractive test mode")
        print("Enter messages to send (or commands)")
        print("Commands: stats, auto, exit")
        
        try:
            while self.running:
                user_input = input("> ")
                command = user_input.lower()
                
                if command == "exit":
                    break
                elif command == "stats":
                    self._print_stats()
                elif command == "auto":
                    count = int(input("Number of messages: ") or "5")
                    delay = float(input("Delay between messages (seconds): ") or "1.0")
                    self.run_automated_test(count, delay)
                else:
                    self.send_message(user_input)
        except KeyboardInterrupt:
            print("\nInteractive mode terminated")

def is_process_running(process_name):
    """Check if a process is running by name."""
    try:
        output = subprocess.check_output(["pgrep", "-f", process_name])
        return len(output.strip()) > 0
    except:
        return False

def main():
    """Run the network test."""
    print("UDP Network Communication Test")
    
    # Check if required C programs are running
    if not is_process_running("./receive"):
        print("Warning: 'receive' program doesn't appear to be running")
        print("Run './receive' in another terminal first")
    
    if not is_process_running("./broadcast_sender"):
        print("Warning: 'broadcast_sender' program doesn't appear to be running")
        print("Run './broadcast_sender' in another terminal first")
        
    response = input("Continue anyway? (y/n): ").lower()
    if response != 'y':
        print("Test aborted.")
        return
        
    # Initialize and run the test
    tester = NetworkTester()
    
    if not tester.start():
        print("Failed to start network test. Exiting.")
        return
        
    try:
        if len(sys.argv) > 1 and sys.argv[1] == "--auto":
            count = 10
            if len(sys.argv) > 2:
                try:
                    count = int(sys.argv[2])
                except:
                    pass
            tester.run_automated_test(count)
        else:
            tester.run_interactive_mode()
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
    finally:
        tester.stop()

if __name__ == "__main__":
    main()