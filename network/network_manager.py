import socket 
import json
import threading
from typing import Dict, Any, Callable, Optional
from enum import Enum

class EventType(Enum):
    """Types d'événements réseau possibles dans le jeu"""
    UNIT_MOVEMENT = 0
    UNIT_ATTACK = 1
    UNIT_CREATION = 2
    BUILDING_CONSTRUCTION = 3
    RESOURCE_COLLECTION = 4
    GAME_STATE_UPDATE = 5
   
    
class NetworkManager:
    """Gestionnaire réseau qui detecte les événements du jeu et les envoie au relai.c
    """
    def __init__(self,host: str = "127.0.0.1",port: int =8080):
        """initaliser le gestionnaire réseau 
         :param host : adresse IP du relai C local
         :param port: Port du relais C local
         
        """
        self.socket =socket.socket(socket.AF_INET,socket.SOCK_DGRAM) 
        self.relay_address=(host,port)
        self.event_handlers={}
        self.game_id=None
        self.player_id=None
    
    def send_event(self, event_type: EventType, data: Dict[str, Any]) -> bool:
        """Envoie des données d'un evenement specifique au relai C 
        :param event_type: Type d'événement
        :param data: Données associées à l'événement
        :return: True si l'envoi a réussi       
        """
        message = {
            "event_type": event_type.value,
            "game_id": self.game_id,
            "player_id": self.player_id,
            "data": data
        }
        try:
            #conversion du message en json et l'envoyer vers le relai 
            serialized = json.dumps(message).encode('utf-8')
            self.socket.sendto(serialized, self.relay_address)
            return True
        except Exception as e:
            print(f"Erreur d'envoi: {e}")
            return False       
    
    def set_game_info(self, game_id: str, player_id: str) -> None:
        """
        Définit les identifiants du jeu et du joueur.
        
        :param game_id: Identifiant unique de la partie
        :param player_id: Identifiant unique du joueur local
        """
        self.game_id = game_id
        self.player_id = player_id
        
    def close(self) -> None:
        """Ferme la connexion socket."""
        self.socket.close()
    
        