import socket


class NetworkController:
    """
    The goal of this class is to provide a way to interact with the other
    players on the network, by sending and receiving messages.
    This class sends messages locally to the C program that runs with the
    game, and receives messages from it, using UDP sockets and the port 9090.
    """

    def __init__(self) -> None:
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__address = ("127.0.0.1", 9090)
        self.__sock.settimeout(1.0)

    def send(self, message: str) -> None:
        """
        Sends a message to the C program that runs the game.
        """
        self.__sock.sendto(message.encode(), self.__address)

    def receive(self) -> str:
        """
        Receives a message from the C program that runs the game.
        """
        try:
            data, _ = self.__sock.recvfrom(1024)
            return data.decode()
        except socket.timeout:
            return ""

    def close(self) -> None:
        """
        Closes the socket.
        """
        self.__sock.close()
