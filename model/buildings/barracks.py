from model.buildings.building import Building
from model.resources.wood import Wood


class Barracks(Building):
    """This class represents the Barracks building."""

    def __init__(self) -> None:
        """Initialize a Barracks object."""
        super().__init__("Barracks", "B", 500, {Wood(): 175}, 3, 50)
