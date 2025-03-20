
from model.entity import Entity
from model.resources.resource import Resource


class Unit(Entity):
    """This class represents the units on the map."""

    def __init__(self, name: str, letter: str, hp: int, cost: dict[Resource, int], spawning_time: int, attack_per_second: int, speed: float):
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

    
    """This method will return the speed of attack of the unit"""
    def get_attack_per_second(self) -> float:
        return self.__attack_per_second
    
    """This method will return the speed of the unit"""
    def get_speed(self) -> float:
        return self.__speed
    
    """This method will return the range of the unit"""
    def get_range(self) -> int:
        return self.__range
    
    """This method will set the range of the unit"""
    def set_range(self, new_range: int):
        self.__range = new_range

    """This method will set the speed of the unit"""
    def set_speed(self, new_speed: float):
        self.__speed = new_speed


    """This method will set the attack speed of the unit"""
    def set_attack_per_second(self, new_attack_per_second: float):
        self.__attack_per_second = new_attack_per_second

    
   
        

            

