from model.buildings.building import Building
from model.resources.wood import Wood


class TownCenter(Building):
    """This class represents the Town Center building."""

    def __init__(self) -> None:
        """Initialize a TownCenter object."""
        super().__init__("Town Center", "T", 1000, {Wood(): 350}, 4, 150)
        self.__capacity_increase = 5
        super().set_population_increase(True)
        super().set_resources_drop_point(True)

    def get_capacity_increase(self) -> int:
        """
        Returns the population capacity increase of the town center.

        :return: The population capacity increase.
        :rtype: int
        """
        return self.__capacity_increase
