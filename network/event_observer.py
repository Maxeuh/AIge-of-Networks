from typing import Dict, Any, Callable
from controller.command import Command, Process
from model.player.player import Player
from model.entity import Entity
from network.network_manager import NetworkManager, EventType

class GameEventObserver:
    """
    Observe les événements du jeu et les convertit en événements réseau.
    """
    def __init__(self, network_manager: NetworkManager):
        """
        Initialise l'observateur d'événements.
        
        :param network_manager: Le gestionnaire réseau
        """
        self.network_manager = network_manager
        
    def observe_command(self, command: Command) -> None:
        """
        Observe une commande du jeu et l'envoie sur le réseau si nécessaire.
        
        :param command: La commande exécutée
        """
        process = command.get_process()
        entity = command.get_entity()
        player = command.get_player()
        
        if process == Process.MOVE:
            self._handle_move_command(command)
        elif process == Process.ATTACK:
            self._handle_attack_command(command)
        elif process == Process.SPAWN:
            self._handle_spawn_command(command)
        elif process == Process.BUILD:
            self._handle_build_command(command)
        elif process == Process.COLLECT:
            self._handle_collect_command(command)
        
    def _handle_move_command(self, command: Command) -> None:
        """Traite une commande de mouvement"""
        entity = command.get_entity()
        player = command.get_player()
        
        # Extraction des données pertinentes
        data = {
            "entity_id": id(entity),
            "entity_type": entity.__class__.__name__,
            "player_name": player.get_name(),
            "coordinates": {
                "x": entity.get_coordinate().get_x(),
                "y": entity.get_coordinate().get_y()
            },
            "target": {
                # en fonction de comment MoveCommand stocke la destination
              
            }
        }
        
        # Envoi de l'événement
        self.network_manager.send_event(EventType.UNIT_MOVEMENT, data)
        
    def _handle_attack_command(self, command: Command) -> None:
        """Traite une commande d'attaque"""
       
        pass
    
    def _handle_spawn_command(self, command: Command) -> None:
        """Traite une commande de création d'unité"""
      
        pass
    
    def _handle_build_command(self, command: Command) -> None:
        """Traite une commande de construction"""
  
        pass
    
    def _handle_collect_command(self, command: Command) -> None:
        """Traite une commande de collecte de ressource"""
    
        pass
