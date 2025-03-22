import typing

from model.ai import AI

if typing.TYPE_CHECKING:
    from controller.game_controller import GameController
    from model.player.strategies.strategy import Strategy

from pygame import time

from model.player.player import Player


class AIController:
    """This module is responsible for controlling the AI."""

    def __init__(self, game_controller: "GameController", refresh_rate: int) -> None:
        """
        Initializes the AIController with the given game controller.

        :param game_controller: The game controller.
        :type game_controller: GameController
        """
        self.__game_controller: "GameController" = game_controller
        self.__players: list[Player] = self.__game_controller.get_players()
        self.__refresh_rate: int = refresh_rate
        self.__running = True
        #for player in self.__players:
           # player.set_ai(AI(player, None, self.__game_controller.get_map().capture()))

    def exit(self) -> None:
        """
        Exits the AIController.
        """
        self.__running = False
        exit(0)

    def update_knowledge(self) -> None:
        """
        Updates the known map of the player.

        :param player: The player.
        :type player: Player
        """
        for player in self.__players:
            player.update_centre_coordinate()
        for player in self.__players:
            player.get_ai().set_map_known(self.__game_controller.get_map().capture())
            player.get_ai().update_enemies(
                [enemy.capture() for enemy in self.__players if enemy != player]
            )

    def ai_loop(self) -> None:
        """
        The main loop of the AIController.
        """
        while self.__running:
            ##print("AI loop")
            for player in self.__players:
                self.update_knowledge()
            for player in self.__players:
                try:
                    player.get_ai().get_strategy().execute()
                except (ValueError, IndexError, AttributeError):
                    pass
            if self.__game_controller.get_speed() != 0:
                time.wait(
                    1000 * self.__refresh_rate // self.__game_controller.get_speed()
                )

    def pause(self) -> None:
        """
        Pauses the AIController.
        """
        self.__running = False

    def resume(self) -> None:
        """
        Resumes the AIController.
        """
        self.__running = True

    def load(self, game_controller: "GameController") -> None:
        """
        Loads the AIController.
        """
        self.__game_controller = game_controller
        self.__players = self.__game_controller.get_players()
