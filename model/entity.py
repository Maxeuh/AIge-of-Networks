import typing

from model.game_object import GameObject
from model.resources.resource import Resource

if typing.TYPE_CHECKING:
    from model.tasks.task import Task
    from model.player.player import Player


class Entity(GameObject):
    """This class represents the entities (Units and Buildings) on the map."""

    def __init__(
        self,
        name: str,
        letter: str,
        hp: int,
        cost: dict["Resource", int],
        spawning_time: int,
    ):
        """
        Initializes the entity.

        :param name: The name of the entity.
        :type name: str
        :param letter: The letter representing the entity.
        :type letter: str
        :param hp: The hit points of the entity.
        :type hp: int
        :param cost: The cost of the entity in resources.
        :type cost: dict['Resource', int]
        :param spawning_time: The time it takes to spawn the entity.
        :type spawning_time: int
        """
        super().__init__(name, letter, hp)
        self.__cost: dict[Resource, int] = cost
        self.__spawning_time: int = spawning_time
        self.__player: "Player" = None
        self.__task: "Task" = None

    def __repr__(self):
        return f"{self.get_name()} Hp: {self.get_hp()}. Coordinate: {self.get_coordinate()}"

    def __repr__(self):
        return f"{self.get_name()} Hp: {self.get_hp()}. Coordinate: {self.get_coordinate()}"

    def get_cost(self) -> dict[Resource, int]:
        """
        Returns the cost of the entity.

        :return: The cost of the entity in resources.
        :rtype: dict['Resource', int]
        """
        return self.__cost

    def get_spawning_time(self) -> int:
        """
        Returns the spawning time of the entity.

        :return: The spawning time of the entity.
        :rtype: int
        """
        return self.__spawning_time

    def get_player(self) -> "Player":
        """
        Returns the player associated with the entity.

        :return: The player associated with the entity.
        :rtype: Player
        """
        return self.__player

    def set_player(self, player: "Player") -> None:
        """
        Sets the player associated with the entity.

        :param player: The player to associate with the entity.
        :type player: Player
        """
        self.__player = player

    def get_task(self) -> "Task":
        """
        Returns the task associated with the entity.

        :return: The task associated with the entity.
        :rtype: Task
        """
        return self.__task

    def set_task(self, task: "Task") -> None:
        """
        Sets the task associated with the entity.

        :param task: The task to associate with the entity.
        :type task: Task
        """
        self.__task = task
