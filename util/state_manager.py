from enum import Enum

class MapType(Enum):
    """
    Enum representing the different types of maps that can be generated.

    This Enum class defines the various types of maps that can be generated.

    :cvar RICH: Represents the map type with generous resources dotted across the map.
    :cvar GOLD_CENTER: Represents the map type with all the gold at the centre of the map.
    :cvar TEST: Represents the map type for testing purposes.
    """
    RICH = 1
    GOLD_CENTER = 2
    TEST = 9

class MapSize(Enum):
    """
    Enum representing the different sizes of the map.

    This Enum class defines the various sizes that the map can be.

    :cvar SMALL: Represents the small map size of 120x120.
    """
    SMALL = 120
    MEDIUM = 240
    LARGE = 480

class StartingCondition(Enum):
    """
    Enum representing the different starting conditions of the game.

    This Enum class defines the various starting conditions that the game can be in.

    :cvar LEAN: Represents the starting condition with lean resources:
        - 50F, 200W, 50G
        - Town Centre, 3 Villagers
    :cvar MEAN: Represents the starting condition with mean resources:
        - 2000(F,W,G)
        - Town Centre, 3 Villagers
    :cvar MARINES: Represents the starting condition with marines resources:
        - 20000(F,W,G)
        - 3 Town Centres, 15 Villagers, 2 (Barracks, Stable, Archery Range)
    """
    LEAN = 0
    MEAN = 1
    # MARINES = 2

class GameState(Enum):
    """
    Enum representing the different states of the game.

    This Enum class defines the various states that the game can be in.

    :cvar NOT_STARTED: The game has not started yet.
    :cvar PLAYING: The game is currently being played.
    :cvar PAUSED: The game is currently paused.
    :cvar GAME_OVER: The game has ended.
    """
    NOT_STARTED = 0
    PLAYING = 1
    PAUSED = 2
    GAME_OVER = 3

class FPS(Enum):
    """
    Enum class representing the different frames per second options available in the game.

    This enum class defines the various frames per second options that can be selected from the game's settings.

    :cvar FPS_15: Represents the option for 15 frames per second.
    :cvar FPS_30: Represents the option for 30 frames per second.
    :cvar FPS_60: Represents the option for 60 frames per second.
    """
    FPS_15 = 15
    FPS_30 = 30
    FPS_60 = 60

class MenuOptions(Enum):
    """
    Enum class representing the different menu options available in the game.

    This enum class defines the various options that can be selected from the game's menu.

    :cvar EXIT: Represents the option to exit the game.
    :cvar SETTINGS: Represents the option to open the settings menu.
    :cvar START_GAME: Represents the option to start a new game.
    :cvar RESUME: Represents the option to resume the current game.
    :cvar RESTART: Represents the option to restart the current game.
    :cvar LOAD_GAME: Represents the option to load a previously saved game.
    :cvar SAVE_GAME: Represents the option to save the current game.
    """
    EXIT = 0
    SETTINGS = 1
    START_GAME = 2
    RESUME = 3
    RESTART = 4
    LOAD_GAME = 5
    SAVE_GAME = 6
    VISITOR=7
