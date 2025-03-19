import socket
import threading
import time
import sys
import select
import os
import uuid
import datetime

class EndToEndTester:
    def __init__(self):
        """Initialize the end-to-end network tester."""
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
        
        # Tracking
        self.sent_messages = {}  # message_id -> timestamp
        self.received_messages = {}  # message_id -> timestamp
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
        
        print("End-to-end network test started")
        print("This test will verify the complete communication loop:")
        print("Python → C Broadcaster → Network → C Receiver → Python")
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
        print("End-to-end test stopped")
        
    def _receiver_loop(self):
        """Thread function for receiving messages."""
        while self.running:
            try:
                ready = select.select([self.receiver_socket], [], [], 0.5)
                if ready[0]:
                    data, addr = self.receiver_socket.recvfrom(self.buffer_size)
                    message = data.decode('ascii')
                    
                    # Try to extract message ID
                    msg_id = self._extract_id(message)
                    if msg_id:
                        now = time.time()
                        self.received_messages[msg_id] = now
                        
                        # Calculate round-trip time if we sent this message
                        rtt = None
                        if msg_id in self.sent_messages:
                            rtt = now - self.sent_messages[msg_id]
                            
                        print(f"\n✅ COMPLETE CYCLE VERIFIED - ID: {msg_id}")
                        print(f"Message arrived back to Python receiver after full loop!")
                        if rtt:
                            print(f"Round-trip time: {rtt*1000:.2f} ms")
                    
                    print(f"Received from {addr[0]}:{addr[1]}: {message}")
                    self._parse_message(message)
                    
                    # Print stats periodically
                    if len(self.received_messages) % 5 == 0:
                        self._print_stats()
                        
            except Exception as e:
                print(f"Error in receiver: {e}")
                time.sleep(0.1)
    
    def _extract_id(self, message):
        """Extract message ID from a message."""
        try:
            if "ID:" in message:
                parts = message.split("ID:")
                if len(parts) > 1:
                    id_part = parts[1].split(":", 1)[0]
                    return id_part
        except:
            pass
        return None
    
    def _parse_message(self, message):
        """Parse and display a received message."""
        if not message or ":" not in message:
            print(f"Unknown format: {message}")
            return
            
        # Skip ID part for display purposes
        display_msg = message
        if "ID:" in message:
            display_msg = message.split("ID:", 1)[0]
            
        parts = display_msg.split(":")
        msg_type = parts[0]
        
        try:
            if msg_type == "POS" and len(parts) >= 4:
                print(f"Position update: {parts[1]} at ({parts[2]}, {parts[3]})")
            elif msg_type == "ACT" and len(parts) >= 3:
                print(f"Action: {parts[1]} performs {parts[2]}")
            elif msg_type == "EVT" and len(parts) >= 2:
                print(f"Event: {parts[1]} with params {parts[2:] if len(parts) > 2 else []}")
            else:
                print(f"Custom message or unknown format: {display_msg}")
        except Exception as e:
            print(f"Error parsing message: {e}")
    
    def _print_stats(self):
        """Print network test statistics."""
        elapsed = time.time() - self.start_time
        sent_count = len(self.sent_messages)
        received_count = len(self.received_messages)
        
        if elapsed > 0:
            print("\n--- End-to-End Test Statistics ---")
            print(f"Runtime: {elapsed:.1f} seconds")
            print(f"Messages sent: {sent_count}")
            print(f"Messages received: {received_count}")
            print(f"Success rate: {(received_count/max(1, sent_count))*100:.1f}%")
            
            # Calculate RTT statistics for messages that completed the cycle
            rtts = []
            for msg_id, sent_time in self.sent_messages.items():
                if msg_id in self.received_messages:
                    rtts.append((self.received_messages[msg_id] - sent_time) * 1000)  # ms
            
            if rtts:
                print(f"Average RTT: {sum(rtts)/len(rtts):.2f} ms")
                print(f"Min RTT: {min(rtts):.2f} ms")
                print(f"Max RTT: {max(rtts):.2f} ms")
            
            print("-----------------------------------")
    
    def send_message(self, message):
        """Send a message with an ID through the full communication loop."""
        if not self.running or not self.sender_socket:
            print("Cannot send: test not running")
            return False
            
        # Add unique ID to track the message through the system
        msg_id = str(uuid.uuid4())[:8]  # Short UUID
        tagged_message = f"{message}:ID:{msg_id}"
        
        try:
            self.sender_socket.sendto(tagged_message.encode('ascii'), 
                                     (self.c_sender_ip, self.c_sender_port))
            now = time.time()
            self.sent_messages[msg_id] = now
            print(f"Sent message with ID {msg_id}: {message}")
            print(f"Waiting to confirm receipt through the complete communication loop...")
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
            "CUSTOM:This is a test message"
        ]
        
        print(f"\nRunning end-to-end test with {message_count} messages")
        print("Each message will be tracked through the complete system")
        
        for i in range(message_count):
            msg_index = i % len(test_messages)
            self.send_message(test_messages[msg_index])
            time.sleep(delay)
            
        print("Test messages sent. Waiting for confirmation...")
        # Wait for all messages to complete the loop or timeout
        wait_time = min(message_count * delay * 2, 30)  # Wait up to 30 seconds
        time.sleep(wait_time)
        
        print("\nEnd-to-end test summary:")
        sent_ids = set(self.sent_messages.keys())
        received_ids = set(self.received_messages.keys())
        completed_ids = sent_ids.intersection(received_ids)
        
        print(f"Messages sent: {len(sent_ids)}")
        print(f"Messages that completed full loop: {len(completed_ids)}")
        print(f"Success rate: {len(completed_ids)/max(1, len(sent_ids))*100:.1f}%")
        
        if len(completed_ids) != len(sent_ids):
            print("⚠️ Some messages did not complete the full communication loop!")
            print("This may indicate an issue in the network stack.")
        else:
            print("✅ All messages successfully completed the full communication loop!")
            print("The entire Python → C → Network → C → Python path is working correctly.")
    
    def run_interactive_mode(self):
        """Run an interactive test mode."""
        print("\nEnd-to-End Test Interactive Mode")
        print("Enter messages to send (or commands)")
        print("Commands: stats, auto, exit")
        print("Each message will be tracked through the complete communication loop")
        
        try:
            while self.running:
                user_input = input("> ")
                command = user_input.lower()
                
                if command == "exit":
                    break
                elif command == "stats":
                    self._print_stats()
                elif command == "auto":
                    count = input("Number of messages: ")
                    count = int(count) if count else 5
                    delay = input("Delay between messages (seconds): ")
                    delay = float(delay) if delay else 1.0
                    self.run_automated_test(count, delay)
                else:
                    self.send_message(user_input)
        except KeyboardInterrupt:
            print("\nInteractive mode terminated")

def main():
    """Run the end-to-end network test."""
    print("UDP End-to-End Communication Test")
    print("This test verifies the complete communication cycle:")
    print("Python → C Broadcaster → Network → C Receiver → Python")
    print("\nWarning: Both C programs must be running:")
    print("- ./receive (listens on port 8080)")
    print("- ./broadcast_sender (listens on port 8082)\n")
    
    response = input("Ready to start the test? (y/n): ").lower()
    if response != 'y':
        print("Test aborted.")
        return
        
    # Initialize and run the test
    tester = EndToEndTester()
    
    if not tester.start():
        print("Failed to start end-to-end test. Exiting.")
        return
        
    try:
        if len(sys.argv) > 1 and sys.argv[1] == "--auto":
            count = 5  # default
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