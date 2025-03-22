# Documentation du fonctionnement réseau du jeu RTS

Ce document décrit le processus d'initialisation et d'échange des données réseau du jeu RTS, notamment la façon dont les informations de la carte et les commandes exécutées pendant la partie sont transmises via TCP.

## Initialisation du réseau

- Lors du lancement du jeu, la méthode `start_game()` est appelée. Celle-ci instancie un objet `GameController`.
- Le constructeur de `GameController` instancie à son tour un objet `NetworkController`. Ce contrôleur réseau établit immédiatement un socket TCP en écoute sur le port **9090** pour accepter les connexions entrantes.

## Boucle de jeu (Game Loop)

- Une fois le réseau configuré, le jeu appelle la méthode `game_loop()` (ligne 61 dans `GameController`).

### Envoi des données initiales

- La `game_loop()` appelle la méthode `start()`, qui déclenche la méthode `send_initial_map_data()` (ligne 479).
- `send_initial_map_data()` extrait toutes les informations nécessaires sur la carte actuelle du jeu, y compris les détails des objets présents, et les envoie immédiatement via le réseau au client distant connecté au socket.

### Mise à jour en temps réel

- Après avoir envoyé les données initiales, la boucle principale continue et appelle la méthode `update()`.
- La méthode `update()` exécute les commandes (actions des joueurs, mouvements d'unités, etc.). Chaque commande exécutée génère des données spécifiques qui sont immédiatement envoyées au réseau en utilisant la méthode `send_network()` du `NetworkController`.
- Ainsi, chaque changement d'état dans le jeu est transmis au client distant en temps réel via le réseau TCP.

## Flux récapitulatif

Voici un résumé clair du flux d'informations réseau :

```
start_game()
    └──> GameController()
          └──> NetworkController()  ──── Écoute sur TCP:9090

GameController.game_loop()
    └──> start()
          └──> send_initial_map_data() ──── Envoi initial map + objets

    └──> update()
          └──> execute_commands()
                └──> send_network() ──── Envoi en temps réel des commandes exécutées
```

Ce fonctionnement assure la synchronisation continue et en temps réel des données du jeu entre les clients.

