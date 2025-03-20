from util.state_manager import FPS, MapSize, MapType, StartingCondition


class Settings:
    """
    Create a new Settings object with default values. It is used to store the game settings and allows the user to change them.

    :ivar map_type: The type of the map.
    :vartype map_type: MapType
    :ivar map_size: The size of the map.
    :vartype map_size: MapSize
    :ivar starting_condition: The starting condition of the game.
    :vartype starting_condition: StartingCondition
    :ivar fps: The frames per second setting.
    :vartype fps: int
    """

    def __init__(self) -> None:
        """Create a new Settings object with default values."""
        self.map_type: MapType = MapType.RICH
        self.map_size: MapSize = MapSize.SMALL
        self.starting_condition: StartingCondition = StartingCondition.LEAN
        self.fps: int = FPS.FPS_60
