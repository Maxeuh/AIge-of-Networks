from model.resources.food import Food
from model.resources.gold import Gold
from model.resources.resource import Resource
from model.resources.wood import Wood
from model.units.unit import Unit


class Villager(Unit):
    """This class represents the Villager unit"""

    def __init__(self):
        """Initializes the villager"""
        super().__init__("Villager", "v", 25, {Food(): 50}, 25, 2, 0.8)        
        self.__inventory: dict[Resource, int] = {Food(): 0,Gold(): 0,Wood(): 0}
        self.__inventory_size: int = 20
        self.__collect_time_per_minute: int = 25

    def get_inventory(self) -> dict[Resource, int]:
        """
        Returns the inventory of the villager.

        :return: The inventory of the villager.
        :rtype: dict[Resource, int]
        """
        return self.__inventory
    
    def get_inventory_size(self) -> int:
        """
        Returns the inventory size of the villager.

        :return: The inventory size of the villager.
        :rtype: int
        """
        return self.__inventory_size
    
    def get_collect_time_per_minute(self) -> int:
        """
        Returns the time it takes to collect resources per minute.

        :return: The time it takes to collect resources per minute.
        :rtype: int
        """
        return self.__collect_time_per_minute
    
    def stock_resource(self,resource: Resource, amount: int) -> None:
        """
        Stocks the resource in the inventory of the villager.

        :param resource: The resource to stock.
        :type resource: Resource
        :param amount: The amount of resource to stock.
        :type amount: int
        """
        if self.__inventory[Wood()] + self.__inventory[Food()] + self.__inventory[Gold()] + amount <= self.__inventory_size:
            self.__inventory[resource] += amount
        else:
            self.__inventory[resource] += self.__inventory_size - self.__inventory[Wood()] + self.__inventory[Food()] + self.__inventory[Gold()]
            raise ValueError("Capacity exceeded")
        
    def empty_resource(self) -> dict[Resource, int]:
        """
        Empties the inventory of the villager.

        :return: The inventory of the villager.
        :rtype: dict[Resource, int]
        """
        inventory = self.__inventory
        self.__inventory = {Food(): 0,Gold(): 0,Wood(): 0}
        return inventory