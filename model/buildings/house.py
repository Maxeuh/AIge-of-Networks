from model.buildings.building import Building
from model.resources.wood import Wood


class House(Building):
    """This class represents the House building."""

    def __init__(self) -> None:
        """Initialize a House object."""
        super().__init__("House", "H", 200, {Wood(): 25}, 2, 25)
        self.__capacity_increase = 5
        super().set_population_increase(True)

    def get_capacity_increase(self) -> int:
        """
        Returns the population capacity increase of the town center.

        :return: The population capacity increase.
        :rtype: int
        """
        return self.__capacity_increase
