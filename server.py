import socket

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(("", 9090))

print("Server is running...")

while True:
    message, address = server_socket.recvfrom(1024)
    print(f"Received {message} from {address}")
