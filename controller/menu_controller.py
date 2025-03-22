from controller.game_controller import GameController
from util.settings import Settings
from util.state_manager import GameState, MenuOptions
from view.menus.load_view import LoadMenu
from view.menus.menu_view import MenuView
from view.menus.settings_view import SettingsMenu
from datetime import datetime
import pickle, os

class MenuController:
    """Controller for all the menus in the game."""
    
    def __init__(self) -> None:
        """
        Initializes the MenuController with the default state NOT_STARTED and calls the main menu.
        
        :rtype: None
        """
        self.state: GameState = GameState.NOT_STARTED
        self.settings: Settings = Settings()
        self.__menu = MenuView()
        self.__game_controller: GameController = None
        self.call_menu()
    
    def call_menu(self) -> None:
        """
        When called, MenuController will display the main menu based on the current state.
        
        :rtype: None
        """
        option_selected: MenuOptions = self.__menu.show(self.state)
        self.handle_option(option_selected)
    
    def handle_option(self, option: MenuOptions) -> None:
        """
        Handles the option selected by the user.
        
        :param option: The option selected by the user.
        :type option: MenuOptions
        :rtype: None
        """
        option = MenuOptions(option)
        if option == MenuOptions.EXIT:
            self.exit()
        elif option == MenuOptions.SETTINGS:
            SettingsMenu(self.settings)
            self.call_menu()
        elif option == MenuOptions.START_GAME:
            self.start_game()
        elif option == MenuOptions.LOAD_GAME:
            filename = LoadMenu().show()
            if filename is not None:
                self.load_game(filename)
            else:
                self.call_menu()
        elif option == MenuOptions.RESUME:
            self.resume()
        elif option == MenuOptions.RESTART:
            self.start_game()
        elif option == MenuOptions.SAVE_GAME:
            self.save_game()  
        elif option==MenuOptions.VISITOR:
            self.start_game_visitor()
        
        
    def start_game_visitor(self)->None:
        """
        Starts a new game in 'visitor' mode (no AI, no game threads, only map).
        """    
        self.state = GameState.NOT_STARTED
        self.__game_controller = GameController(self, load=3)
        
        
        
              
    
    
    
    
    def exit(self) -> None:
        """
        Exits the game.
        
        :rtype: None
        """
        if self.__game_controller:
            self.__game_controller.exit()
        exit(0)

    def start_game(self) -> None:
        """
        Starts a new game by creating a GameController instance.
        
        :rtype: None
        """
        self.state = GameState.PLAYING
        self.__game_controller = GameController(self)
        pass
    
    def pause(self, game_controller: GameController) -> None:
        """
        Pauses the game.
        
        :rtype: None
        """
        self.state = GameState.PAUSED
        self.__game_controller = game_controller
        self.call_menu()
    
    def resume(self) -> None:
        """
        Resumes the game.
        """
        self.state = GameState.PLAYING
        self.__game_controller.resume()
    
    def save_game(self) -> None:
        """Save the current game state"""
        if self.__game_controller:
            game_state = {
                'settings': self.settings,
                'map': self.__game_controller.get_map(),
                'players': self.__game_controller.get_players(),
                'command_list': self.__game_controller.get_commandlist()
            }
        try: 
            # Ensure the save directory exists
            save_dir = "save"
            os.makedirs(save_dir, exist_ok=True)

            # Generate a timestamped filename
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = os.path.join(save_dir, f"{timestamp}.pkl")

            with open(filename, 'wb') as file:
                pickle.dump(game_state, file)
            print(f"Game successfully saved to {filename}.")
            self.call_menu()
        except Exception as e:
            print(f"Error saving game: {e}")

    def load_game(self, filename: str) -> None:
        """Load a saved game state"""
        try:
            save_dir = "save"
            filepath = os.path.join(save_dir, filename + ".pkl")
            with open(filepath, 'rb') as file:
                game_state = pickle.load(file)

            self.settings = game_state['settings']
            self.__game_controller = GameController(self, True)
            self.__game_controller.load_game(game_state['map'], game_state['players'], game_state['command_list'])
            self.state = GameState.PLAYING
            self.__game_controller.start_all_threads()
            print("Game successfully loaded.")
        except FileNotFoundError:
            print(f"Save file not found.")
        except Exception as e:
            print(f"Error loading game: {e}")
