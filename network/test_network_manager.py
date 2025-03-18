from network_manager import NetworkManager, EventType
import time
import uuid

def test_network_manager():
    """Test simple pour vérifier que NetworkManager envoie des données au receive.c"""
    
    # Créer une instance de NetworkManager
    nm = NetworkManager(host="127.0.0.1", port=8080)
    
    # Définir les informations de jeu
    nm.set_game_info(
        game_id=str(uuid.uuid4()),
        player_id="test_player"
    )
    
    # Préparer des données de test (simuler un mouvement d'unité)
    test_data = {
        "entity_id": 12345,
        "entity_type": "Villager",
        "player_name": "Joueur1",
        "coordinates": {
            "x": 10,
            "y": 20
        },
        "target": {
            "x": 15,
            "y": 25
        }
    }
    
    print("Envoi d'un événement de test...")
    
    # Envoyer l'événement
    success = nm.send_event(EventType.UNIT_MOVEMENT, test_data)
    
    if success:
        print("Événement envoyé avec succès")
    else:
        print(" Échec de l'envoi de l'événement")
    
    # Attendre un peu pour s'assurer que le programme C a le temps de traiter
    time.sleep(0.5)
    
    # Fermer la connexion
    nm.close()

if __name__ == "__main__":
    test_network_manager()

