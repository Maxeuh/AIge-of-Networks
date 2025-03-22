from blessed import Terminal
from util.state_manager import GameState, MenuOptions

class MenuView:
    """
    Represents the menu view in the terminal window.
    It's used to display the starting screen of the game, the menu (pause), and all available options:
    Create, start, load, save a game; change its settings, etc.
    """

    def __init__(self) -> None:
        """Initialize the menu view."""
        self.current_option: int = 0
        self.term: Terminal = Terminal()

    def __get_menu_options(self, game_state: GameState) -> list[MenuOptions]:
        """
        Get the different options available in the menu depending on the game state.

        :param game_state: The current state of the game.
        :type game_state: GameState
        :return: A list of menu options available for the given game state.
        :rtype: list[MenuOptions]
        """
        game_state = GameState(game_state)
        if game_state == GameState.NOT_STARTED:
            return [MenuOptions.START_GAME, MenuOptions.LOAD_GAME, MenuOptions.SETTINGS,MenuOptions.VISITOR, MenuOptions.EXIT]
        elif game_state == GameState.PAUSED:
            return [MenuOptions.RESUME, MenuOptions.SAVE_GAME, MenuOptions.SETTINGS, MenuOptions.EXIT]
        elif game_state == GameState.GAME_OVER:
            return [MenuOptions.RESTART, MenuOptions.LOAD_GAME, MenuOptions.SETTINGS, MenuOptions.EXIT]

    def show(self, game_state: GameState) -> int:
        """
        Show the menu in the terminal window.

        :param game_state: The current state of the game.
        :type game_state: GameState
        :return: The value of the selected menu option.
        :rtype: int
        """
        with self.term.fullscreen(), self.term.cbreak(), self.term.hidden_cursor():
            while True:
                print(self.term.clear)
                options = self.__get_menu_options(game_state)

                print(self.term.center(self.term.bold_red("AIge of EmpAIres")))

                for i, option in enumerate(options):
                    option_str = option.name.replace("_", " ").title()
                    y = 3 + i
                    if i == self.current_option:
                        print(self.term.on_black(self.term.white(f"→ {option_str}")))
                    else:
                        print(f"  {option_str}")

                key = self.term.inkey()

                if key.code == self.term.KEY_UP and self.current_option > 0:
                    self.current_option -= 1
                elif key.code == self.term.KEY_DOWN and self.current_option < len(options) - 1:
                    self.current_option += 1
                elif key.code in [self.term.KEY_ENTER, '\n', '\r']:
                    return options[self.current_option].value