import random
from controller.view_controller import ViewController
from model.buildings.town_center import TownCenter
from model.resources.food import Food
from model.resources.wood import Wood
from model.resources.gold import Gold
from model.units.villager import Villager
from network.game_sender import GameSender
from util.map import Map
from util.coordinate import Coordinate
from util.settings import Settings
from util.state_manager import MapType, StartingCondition
from controller.command import CommandManager, Command, TaskManager, BuildTask, MoveTask, CollectAndDropTask, SpawnCommand
from controller.interactions import Interactions
from controller.AI_controller import AIController, AI
from model.player.player import Player
from pygame import time
from model.player.strategy import Strategy1
import threading
import typing
from network.game_network import GameEventSender
from network.network_manager import NetworkManager

if typing.TYPE_CHECKING:
    from controller.menu_controller import MenuController
class GameController:
    """This module is responsible for controlling the game."""
    _instance = None

    @staticmethod
    def get_instance(menu_controller: 'MenuController'):
        if GameController._instance is None:
            GameController._instance = GameController(menu_controller)
        return GameController._instance

    def __init__(self, menu_controller: 'MenuController', load: int = 2, player_number=1) -> None:
        """
        Initializes the GameController with the given settings.

        :param menu_controller: The menu controller.
        :type menu_controller: MenuController
        1 is  load 
        2 is not  load 
        3 is visitor
        """
        self.__game_sender = GameSender()
        
        # Store player number
        self.player_number = player_number
        
        # Use different AI settings based on player number
        if player_number == 2:
            # Second player has different settings
            self.is_ai_enabled = False  # Example setting
        
        if load== 2:
            self.__menu_controller: 'MenuController' = menu_controller
            self.settings: Settings = self.__menu_controller.settings
            self.__command_list: list[Command] = []
            self.__players: list[Player] = []
            self.__map: Map = self.__generate_map()
            self.__ai_controller: AIController = AIController(self,1)
            self.__assign_AI()
            self.__running: bool = False
            self.__game_thread = threading.Thread(target=self.game_loop)
            self.__ai_thread = threading.Thread(target=self.__ai_controller.ai_loop)
            self.__view_controller: ViewController = ViewController(self)
            
            
            # Set up and start the game sender AFTER all other initialization
            self.__game_sender.setup(self)
            self.__game_sender.start()
            self.__game_sender.handle_client_registration()
            
            # Initialize network manager
            self.network_manager = NetworkManager(self)
            self.network_manager.start()
            
            self.__game_thread.start()
            self.__ai_thread.start()
            self.__view_controller.start_view()
        elif load==1:
            self.__menu_controller: 'MenuController' = menu_controller
            self.settings: Settings = self.__menu_controller.settings
            self.__command_list: list[Command] = []
            self.__players: list[Player] = []
            self.__map: Map = self.__generate_map()
            self.__ai_controller: AIController = AIController(self,1)
            self.__assign_AI()
            self.__running: bool = False
            self.__ai_thread = None
            self.__view_controller = None
            self.__game_thread = None
        else:
            # visitor mode
            self.__menu_controller: 'MenuController' = menu_controller
            self.settings: Settings = self.__menu_controller.settings
            self.__map: Map = self.__generate_map(skip_players=True)
            self.__ai_controller = None
            self.__running = False
            self.__ai_thread = None
            self.__view_controller: ViewController = ViewController(self)
            self.__game_thread = None
            self.__view_controller.start_view()
                
        # Initialize network event sender
        self.event_sender = GameEventSender()

    def start_all_threads(self, is_visitor: bool = False):
        """
        Start threads if not a visitor.
        """
        if is_visitor:
            # Skip AI/game loops, directly start the view:
            self.__view_controller = ViewController(self)
            self.__view_controller.start_view()
        else:
            self.__view_controller = ViewController(self)
            self.__game_thread = threading.Thread(target=self.game_loop)
            self.__ai_thread = threading.Thread(target=self.__ai_controller.ai_loop)
            self.__ai_thread.start()
            self.__game_thread.start()
            self.__view_controller.start_view()

    def handle_external_state(self, item_data: dict) -> None:
        """
        Method for a visitor to update this view with external item data.
        """
        if self.__view_controller:
            # Propagate data to view
            self.__view_controller.update_map_state(item_data)
    def update_map_state(self):
        pass

    
    def get_commandlist(self):
        return self.__command_list
        
    def __generate_players(self, number_of_player: int, map: Map ) -> None:
        """
        Generates the players based on the settings.
        """
        colors = ["blue", "red", "green", "yellow", "purple", "orange", "pink", "cyan"]
        for i in range(number_of_player):
            player = Player("Player 1", colors[0])
            self.get_players().append(player)
            player.set_command_manager(CommandManager(map, player, self.settings.fps.value, self.__command_list))
            player.set_task_manager(TaskManager(player.get_command_manager()))
    
    def __assign_AI(self)-> None:
        for player in self.get_players():
            player.set_ai(AI(player,None, map))
            player.get_ai().set_strategy(Strategy1(player.get_ai(), 5))
            # print(f"Player {player.get_name()} has strat {player.get_ai().get_strategy()}")
            player.update_centre_coordinate()

            option = StartingCondition(self.settings.starting_condition)
            if option == StartingCondition.LEAN:
                player.collect( Food(), 50 )
                player.collect( Wood(), 200 )
                player.collect( Gold(), 50 )
            elif option == StartingCondition.MEAN:
                player.collect( Food(), 2000 )
                player.collect( Wood(), 2000 )
                player.collect( Gold(), 2000 )
            # elif option == StartingCondition.MARINES:
            #     player.collect( Food(), 20000 )
            #     player.collect( Wood(), 20000 )
            #     player.collect( Gold(), 20000 )
        
    def __generate_map(self, skip_players: bool = False) -> Map:
        """
        Generates a map with or without placing players, depending on skip_players.
        If skip_players is True, only resources are placed, with no players or units.
        """
        # Create the map
        map_generation: Map = Map(self.settings.map_size.value)
        interactions = Interactions(map_generation)

        # Optionally generate players
        if not skip_players:
            self.__generate_players(1, map_generation)
            first_player_coordinate = None
            min_distance = int(self.settings.map_size.value * 0.3)

            for player in self.get_players():
                town_center = TownCenter()

                if player == self.get_players()[0]:
                    while True:
                        center_size = 2 if map_generation.get_size() % 2 == 0 else 1
                        center_coordinate = Coordinate((map_generation.get_size() - center_size) // 2,
                                                       (map_generation.get_size() - center_size) // 2)
                        coordinate = Coordinate((map_generation.get_size() - center_size) // 2,
                                                (map_generation.get_size() - center_size) // 2)
                        # Ensure it's at least min_distance from the center
                        while coordinate.distance(center_coordinate) < min_distance:
                            coordinate = Coordinate(
                                random.randint(0, self.settings.map_size.value - 1),
                                random.randint(0, self.settings.map_size.value - 1)
                            )
                        coordinate_mirror = Coordinate(
                            self.settings.map_size.value - 1 - coordinate.get_x() - town_center.get_size() + 1,
                            self.settings.map_size.value - 1 - coordinate.get_y() - town_center.get_size() + 1
                        )
                        if map_generation.check_placement(town_center, coordinate) \
                           and map_generation.check_placement(town_center, coordinate_mirror):
                            break
                    first_player_coordinate = coordinate
                else:
                    coordinate = Coordinate(
                        self.settings.map_size.value - 1 - first_player_coordinate.get_x() - town_center.get_size() + 1,
                        self.settings.map_size.value - 1 - first_player_coordinate.get_y() - town_center.get_size() + 1
                    )

                # Place the town center
                interactions.place_object(town_center, coordinate)
                interactions.link_owner(player, town_center)
                player.set_max_population(player.get_max_population() + town_center.get_capacity_increase())

                # Generate a list of coordinates around the town center (not inside it)
                around_coordinates = []
                for x in range(coordinate.get_x() - 1,
                               coordinate.get_x() + town_center.get_size()):
                    for y in range(coordinate.get_y() - 1,
                                   coordinate.get_y() + town_center.get_size()):
                        if (0 <= x < self.settings.map_size.value
                           and 0 <= y < self.settings.map_size.value):
                            is_town_center_area = (coordinate.get_x() <= x < coordinate.get_x() + town_center.get_size()
                                                   and coordinate.get_y() <= y < coordinate.get_y() + town_center.get_size())
                            if not is_town_center_area:
                                around_coordinates.append(Coordinate(x, y))

                # Place 3 villagers around the town center
                for _ in range(3):
                    villager = Villager()
                    while True:
                        coords_index = random.randint(0, len(around_coordinates) - 1)
                        villager_coord = around_coordinates.pop(coords_index)
                        if map_generation.check_placement(villager, villager_coord):
                            break
                    interactions.place_object(villager, villager_coord)
                    interactions.link_owner(player, villager)

        # Resource generation: RICH or GOLD_CENTER or TEST, etc.
        if MapType(self.settings.map_type) == MapType.RICH:
            wood = Wood()
            # Place wood on 5% of the map
            for _ in range(int(self.settings.map_size.value ** 2 * 0.05)):
                while True:
                    rand_coord = Coordinate(
                        random.randint(0, self.settings.map_size.value - 1),
                        random.randint(0, self.settings.map_size.value - 1)
                    )
                    if map_generation.check_placement(wood, rand_coord):
                        break
                map_generation.add(wood, rand_coord)
                wood.set_coordinate(rand_coord)

            # Place gold (0.5% of the map)
            for _ in range(int(self.settings.map_size.value ** 2 * 0.005)):
                gold = Gold()
                while True:
                    rand_coord = Coordinate(
                        random.randint(0, self.settings.map_size.value - 1),
                        random.randint(0, self.settings.map_size.value - 1)
                    )
                    if map_generation.check_placement(gold, rand_coord):
                        break
                map_generation.add(gold, rand_coord)
                gold.set_coordinate(rand_coord)

        elif MapType(self.settings.map_type) == MapType.GOLD_CENTER:
            # Place gold in a circle at the center
            center = Coordinate(self.settings.map_size.value // 2,
                                self.settings.map_size.value // 2)
            radius = int(self.settings.map_size.value * 0.05)
            for x in range(center.get_x() - radius, center.get_x() + radius + 1):
                for y in range(center.get_y() - radius, center.get_y() + radius + 1):
                    if (x - center.get_x()) ** 2 + (y - center.get_y()) ** 2 <= radius ** 2:
                        gold = Gold()
                        gold_coord = Coordinate(x, y)
                        map_generation.add(gold, gold_coord)
                        gold.set_coordinate(gold_coord)
            # Place wood (5% of the map)
            for _ in range(int(self.settings.map_size.value ** 2 * 0.05)):
                wood = Wood()
                while True:
                    rand_coord = Coordinate(
                        random.randint(0, self.settings.map_size.value - 1),
                        random.randint(0, self.settings.map_size.value - 1)
                    )
                    if map_generation.check_placement(wood, rand_coord):
                        break
                map_generation.add(wood, rand_coord)
                wood.set_coordinate(rand_coord)

        elif MapType(self.settings.map_type) == MapType.TEST:
            # Custom test scenario
            map_generation = Map(120)
            test_interactions = Interactions(map_generation)
            if not skip_players:
                self.__generate_players(2, map_generation)
                self.get_players()[0].collect(Wood(), 1000)

                town_center1 = TownCenter()
                test_interactions.place_object(town_center1, Coordinate(0, 0))
                test_interactions.link_owner(self.get_players()[0], town_center1)
                self.get_players()[0].set_max_population(
                    self.get_players()[0].get_max_population() + town_center1.get_capacity_increase()
                )
                villager1 = Villager()
                test_interactions.place_object(villager1, Coordinate(5, 5))
                test_interactions.link_owner(self.get_players()[0], villager1)
                town_center3 = TownCenter()
                villager1.set_task(BuildTask(
                    self.get_players()[0].get_command_manager(),
                    villager1,
                    Coordinate(6, 6),
                    town_center3
                ))
                town_center2 = TownCenter()
                test_interactions.place_object(town_center2, Coordinate(100, 100))
                test_interactions.link_owner(self.get_players()[1], town_center2)
                self.get_players()[1].set_max_population(
                    self.get_players()[1].get_max_population() + town_center2.get_capacity_increase()
                )
                villager2 = Villager()
                test_interactions.place_object(villager2, Coordinate(90, 90))
                test_interactions.link_owner(self.get_players()[1], villager2)

        return map_generation
    
    def pause(self) -> None:
        """Pauses the game."""
        self.__menu_controller.pause(self)
    
    ## question: what to do if a max_population_increase building is destroyed and the population cap is decreased and become lower than the current unit count?
    ## possible solution: ban the creation of new units until the population is lower than the new cap but not kill the units already created
    def get_map(self) -> Map:
        """
        Returns the map.
        :return: The map.
        :rtype: Map
        """
        return self.__map
    
    def get_players(self) -> list[Player]:
        """
        Returns the players.
        :return: The players.
        :rtype: list[Player]
        """
        return self.__players

    def start(self) -> None:
        """Starts the game."""
        self.__running = True
    
    def exit(self) -> None:
        """Exits the game."""
        self.__running = False
        self.__ai_controller.exit()
        
        # Stop network components
        if hasattr(self, 'network_manager'):
            self.network_manager.stop()
        
        # Stop the game sender
        if hasattr(self, '__game_sender'):
            self.__game_sender.stop()
            
        self.__menu_controller.exit()

    def get_speed(self) -> int:
        """Get the current speed."""
        return self.__view_controller.get_speed()

    # TODO: Generate list of players and their units/buildings.
    def update(self) -> None:
        """
        Update the game state.
        """
        for command in self.__command_list.copy():
            try:
                # Store state before command execution for comparison
                entity = command.get_entity()
                prev_state = self._capture_entity_state(entity)
                
                # Execute the command
                command.run_command()
                
                # Compare state and send update if changed
                new_state = self._capture_entity_state(entity)
                if self._state_changed(prev_state, new_state):
                    self._send_entity_update(entity, command, prev_state, new_state)
                    
            except (ValueError, AttributeError) as e:
                command.remove_command_from_list(self.__command_list)
                command.get_entity().set_task(None)
    
    def _capture_entity_state(self, entity):
        """Capture the current state of an entity for comparison"""
        state = {}
        
        # Capture position if available
        if hasattr(entity, "get_coordinate") and entity.get_coordinate():
            state["position"] = {
                "x": entity.get_coordinate().get_x(),
                "y": entity.get_coordinate().get_y()
            }
        
        # Capture health if available
        if hasattr(entity, "get_health"):
            state["health"] = entity.get_health()
        
        # Add any other state you need to track
        
        return state
    
    def _state_changed(self, prev_state, new_state):
        """Check if the entity state has changed"""
        # Compare positions
        if "position" in prev_state and "position" in new_state:
            if (prev_state["position"]["x"] != new_state["position"]["x"] or
                prev_state["position"]["y"] != new_state["position"]["y"]):
                return True
                
        # Compare health
        if "health" in prev_state and "health" in new_state:
            if prev_state["health"] != new_state["health"]:
                return True
                
        # Add other comparisons as needed
        
        return False
    
    def _send_entity_update(self, entity, command, prev_state, new_state):
        """Send a network update about an entity state change"""
        # Determine the event type based on the command
        event_type = command.__class__.__name__.upper().replace("COMMAND", "")
        
        # Create the event data
        event_data = {
            "entity_id": entity.get_id() if hasattr(entity, "get_id") else str(id(entity)),
            "entity_type": entity.__class__.__name__,
            "player_id": entity.get_owner().get_id() if hasattr(entity, "get_owner") else None,
            "previous_state": prev_state,
            "current_state": new_state
        }
        
        # Send the event using network manager instead of event_sender
        self.network_manager.send_game_event(event_type, event_data)

    
    def load_task(self) -> None:
        """
        Load the task of the player.
        serves as the player's input
        """
        for player in self.__players:
            for unit in player.get_units():
               #print(f"Unit {unit.get_name()} has {unit.get_task()} at {unit.get_coordinate()}")
               pass
            player.get_task_manager().execute_tasks()

    def game_loop(self) -> None:
        """
        The main game loop.
        """
        self.start()
        while self.__running:
            self.load_task()
            self.update() 
            # Cap the loop time to ensure it doesn't run faster than the desired FPS
            time.Clock().tick(self.settings.fps.value * self.get_speed())
    
    def resume(self) -> None:
        """
        Resumes the game.
        """
        self.start()
        if not self.__game_thread.is_alive():
            self.__game_thread = threading.Thread(target=self.game_loop)
            self.__game_thread.start()
        if not self.__ai_thread.is_alive():
            self.__ai_thread = threading.Thread(target=self.__ai_controller.ai_loop)
            self.__ai_thread.start()
        self.__view_controller.start_view()
    
    def load_game(self, map: Map, players: list[Player], command_list: list[Command]) -> None:
        """
        Load the game with the given map, players and settings.

        :param map: The map.
        :type map: Map
        :param players: The players.
        :type players: list[Player]
        """
        self.__map = map
        self.__players = players
        self.__running = True
        self.__command_list = command_list
        self.__ai_controller.load(self)
        

    def is_visitor_mode(self) -> bool:
        """Check if the game is running in visitor mode."""
        # Since visitor mode is when load==3 and ai_controller is None
        return self.__ai_controller is None