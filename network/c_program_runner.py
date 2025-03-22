import os
import sys
import subprocess
import threading
import time
import signal
import pty

class CNetworkRunner:
    """Runs the C network program with completely controlled output"""
    
    def __init__(self, program_path, port_offset, debug=False):
        self.program_path = program_path
        self.port_offset = port_offset
        self.debug = debug
        self.process = None
        self.running = False
        self.output_thread = None
        self.last_map_output = ""
        self.map_counter = 0
    
    def _filter_and_display_output(self, fd):
        """Read from fd, filter network messages, and display map"""
        buffer = ""
        
        # Network message patterns to filter out
        network_patterns = [
            "Data sent to", 
            "Sent updated game data",
            "Message forwarded to",
            "Broadcast message sent",
            "Received message from",
            "Enter a message to broadcast",
            "Python client acknowledgment",
            "Received IPC command"
        ]
        
        while self.running:
            try:
                # Read from master side of PTY
                data = os.read(fd, 1024)
                if not data:
                    break
                
                text = data.decode('utf-8', errors='replace')
                buffer += text
                
                # Process complete lines
                lines = buffer.split('\n')
                buffer = lines.pop()  # Keep incomplete line in buffer
                
                # Extract map from output (lines with lots of │ and ─ chars)
                map_lines = []
                for line in lines:
                    # Skip network messages
                    if any(pattern in line for pattern in network_patterns):
                        continue
                    
                    # Keep map lines and important messages
                    if '│' in line or '─' in line or len(line.strip()) > 30:
                        map_lines.append(line)
                
                # If we have enough map lines, display them
                if len(map_lines) >= 10:
                    # Clear screen first
                    if not self.debug:
                        os.system('clear')
                    
                    # Print the map
                    for line in map_lines:
                        print(line)
                    
                    # Remember this map
                    self.last_map_output = '\n'.join(map_lines)
                    self.map_counter += 1
                elif len(map_lines) > 0 and self.debug:
                    # In debug mode, show partial output too
                    for line in map_lines:
                        print(line)
                
            except Exception as e:
                if self.debug:
                    print(f"Error reading output: {e}")
                time.sleep(0.1)
    
    def start(self):
        """Start the C program with controlled output"""
        try:
            # Create a pseudoterminal to capture output
            master, slave = pty.openpty()
            
            # Start the C program with PTY as stdout/stderr
            self.process = subprocess.Popen(
                [self.program_path, str(self.port_offset)],
                stdout=slave,
                stderr=slave,
                stdin=subprocess.PIPE,
                preexec_fn=os.setsid  # Run in a new session
            )
            
            # Close slave side in parent process
            os.close(slave)
            
            self.running = True
            
            # Start output processing thread
            self.output_thread = threading.Thread(
                target=self._filter_and_display_output,
                args=(master,)
            )
            self.output_thread.daemon = True
            self.output_thread.start()
            
            return True
        except Exception as e:
            print(f"Failed to start C program: {e}")
            return False
    
    def stop(self):
        """Stop the C program"""
        self.running = False
        
        if self.process:
            try:
                # Try to kill the entire process group
                os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
                self.process.wait(timeout=1)
            except (subprocess.TimeoutExpired, ProcessLookupError):
                try:
                    os.killpg(os.getpgid(self.process.pid), signal.SIGKILL)
                except ProcessLookupError:
                    pass
            finally:
                self.process = None
        
        # Wait for threads to finish
        if self.output_thread and self.output_thread.is_alive():
            self.output_thread.join(1)