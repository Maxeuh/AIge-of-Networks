from model.buildings.building import Building
from model.resources.food import Food
from model.resources.wood import Wood


class Farm(Building):
    """This class represents the Farm building."""

    def __init__(self) -> None:
        """Initialize a Farm object."""
        super().__init__("Farm", "F", 100, {Wood(): 60}, 2, 10)
        self.___food: Food = Food()

    def get_food(self) -> Food:
        """
        Returns the food object of the farm.

        :return: The food object.
        :rtype: Food
        """
        return self.___food
