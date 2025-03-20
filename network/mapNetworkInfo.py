import json
import os
import sys
from typing import Dict, Any, List

# Ajouter le dossier parent au chemin de recherche des modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from controller.game_controller import GameController
from util.coordinate import Coordinate
from model.game_object import GameObject

class MapNetworkInfo:
    """Classe pour gérer les informations réseau de la carte de jeu."""
    
    def extract_map_info(game_controller) -> Dict[str, Any]:
        """Extrait toutes les informations de la carte et les objets présents."""
        map_obj = game_controller.get_map()
        print(map_obj)
        map_size = map_obj.get_size()
        print(map_size)
        # Structure pour stocker les informations
        map_info = {
            "map_size": map_size,
            "objects": []
        }
        
        # Récupération des joueurs
        players = game_controller.get_players()
        map_info["players"] = [
            {
                "name": player.get_name(),
                "color": player.get_color(),
                "id": i
            }
            for i, player in enumerate(players)
        ]
        
        # Parcours de la carte pour récupérer tous les objets
        for coordinate, obj in map_obj.get_map().items():
            if obj is not None:
                # Trouver le propriétaire de l'objet, s'il existe
                owner_id = None
                for i, player in enumerate(players):
                    if obj in player.get_units() or obj in player.get_buildings():
                        owner_id = i
                        break
                
                # Ajouter les informations de l'objet
                object_info = {
                    "id": id(obj),  # Identifiant unique
                    "type": obj.__class__.__name__,
                    "name": obj.get_name(),
                    "x": coordinate.get_x(),
                    "y": coordinate.get_y(),
                    "size": obj.get_size() if hasattr(obj, "get_size") else 1,
                    "owner_id": owner_id
                }
                
                map_info["objects"].append(object_info)
        
        return map_info
    
    @staticmethod
    def save_map_info(game_controller, filename="map_info.json") -> None:
        """Sauvegarde les informations de la carte dans un fichier JSON."""
        map_info = MapNetworkInfo.extract_map_info(game_controller)
        
        # Chemin vers le dossier network
        network_dir = os.path.dirname(os.path.abspath(__file__))
        filepath = os.path.join(network_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(map_info, f, indent=2)
        
        print(f"Informations de la carte sauvegardées dans {filepath}")








