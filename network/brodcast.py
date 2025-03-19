import socket

UDP_IP = "127.0.0.1"
UDP_PORT = 9090
BUFFER_SIZE = 1024

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print(f"Python en attente sur port {UDP_PORT}")

while True:
    data, addr = sock.recvfrom(BUFFER_SIZE)
    print(f"Reçu: {data.decode()}")