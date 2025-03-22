import socket
import threading


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
        self.__listening = False
        self.__listener_thread = None
        self.__message_list = []

    def send(self, message: str) -> None:
        """
        Sends a message to the C program that runs the game.
        """
        self.__sock.sendto(message.encode(), self.__address)

    def receive(self) -> list:
        """
        Receives all messages from the list.
        """
        messages = self.__message_list.copy()
        self.__message_list.clear()
        return messages

    def close(self) -> None:
        """
        Closes the socket.
        """
        self.__sock.close()

    def start_listening(self) -> None:
        """
        Starts listening for incoming messages in a separate thread.
        """
        self.__listening = True
        self.__listener_thread = threading.Thread(target=self.__listen)
        self.__listener_thread.start()

    def stop_listening(self) -> None:
        """
        Stops listening for incoming messages.
        """
        self.__listening = False
        if self.__listener_thread:
            self.__listener_thread.join()

    def __listen(self) -> None:
        """
        Listens for incoming messages and processes them.
        """
        while self.__listening:
            message = self.receive_message()
            if message:
                self.__process_message(message)

    def receive_message(self) -> str:
        """
        Receives a single message from the C program that runs the game.
        """
        try:
            data, _ = self.__sock.recvfrom(1024)
            return data.decode()
        except socket.timeout:
            return ""

    def __process_message(self, message: str) -> None:
        """
        Processes the received message by adding it to the list.
        """
        self.__message_list.append(message)
