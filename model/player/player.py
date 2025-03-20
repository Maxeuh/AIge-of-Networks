from typing import TYPE_CHECKING, Set

from model.buildings.building import Building
from model.resources.food import Food
from model.resources.gold import Gold
from model.resources.resource import Resource
from model.resources.wood import Wood
from model.units.unit import Unit
from util.coordinate import Coordinate

if TYPE_CHECKING:
    from model.ai import AI
    from model.commands.command import CommandController, TaskController


class Player:
    """This class represents the player (AI) in the game."""

    def __init__(self, name: str, color: str) -> None:
        """
        Initializes the player with the given name and color.

        :param name: The name of the player.
        :type name: str
        :param color: The color of the player.
        :type color: str
        """
        self.__name: str = name
        self.__color: str = color
        self.__resource: dict[Resource, int] = {Food(): 0, Gold(): 0, Wood(): 0}
        self.__units: Set[Unit] = set()
        self.__unit_count: int = 0
        self.__buildings: Set[Building] = set()
        self.__max_population: int = 0
        self.__command_manager: "CommandController" = None
        self.__task_manager: "TaskController" = None
        self.__ai: "AI" = None
        self.__centre_coordinate: Coordinate = None

    def __repr__(self):
        return f"{self.get_name()} : {self.get_color()}"

    def get_centre_coordinate(self) -> Coordinate:
        return self.__centre_coordinate

    def update_centre_coordinate(self) -> None:
        if self.__buildings:
            total_x = sum(
                building.get_coordinate().get_x() for building in self.__buildings
            )
            total_y = sum(
                building.get_coordinate().get_y() for building in self.__buildings
            )
            self.__centre_coordinate = Coordinate(total_x, total_y) // len(
                self.__buildings
            )
        else:
            self.__centre_coordinate = None

    def get_ai(self) -> "AI":
        """
        Returns the AI of the player.

        :return: The AI.
        :rtype: AI
        """
        return self.__ai

    def set_ai(self, ai: "AI") -> None:
        """
        Sets the AI of the player.

        :param ai: The AI to set.
        :type ai: AI
        """
        self.__ai = ai

    def capture(self) -> "Player":
        """
        Capture the player current state
        """
        player: Player = Player(self.__name, self.__color)
        player.__resource = self.__resource.copy()
        player.__units = self.__units.copy()
        player.__unit_count = self.__unit_count
        player.__buildings = self.__buildings.copy()
        player.__max_population = self.__max_population
        player.__centre_coordinate = self.__centre_coordinate
        return player

    def get_name(self) -> str:
        """
        Returns the name of the player.

        :return: The name of the player.
        :rtype: str
        """
        return self.__name

    def get_color(self) -> str:
        """
        Returns the color of the player.

        :return: The color of the player.
        :rtype: str
        """
        return self.__color

    def get_resources(self) -> dict[Resource, int]:
        """
        Returns the resources of the player.

        :return: A dictionary of resources and their amounts.
        :rtype: dict[Resource, int]
        """
        return self.__resource

    def collect(self, resource: Resource, amount: int) -> None:
        """
        Adds a resource to the player.

        :param resource: The type of resource to add.
        :type resource: Resource
        :param amount: The amount of the resource to add.
        :type amount: int
        """
        if (
            isinstance(resource, Food)
            or isinstance(resource, Gold)
            or isinstance(resource, Wood)
        ):
            self.__resource[resource] += amount

    def check_consume(self, resource: Resource, amount: int) -> bool:
        """
        Checks if the player has enough resources to consume.

        :param resource: The type of resource to check.
        :type resource: Resource
        :param amount: The amount of the resource to check.
        :type amount: int
        :return: True if the player has enough resources, False otherwise.
        :rtype: bool
        """
        return self.__resource[resource] >= amount

    def consume(self, resource: Resource, amount: int) -> None:
        """
        Uses a resource from the player.

        :param resource: The type of resource to consume.
        :type resource: Resource
        :param amount: The amount of the resource to consume.
        :type amount: int
        :raises ValueError: If there are not enough resources to consume.
        """
        if not self.check_consume(resource, amount):
            raise ValueError("Not enough resources to consume")
        self.__resource[resource] -= amount

    def get_units(self) -> Set[Unit]:
        """
        Returns the units of the player.

        :return: A set of units.
        :rtype: Set[Unit]
        """
        return self.__units

    def get_unit_count(self) -> int:
        """
        Returns the number of units of the player.

        :return: The number of units.
        :rtype: int
        """
        return self.__unit_count

    def add_unit(self, unit: Unit) -> None:
        """
        Adds a unit to the player.

        :param unit: The unit to add.
        :type unit: Unit
        :raises ValueError: If the player has reached the maximum population.
        """
        if not self.__unit_count < self.__max_population:
            raise ValueError("Player has reached the maximum population")
        self.__units.add(unit)
        self.__unit_count += 1

    def remove_unit(self, unit: Unit) -> None:
        """
        Removes a unit from the player.

        :param unit: The unit to remove.
        :type unit: Unit
        """
        self.__units.remove(unit)
        self.__unit_count -= 1

    def get_buildings(self) -> Set[Building]:
        """
        Returns the buildings of the player.

        :return: A set of buildings.
        :rtype: Set[Building]
        """
        return self.__buildings

    def add_building(self, building: Building) -> None:
        """
        Adds a building to the player.

        :param building: The building to add.
        :type building: Building
        """
        self.__buildings.add(building)

    def remove_building(self, building: Building) -> None:
        """
        Removes a building from the player.

        :param building: The building to remove.
        :type building: Building
        """
        self.__buildings.remove(building)

    def get_max_population(self) -> int:
        """
        Returns the maximum population of the player.

        :return: The maximum population.
        :rtype: int
        """
        return self.__max_population

    def get_command_manager(self) -> "CommandController":
        """
        Returns the command manager of the player.

        :return: The command manager.
        :rtype: CommandController
        """
        return self.__command_manager

    def set_command_manager(self, command_manager: "CommandController") -> None:
        """
        Sets the command manager of the player.

        :param command_manager: The command manager to set.
        :type command_manager: CommandController
        """
        self.__command_manager = command_manager

    def set_max_population(self, max_population: int) -> None:
        """
        Sets the maximum population of the player.

        :param max_population: The maximum population to set.
        :type max_population: int
        """
        self.__max_population = max_population

    def get_task_manager(self) -> "TaskController":
        """
        Returns the task manager of the player.

        :return: The task manager.
        :rtype: TaskController
        """
        return self.__task_manager

    def set_task_manager(self, task_manager: "TaskController") -> None:
        """
        Sets the task manager of the player.

        :param task_manager: The task manager to set.
        :type task_manager: TaskController
        """
        self.__task_manager = task_manager

    def __eq__(self, other: "Player") -> bool:
        """
        Compares the player to another player.

        :param other: The other player to compare.
        :type other: Player
        :return: True if the players are equal, False otherwise.
        :rtype: bool
        """
        if not isinstance(other, Player) or other is None:
            return False
        return self.__name == other.get_name() and self.__color == other.get_color()
