from model.player.player import Player
from model.player.strategies.strategy import Strategy
from util.map import Map


class AI:
    """This module is responsible for controlling the AI."""

    def __init__(self, player: Player, strategy: "Strategy", game_map: Map) -> None:
        """
        Initializes the AI with the given player.

        :param player: The player.
        :type player: Player
        """
        self.__player: Player = player
        self.__strategy: "Strategy" = strategy
        self.__map_known: Map = game_map
        self.__enemies: list[Player] = []

    def update_enemies(self, enemies: list[Player]) -> None:
        """
        Updates the enemies of the AI.

        :param enemies: The enemies.
        :type enemies: list[Player]
        """
        self.__enemies = enemies

    def get_enemies(self) -> list[Player]:
        """
        Returns the enemies.

        :return: The enemies.
        :rtype: list[Player]
        """
        return self.__enemies

    def get_player(self) -> Player:
        """
        Returns the player.

        :return: The player.
        :rtype: Player
        """
        return self.__player

    def get_strategy(self) -> "Strategy":
        """
        Returns the strategy.

        :return: The strategy.
        :rtype: Strategy
        """
        return self.__strategy

    def get_map_known(self) -> Map:
        """
        Returns the map.

        :return: The map.
        :rtype: Map
        """
        return self.__map_known

    def set_player(self, player: Player) -> None:
        """
        Sets the player.

        :param player: The player.
        :type player: Player
        """
        self.__player = player

    def set_strategy(self, strategy: "Strategy") -> None:
        """
        Sets the strategy.

        :param strategy: The strategy.
        :type strategy: Strategy
        """
        self.__strategy = strategy

    def set_map_known(self, game_map: Map) -> None:
        """
        Sets the map.

        :param game_map: The map.
        :type map: Map
        """
        self.__map_known = game_map
