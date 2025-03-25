import socket
import subprocess
import os
import atexit
import json


class NetworkController:
    """
    The goal of this class is to provide a way to interact with the other
    players on the network, by sending and receiving messages.
    This class sends messages locally to the C program that runs with the
    game, and receives messages from it, using UDP sockets.
    Port 9090 is used for sending messages, and port 9092 is used for
    receiving messages.
    """

    def __init__(self) -> None:
        self.__send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__send_address = ("127.0.0.1", 9090)
        self.__recv_address = ("127.0.0.1", 9092)
        if os.name != "nt":
            self.__send_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            self.__recv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.__recv_sock.bind(self.__recv_address)
        self.__recv_sock.settimeout(0.05)
        self.__network_bridge_process = None
        self.__bridge_exists = True

        # Démarrer le pont réseau
        self.__start_network_bridge()

        # S'assurer que le pont réseau est arrêté quand le programme termine
        atexit.register(self.__stop_network_bridge)

    def __start_network_bridge(self) -> None:
        """
        Démarre le programme C qui fait office de pont réseau.
        """
        try:
            # Chemin vers l'exécutable du pont réseau
            bridge_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "network_bridge.exe" if os.name == "nt" else "network_bridge",
            )
            if not os.path.isfile(bridge_path):
                self.__bridge_exists = False
                subprocess.run(
                    ["make", "network_bridge"],
                    cwd=os.path.dirname(os.path.dirname(__file__)),
                )
            # Démarre le programme C du pont réseau avec le flag --run pour la transmission et --no-debug pour enlever les logs
            self.__network_bridge_process = subprocess.Popen(
                [bridge_path, "--run", "--no-debug"]
            )
        except Exception as e:
            self.__network_bridge_process = None
            raise e

    def __stop_network_bridge(self) -> None:
        """
        Arrête le programme C du pont réseau.
        """
        if self.__network_bridge_process is not None:
            try:
                self.__network_bridge_process.terminate()
                self.__network_bridge_process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.__network_bridge_process.kill()
            except Exception as e:
                raise e
            finally:
                self.__network_bridge_process = None
                if not self.__bridge_exists:
                    subprocess.run(
                        ["make", "clean_bridge"],
                        cwd=os.path.dirname(os.path.dirname(__file__)),
                    )

    def send(self, message: str) -> None:
        """
        Sends a message to the C program that runs the game.
        """
        self.__send_sock.sendto(json.dumps(message).encode(), self.__send_address)

    def receive(self) -> list:
        """
        Récupère tous les messages disponibles dans la file du socket.
        """
        messages = []
        # Lire tous les messages disponibles jusqu'à ce que la file soit vide
        while True:
            try:
                data, _ = self.__recv_sock.recvfrom(65507)
                if not data:
                    break
                message_str = data.decode()
                try:
                    message = json.loads(message_str)
                    messages.append(message)
                except json.JSONDecodeError as e:
                    raise e
            except socket.timeout:
                # Plus de messages disponibles, on sort de la boucle
                break
            except ConnectionResetError:
                # Erreur de connexion, on sort de la boucle
                break

        return messages

    def close(self) -> None:
        """
        Closes the socket and stops the network bridge.
        """
        self.__stop_network_bridge()
        self.__recv_sock.close()
        self.__send_sock.close()
