import random
from controller.view_controller import ViewController
from model.buildings.town_center import TownCenter
from model.resources.food import Food
from model.resources.wood import Wood
from model.resources.gold import Gold
from util.map import Map
from util.coordinate import Coordinate
from util.settings import Settings
from util.state_manager import MapType, StartingCondition
from controller.command import CommandManager, Command, TaskManager, BuildTask, MoveTask, CollectAndDropTask, SpawnCommand
from controller.interactions import Interactions
from controller.AI_controller import AIController, AI
from model.player.player import Player
from model.buildings.town_center import TownCenter
from model.resources.wood import Wood
from model.resources.gold import Gold
from pygame import time
import threading
from model.player.strategy import Strategy1
import typing
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

    def __init__(self, menu_controller: 'MenuController') -> None:
        """
        Initializes the GameController with the given settings.

        :param menu_controller: The menu controller.
        :type menu_controller: MenuController
        """
        self.__menu_controller: 'MenuController' = menu_controller
        self.settings: Settings = self.__menu_controller.settings
        self.__command_list: list[Command] = []
        self.__players: list[Player] = []
        self.__map: Map = self.__generate_map()
        self.__ai_controller: AIController = AIController(self,1)
        self.__view_controller: ViewController = ViewController(self)
        self.__assign_AI()
        # self.__ai_controller: AIController = AIController(self)
        self.__running: bool = False
        game_thread = threading.Thread(target=self.game_loop)
        ai_thread = threading.Thread(target=self.__ai_controller.ai_loop)
        game_thread.start()
        ai_thread.start()
        
    def get_commandlist(self):
        return self.__command_list

        
        # self.__ai_controller.__ai_loop()
        self.game_loop()
        
    def __generate_players(self, number_of_player: int, map: Map ) -> None:
        """
        Generates the players based on the settings.
        """
        colors = ["blue", "red", "green", "yellow", "purple", "orange", "pink", "cyan"]
        for i in range(number_of_player):
            player = Player("Player " + str(i+1), colors[i])
            self.get_players().append(player)
            player.set_command_manager(CommandManager(map, player, self.settings.fps.value, self.__command_list))
            player.set_task_manager(TaskManager(player.get_command_manager()))

            option = StartingCondition(self.settings.starting_condition)
            if option == StartingCondition.LEAN:
                player.collect( Food(), 50 )
                player.collect( Wood(), 200 )
                player.collect( Gold(), 50 )
            elif option == StartingCondition.MEAN:
                player.collect( Food(), 2000 )
                player.collect( Wood(), 2000 )
                player.collect( Gold(), 2000 )
            elif option == StartingCondition.MARINES:
                player.collect( Food(), 20000 )
                player.collect( Wood(), 20000 )
                player.collect( Gold(), 20000 )
    
    def __assign_AI(self)-> None:
        for player in self.get_players():
            player.set_ai(AI(player,None, map))
            player.get_ai().set_strategy(Strategy1(player.get_ai(), 5))
            print(f"Player {player.get_name()} has strat {player.get_ai().get_strategy()}")
            player.update_centre_coordinate()

        
    def __generate_map(self) -> Map:
        """
        Generates a map based on the settings.

        :return: The generated map.
        :rtype: Map
        """
        map_generation: Map = Map(self.settings.map_size.value)

        # Temporary: Create a Building called "Center" at the center of the map
        # Note: It will be size 1, except if the map size is even (it will be size 2 in this case)
        # from model.buildings.building import Building
        # center_size = 2 if map_generation.get_size() % 2 == 0 else 1
        # center_coordinate = Coordinate((map_generation.get_size() - center_size) // 2, (map_generation.get_size() - center_size) // 2)
        # center = Building("Center", "C", 1, {}, center_size, 0)
        # map_generation.add(center, center_coordinate)
        # center.set_coordinate(center_coordinate)

        # Generate the players:
        # Place the town center of the first player at random position, far from the center (30% of map size).
        # Place the 2nd player town center at the opposite side of the map.
        self.__generate_players(2, map_generation)
        interactions = Interactions(map_generation)
        first_player_coordinate = None
        min_distance = int(self.settings.map_size.value * 0.3)
        for player in self.get_players():
            town_center = TownCenter()
            interactions.link_owner(player, town_center)
            player.set_max_population(player.get_max_population() + town_center.get_capacity_increase())
            if player == self.get_players()[0]:
                while True:
                    coordinate = Coordinate(
                        random.randint(min_distance, self.settings.map_size.value - min_distance - 1),
                        random.randint(min_distance, self.settings.map_size.value - min_distance - 1)
                    )
                    if map_generation.check_placement(town_center, coordinate):
                        break
                first_player_coordinate = coordinate
            else:
                coordinate = Coordinate(
                    self.settings.map_size.value - 1 - first_player_coordinate.get_x() - town_center.get_size() + 1,
                    self.settings.map_size.value - 1 - first_player_coordinate.get_y() - town_center.get_size() + 1
                )
            
            map_generation.add(town_center, coordinate)
            town_center.set_coordinate(coordinate)
            interactions.link_owner(player, town_center)
            player.set_max_population(player.get_max_population() + town_center.get_capacity_increase())

        if MapType(self.settings.map_type) == MapType.RICH:
            # Wood need to occupe 5% of the map. It will be randomly placed
            wood = Wood()

            for _ in range(int(self.settings.map_size.value ** 2 * 0.05)):
                while True:
                    coordinate = Coordinate(random.randint(0, self.settings.map_size.value - 1), random.randint(0, self.settings.map_size.value - 1))
                    if map_generation.check_placement(wood, coordinate):
                        break

                map_generation.add(wood, coordinate)
                wood.set_coordinate(coordinate)
            
            # Gold need to occupe 0.5% of the map. It will be randomly placed
            for _ in range(int(self.settings.map_size.value ** 2 * 0.005)):
                gold = Gold()

                while True:
                    coordinate = Coordinate(random.randint(0, self.settings.map_size.value - 1), random.randint(0, self.settings.map_size.value - 1))
                    if map_generation.check_placement(gold, coordinate):
                        break

                map_generation.add(gold, coordinate)
                gold.set_coordinate(coordinate)
            
        if MapType(self.settings.map_type) == MapType.GOLD_CENTER:
            # Gold need to occupe 0.5% of the map. It will be placed in a circle at the center of the map.
            # Draw a circle that occupies 0.5% of the map and place gold in it.
            center = Coordinate(self.settings.map_size.value // 2, self.settings.map_size.value // 2)
            radius = int(self.settings.map_size.value * 0.05)
            for x in range(center.get_x() - radius, center.get_x() + radius + 1):
                for y in range(center.get_y() - radius, center.get_y() + radius + 1):
                    if (x - center.get_x()) ** 2 + (y - center.get_y()) ** 2 <= radius ** 2:
                        coordinate = Coordinate(x, y)
                        gold = Gold()
                        map_generation.add(gold, coordinate)
                        gold.set_coordinate(coordinate)
            
            # Wood need to occupe 5% of the map. It will be randomly placed
            for _ in range(int(self.settings.map_size.value ** 2 * 0.05)):
                wood = Wood()
                
                while True:
                    coordinate = Coordinate(random.randint(0, self.settings.map_size.value - 1), random.randint(0, self.settings.map_size.value - 1))
                    if map_generation.check_placement(wood, coordinate):
                        break
                
                map_generation.add(wood, coordinate)
                wood.set_coordinate(coordinate)
        
        if MapType(self.settings.map_type) == MapType.TEST:
            # Generate a test map 10x10 with a town center at (0,0) and a villager at (5,5)
            from model.units.villager import Villager
            map_generation = Map(120)
            interactions = Interactions(map_generation)
            self.__generate_players(2, map_generation) ## always in the creation of a new map, the players are generated before all generation of objects
            self.get_players()[0].collect( Wood(), 1000 )
            ## Init for player 1
            town_center1 = TownCenter()
            interactions.place_object(town_center1, Coordinate(0,0))
            interactions.link_owner(self.get_players()[0], town_center1)
            self.get_players()[0].set_max_population(self.get_players()[0].get_max_population()+town_center1.get_capacity_increase()) ## increase max population
            villager1 = Villager()
            interactions.place_object(villager1, Coordinate(5,5))
            interactions.link_owner(self.get_players()[0], villager1)
            town_center3 = TownCenter()
            villager1.set_task(BuildTask(self.get_players()[0].get_command_manager(), villager1, Coordinate(6,6), town_center3))
            ## Init for player 2
            town_center2 = TownCenter()
            interactions.place_object(town_center2, Coordinate(100,100))
            interactions.link_owner(self.get_players()[1], town_center2)
            self.get_players()[1].set_max_population(self.get_players()[1].get_max_population()+town_center2.get_capacity_increase())
            villager2 = Villager()
            interactions.place_object(villager2, Coordinate(90,90))
            interactions.link_owner(self.get_players()[1], villager2)
        return map_generation
    
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
    
    def pause(self) -> None:
        """Pauses the game."""
        self.__running = False
    
    def exit(self) -> None:
        """Exits the game."""
        self.__running = False
        self.__ai_controller.exit()
        self.__menu_controller.exit()

    # TODO: Generate list of players and their units/buildings.
    def update(self) -> None:
        """
        Update the game state.
        """
        for command in self.__command_list.copy():
            try:
                #print(f"Command {command} is being executed")
                command.run_command()
            except (ValueError, AttributeError) as e:
               #print(e)
                #print("Command failed.")
                command.remove_command_from_list(self.__command_list)
                command.get_entity().set_task(None)
                #exit()

    
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
                time.Clock().tick(self.settings.fps.value)
