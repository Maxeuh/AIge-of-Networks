from blessed import Terminal

from util.settings import Settings
from util.state_manager import FPS, MapSize, MapType, StartingCondition


class SettingsMenu:
    """A class to represent the settings menu in the game."""

    def __init__(self, settings: Settings) -> None:
        """
        Initialize the SettingsMenu object.

        :param settings: The settings object containing the current game settings.
        :type settings: Settings
        """
        self.term: Terminal = Terminal()
        self.settings: Settings = settings
        self.selected_option: int = 0
        self.__show()

    def __toggle_option(self, option: str) -> None:
        """
        Toggle the selected option in the settings.

        :param option: The option to be toggled.
        :type option: str
        """
        if option == "Map Type" and self.settings.map_type != MapType.TEST:
            current_index = list(MapType).index(self.settings.map_type)
            new_index = (current_index + 1) % len(MapType)
            self.settings.map_type = list(MapType)[new_index]
        elif option == "Map Size":
            current_index = list(MapSize).index(self.settings.map_size)
            new_index = (current_index + 1) % len(MapSize)
            self.settings.map_size = list(MapSize)[new_index]
        elif option == "Starting Condition":
            current_index = list(StartingCondition).index(
                self.settings.starting_condition
            )
            new_index = (current_index + 1) % len(StartingCondition)
            self.settings.starting_condition = list(StartingCondition)[new_index]
        elif option == "FPS":
            current_index = list(FPS).index(self.settings.fps)
            new_index = (current_index + 1) % len(FPS)
            self.settings.fps = list(FPS)[new_index]

    def __show(self) -> None:
        """Display the settings menu and handle user input."""
        with self.term.fullscreen(), self.term.cbreak(), self.term.hidden_cursor():
            while True:
                print(self.term.clear)
                print(self.term.center(self.term.bold_red("Settings Menu")))

                options = ["Map Type", "Map Size", "Starting Condition", "FPS", "Back"]

                for i, option in enumerate(options):
                    if option == "Back":
                        formatted_value = ""
                    else:
                        value = getattr(self.settings, option.lower().replace(" ", "_"))
                        if option == "FPS":
                            formatted_value = str(value.value)
                        else:
                            formatted_value = value.name.replace("_", " ").title()
                    if i == self.selected_option:
                        if option == "Back":
                            print(self.term.on_black(self.term.white("\n→ Back")))
                        else:
                            print(
                                self.term.on_black(
                                    self.term.white(f"→ {option}: {formatted_value}")
                                )
                            )
                    else:
                        if option == "Back":
                            print(f"{self.term.normal}\n  Back")
                        else:
                            print(f"{self.term.normal}  {option}: {formatted_value}")

                key = self.term.inkey()
                if key.name == "KEY_UP":
                    self.selected_option = (self.selected_option - 1) % len(options)
                elif key.name == "KEY_DOWN":
                    self.selected_option = (self.selected_option + 1) % len(options)
                elif key.name == "KEY_ENTER":
                    selected_option = options[self.selected_option]
                    if selected_option == "Back":
                        break
                    self.__toggle_option(selected_option)
