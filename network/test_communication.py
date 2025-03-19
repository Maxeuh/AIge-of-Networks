import subprocess
import time
import os
import signal
import sys
from send import send_message_to_c

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def compile_c_program():
    """Compile the C receiver program if it's not already compiled"""
    receive_c_path = os.path.join(SCRIPT_DIR, 'receive.c')
    receiver_path = os.path.join(SCRIPT_DIR, 'receiver')
    
    if not os.path.exists(receive_c_path):
        print(f"Error: C source file not found at {receive_c_path}")
        sys.exit(1)
        
    if not os.path.exists(receiver_path):
        print("Compiling C receiver program...")
        result = subprocess.run(['gcc', receive_c_path, '-o', receiver_path], 
                                capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Compilation failed: {result.stderr}")
            sys.exit(1)
        print("Compilation successful")
    else:
        print("C receiver program already compiled")
    
    return receiver_path

def run_tests(receiver_path):
    """Run communication tests between Python sender and C receiver"""
    # Start the C receiver program
    print("Starting C receiver program...")
    c_process = subprocess.Popen([receiver_path], stdout=subprocess.PIPE, 
                                text=True, bufsize=1, universal_newlines=True)
    
    # Give the C program time to start and bind to the port
    time.sleep(1)
    
    # Test messages
    test_messages = [
        "Hello from Python!",
        "Testing UDP communication",
        "1234567890",
        "Special chars: !@#$%^&*()",
        "This is the final test message"
    ]
    
    print("\n--- Starting Communication Tests ---\n")
    
    # Send each test message
    for i, message in enumerate(test_messages):
        print(f"\nTest {i+1}/{len(test_messages)}")
        success = send_message_to_c(message)
        
        if success:
            print("Message sent successfully")
        else:
            print(" Failed to send message")
        
        # Give time for C program to process and print the received message
        time.sleep(0.5)
        
    print("\n--- Tests Completed ---\n")
    
    # Allow time to see the last message output from the C program
    time.sleep(1)
    
    # Terminate the C receiver
    print("Terminating C receiver program...")
    c_process.send_signal(signal.SIGINT)
    c_process.wait(timeout=2)
    
    print("\nTest run complete!")

if __name__ == "__main__":
    print("=== UDP Communication Test ===")
    receiver_path = compile_c_program()
    run_tests(receiver_path)
