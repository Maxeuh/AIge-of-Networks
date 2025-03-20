import typing

from model.entity import Entity

if typing.TYPE_CHECKING:
    from model.resources.resource import Resource


class Building(Entity):
    """This class represents the buildings on the map."""

    def __init__(
        self,
        name: str,
        letter: str,
        hp: int,
        cost: dict["Resource", int],
        size: int,
        spawning_time: int,
    ):
        """
        Initializes the building.
        :param name: The name of the building.
        :type name: str
        :param letter: The letter representing the building.
        :type letter: str
        :param hp: The hit points of the building.
        :type hp: int
        :param cost: The cost to build the building.
        :type cost: dict['Resource', int]
        :param size: The size of the building.
        :type size: int
        :param spawning_time: The time it takes to spawn the building.
        :type spawning_time: int
        """
        self.__resources_drop_point: bool = False
        self.__population_increase: bool = False
        super().__init__(name, letter, hp, cost, spawning_time)
        super().set_size(size)
        super().set_sprite_path(f"assets/sprites/buildings/{self.get_name().lower}.png")

    def is_resources_drop_point(self) -> bool:
        """
        Returns whether or not the building is a resources drop point.
        :return: True if the building is a resources drop point, False otherwise.
        :rtype: bool
        """
        return self.__resources_drop_point

    def set_resources_drop_point(self, resources_drop_point: bool) -> None:
        """
        Sets whether or not the building is a resources drop point.
        :param resources_drop_point: True if the building is a resources drop point, False otherwise.
        :type resources_drop_point: bool
        """
        self.__resources_drop_point = resources_drop_point

    def is_population_increase(self) -> bool:
        """
        Returns whether or not the building increases the population.
        :return: True if the building increases the population, False otherwise.
        :rtype: bool
        """
        return self.__population_increase

    def set_population_increase(self, population_increase: bool) -> None:
        """
        Sets whether or not the building increases the population.
        :param population_increase: True if the building increases the population, False otherwise.
        :type population_increase: bool
        """
        self.__population_increase = population_increase
