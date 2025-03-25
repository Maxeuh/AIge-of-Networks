from model.entity import Entity
from model.resources.resource import Resource


class Unit(Entity):
    """This class represents the units on the map."""

    def __init__(
        self,
        name: str,
        letter: str,
        hp: int,
        cost: dict[Resource, int],
        spawning_time: int,
        attack_per_second: int,
        speed: float,
    ):
        """
        Initializes the unit.

        :param name: The name of the unit.
        :type name: str
        :param letter: The letter representing the unit.
        :type letter: str
        :param hp: The hit points of the unit.
        :type hp: int
        :param cost: The cost to create the unit.
        :type cost: dict['Resource', int]
        :param spawning_time: The time it takes to spawn the unit.
        :type spawning_time: int
        :param attack_per_second: The attack rate of the unit.
        :type attack_per_second: int
        :param speed: The speed of the unit.
        :type speed: float
        """
        super().__init__(name, letter, hp, cost, spawning_time)
        self.__attack_per_second: int = attack_per_second
        self.__speed: float = speed
        self.__range: int = 1
        super().set_sprite_path(f"assets/sprites/units/{name.lower()}.png")

    def get_attack_per_second(self) -> float:
        """This method will return the speed of attack of the unit"""
        return self.__attack_per_second

    def get_speed(self) -> float:
        """This method will return the speed of the unit"""
        return self.__speed

    def get_range(self) -> int:
        """This method will return the range of the unit"""
        return self.__range

    def set_range(self, new_range: int):
        """This method will set the range of the unit"""
        self.__range = new_range

    def set_speed(self, new_speed: float):
        """This method will set the speed of the unit"""
        self.__speed = new_speed

    def set_attack_per_second(self, new_attack_per_second: float):
        """This method will set the attack speed of the unit"""
        self.__attack_per_second = new_attack_per_second
