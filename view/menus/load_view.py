import os

from blessed import Terminal


class LoadMenu:
    """
    Represents the menu view in the terminal window.
    It's used to display the starting screen of the game, the menu (pause), and all available options:
    Create, start, load, save a game; change its settings, etc.
    """

    def __init__(self) -> None:
        """Initialize the menu view."""
        self.current_option: int = 0
        self.term: Terminal = Terminal()

    def __get_menu_options(self) -> list[str]:
        """
        Get the different options available in the menu depending on the game state.

        :param game_state: The current state of the game.
        :type game_state: GameState
        :return: A list of menu options available for the given game state.
        :rtype: list[MenuOptions]
        """
        save_directory = "save"  # Nom du dossier contenant les sauvegardes
        try:
            # Lister les fichiers dans le répertoire
            if os.path.exists(save_directory):
                save_files = sorted(
                    [
                        os.path.splitext(f)[0]
                        for f in os.listdir(save_directory)
                        if os.path.isfile(os.path.join(save_directory, f))
                    ],
                    key=lambda x: os.path.getmtime(
                        os.path.join(save_directory, x + ".pkl")
                    ),
                    reverse=True,
                )
                if not save_files:
                    return ["No save files found"]
                return save_files
            else:
                return ["Save directory not found"]
        except Exception as e:
            return [f"Error reading save directory: {e}"]

    # def show(self) -> str:
    #     """
    #     Show the menu in the terminal window.
    #
    #     :param game_state: The current state of the game.
    #     :type game_state: GameState
    #     :return: The value of the selected menu option.
    #     :rtype: int
    #     """
    #     with self.term.fullscreen(), self.term.cbreak(), self.term.hidden_cursor():
    #         while True:
    #             print(self.term.clear)
    #             options = self.__get_menu_options()
    #
    #             print(self.term.center(self.term.bold_red("Load Game")))
    #
    #             for i, option in enumerate(options):
    #                 option_str = option.name.replace("_", " ").title()
    #                 y = 3 + i
    #                 if i == self.current_option:
    #                     print(self.term.on_black(self.term.white(f"→ {option_str}")))
    #                 else:
    #                     print(f"  {option_str}")
    #
    #             print("\nUse ↑/↓ to navigate, Enter to select, or 'q' to quit.")
    #
    #
    #             key = self.term.inkey()
    #
    #             if key.code == self.term.KEY_UP and self.current_option > 0:
    #                 self.current_option -= 1
    #             elif key.code == self.term.KEY_DOWN and self.current_option < len(options) - 1:
    #                 self.current_option += 1
    #             elif key.code in [self.term.KEY_ENTER, '\n', '\r']:
    #                 return options[self.current_option].value

    def show(self) -> str:
        """
        Show the menu in the terminal window and allow the user to select a save file.

        :return: The name of the selected save file or None to return to the main menu.
        :rtype: str
        """
        with self.term.fullscreen(), self.term.cbreak(), self.term.hidden_cursor():
            while True:
                print(self.term.clear)
                options = self.__get_menu_options()

                # Ajouter l'option pour revenir en arrière
                options.append("Back")

                print(self.term.center(self.term.bold_red("Load Game")))

                for i, option in enumerate(options):
                    y = 3 + i
                    if i == self.current_option:
                        print(self.term.on_black(self.term.white(f"→ {option}")))
                    else:
                        print(f"  {option}")

                key = self.term.inkey()

                if key.code == self.term.KEY_UP and self.current_option > 0:
                    self.current_option -= 1
                elif (
                    key.code == self.term.KEY_DOWN
                    and self.current_option < len(options) - 1
                ):
                    self.current_option += 1
                elif key.lower() == "q":  # Quitter le menu
                    return None
                elif key.code in [self.term.KEY_ENTER, "\n", "\r"]:
                    # Gérer l'option "Back"
                    if options[self.current_option] == "Back":
                        return None
                    # Gérer le cas des messages d'erreur ou sélectionner un fichier valide
                    elif options[self.current_option] in [
                        "No save files found",
                        "Save directory not found",
                    ]:
                        return None
                    return options[self.current_option]
