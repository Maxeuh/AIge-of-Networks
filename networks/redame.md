# Network Game Communication System

This project implements a communication system for networked games, separating network functionality (in C) from game logic (in Python).

## Files and Functionality

### Core Implementation Files

1. **`ourmain_linux.c`**: C client that handles UDP and TCP/IPC communication
   - Handles broadcasting game data to other clients via UDP
   - Communicates with the local Python game client via TCP/IPC
   - Manages thread synchronization for concurrent communications

2. **`pythoncli.py`**: Python game client
   - Connects to the C client via TCP/IPC
   - Sends game commands to the C client
   - Receives updates from the C client
   - Implements both UDP and TCP listeners

### Testing Files

3. **`test_client.py`**: Basic communication tests
   - Tests UDP broadcast functionality
   - Tests IPC communication between Python and C
   - Provides detailed pass/fail reporting

4. **`full_cycle_test.py`**: End-to-end communication cycle tests
   - Tests sending messages from Python through C and back
   - Verifies message delivery through the complete system

5. **`single_machine_test.py`**: Focused IPC communication tests
   - Tests local communication between Python and C clients
   - Verifies message passing on a single machine

## Compilation and Execution

### Compiling the C Client

```bash
# Compile the C client with threading support
gcc -o ourmain ourmain_linux.c -lpthread

# Run the compiled executable
./ourmain