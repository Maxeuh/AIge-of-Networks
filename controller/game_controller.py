import json
import random
import threading
import typing

from pygame import time

from controller.ai_controller import AIController
from controller.command_controller import CommandController
from controller.network_controller import NetworkController
from model.buildings.barracks import Barracks
from model.buildings.building import Building
from model.buildings.farm import Farm
from model.buildings.house import House
from model.game_object import GameObject
from model.interactions import Interactions
from controller.task_manager import TaskController
from controller.view_controller import ViewController
from model.ai import AI
from model.buildings.town_center import TownCenter
from model.commands.command import Command
from model.player.player import Player
from model.player.strategies.random_strategy import RandomStrategy
from model.resources.food import Food
from model.resources.gold import Gold
from model.resources.resource import Resource
from model.resources.wood import Wood
from model.tasks.build_task import BuildTask
from model.units.archer import Archer
from model.units.horseman import Horseman
from model.units.swordsman import Swordsman
from model.units.unit import Unit
from model.units.villager import Villager
from util.coordinate import Coordinate
from util.map import Map
from util.settings import Settings
from util.state_manager import InteractionsTypes, MapType, StartingCondition

if typing.TYPE_CHECKING:
    from controller.menu_controller import MenuController
import uuid


class GameController:
    """This module is responsible for controlling the game."""

    _instance = None

    @staticmethod
    def get_instance(menu_controller: "MenuController"):
        if GameController._instance is None:
            GameController._instance = GameController(menu_controller)
        return GameController._instance

    def __init__(self, menu_controller: "MenuController", load: bool = False) -> None:
        """
        Initializes the GameController with the given settings.

        :param menu_controller: The menu controller.
        :type menu_controller: MenuController
        """
        self.__colors: list[str] = [
            "blue",
            "red",
            "green",
            "yellow",
            "purple",
            "orange",
            "pink",
            "cyan",
        ]
        self.__network_controller: NetworkController = NetworkController()
        self.__menu_controller: "MenuController" = menu_controller
        self.settings: Settings = self.__menu_controller.settings
        self.__command_list: list[Command] = []
        self.__players: list[Player] = []
        self.__map: Map = self.__generate_map()
        self.__ai_controller: AIController = AIController(self, 1)
        self.__assign_AI()
        self.__running: bool = False
        if not load:
            self.__game_thread = threading.Thread(target=self.game_loop)
            self.__ai_thread = threading.Thread(target=self.__ai_controller.ai_loop)
            self.__view_controller: ViewController = ViewController(self)
            self.__game_thread.start()
            self.__ai_thread.start()
            self.__view_controller.start_view()
        else:
            self.__game_thread = None
            self.__ai_thread = None
            self.__view_controller = None

    def start_all_threads(self):
        self.__game_thread = threading.Thread(target=self.game_loop)
        self.__ai_thread = threading.Thread(target=self.__ai_controller.ai_loop)
        self.__view_controller: ViewController = ViewController(self)
        self.__game_thread.start()
        self.__ai_thread.start()
        self.__view_controller.start_view()

    def get_commandlist(self):
        return self.__command_list

    def __generate_player(self, player_id: uuid.UUID, game_map: Map) -> Player:
        """
        Generates a player based on the settings.
        """
        if len(self.__colors) == 0:
            self.__colors = [
                "blue",
                "red",
                "green",
                "yellow",
                "purple",
                "orange",
                "pink",
                "cyan",
            ]
        player = Player(str(player_id), self.__colors.pop(0))
        self.get_players().append(player)
        player.set_command_manager(
            CommandController(
                game_map,
                player,
                self.settings.fps.value,
                self.__command_list,
                self.__network_controller,
            )
        )
        player.set_task_manager(TaskController(player.get_command_manager()))
        player.set_max_population(5000)

        return player

    def __assign_AI(self) -> None:
        for player in self.get_players():
            player.set_ai(AI(player, None, self.__map))

            player.get_ai().set_strategy(RandomStrategy(player.get_ai()))

            # Initialize player coordinate for AI navigation
            player.update_centre_coordinate()

            # Rest of resources assignment...
            option = StartingCondition(self.settings.starting_condition)
            if option == StartingCondition.LEAN:
                player.collect(Food(), 50)
                player.collect(Wood(), 200)
                player.collect(Gold(), 50)
            elif option == StartingCondition.MEAN:
                player.collect(Food(), 2000)
                player.collect(Wood(), 2000)
                player.collect(Gold(), 2000)
            # elif option == StartingCondition.MARINES:
            #     player.collect( Food(), 20000 )
            #     player.collect( Wood(), 20000 )
            #     player.collect( Gold(), 20000 )

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
        self.__generate_player(uuid.uuid4(), map_generation)
        interactions = Interactions(map_generation, self.__network_controller)
        min_distance = int(self.settings.map_size.value * 0.3)
        player = self.get_players()[0]
        town_center = TownCenter()
        while True:
            # Get a random coordinate. If it is at less than min_distance from the center, try again.
            center_size = 2 if map_generation.get_size() % 2 == 0 else 1
            center_coordinate = Coordinate(
                (map_generation.get_size() - center_size) // 2,
                (map_generation.get_size() - center_size) // 2,
            )
            coordinate = Coordinate(
                (map_generation.get_size() - center_size) // 2,
                (map_generation.get_size() - center_size) // 2,
            )
            while coordinate.distance(center_coordinate) < min_distance:
                coordinate = Coordinate(
                    random.randint(0, self.settings.map_size.value - 1),
                    random.randint(0, self.settings.map_size.value - 1),
                )
            if map_generation.check_placement(town_center, coordinate):
                break

        # Place the town center and link it to the player
        interactions.place_object(town_center, coordinate)
        interactions.link_owner(player, town_center)
        player.set_max_population(
            player.get_max_population() + town_center.get_capacity_increase()
        )

        # Generate a list of coordinates around the town center (not inside it)
        around_coordinates = []
        for x in range(
            coordinate.get_x() - 1, coordinate.get_x() + town_center.get_size() + 1
        ):
            for y in range(
                coordinate.get_y() - 1, coordinate.get_y() + town_center.get_size() + 1
            ):
                if (
                    x < 0
                    or y < 0
                    or x >= self.settings.map_size.value
                    or y >= self.settings.map_size.value
                ):
                    continue
                if (
                    x < coordinate.get_x()
                    or x > coordinate.get_x() + town_center.get_size()
                    or y < coordinate.get_y()
                    or y > coordinate.get_y() + town_center.get_size()
                ):
                    around_coordinates.append(Coordinate(x, y))

        # Place 3 villagers for the player, at random positions around the town center
        for _ in range(3):
            villager = Villager()
            # Get a random coordinate from the list and check placement
            while True:
                coordinate = around_coordinates.pop(
                    random.randint(0, len(around_coordinates) - 1)
                )
                if map_generation.check_placement(villager, coordinate):
                    break

            # Place the villager and link it to the player
            interactions.place_object(villager, coordinate)
            interactions.link_owner(player, villager)

        if MapType(self.settings.map_type) == MapType.RICH:
            # Wood need to occupe 5% of the map. It will be randomly placed
            wood = Wood()

            for _ in range(int(self.settings.map_size.value**2 * 0.05)):
                while True:
                    coordinate = Coordinate(
                        random.randint(0, self.settings.map_size.value - 1),
                        random.randint(0, self.settings.map_size.value - 1),
                    )
                    if map_generation.check_placement(wood, coordinate):
                        break

                map_generation.add(wood, coordinate)
                wood.set_coordinate(coordinate)

            # Gold need to occupe 0.5% of the map. It will be randomly placed
            for _ in range(int(self.settings.map_size.value**2 * 0.005)):
                gold = Gold()

                while True:
                    coordinate = Coordinate(
                        random.randint(0, self.settings.map_size.value - 1),
                        random.randint(0, self.settings.map_size.value - 1),
                    )
                    if map_generation.check_placement(gold, coordinate):
                        break

                map_generation.add(gold, coordinate)
                gold.set_coordinate(coordinate)

        if MapType(self.settings.map_type) == MapType.GOLD_CENTER:
            # Gold need to occupe 0.5% of the map. It will be placed in a circle at the center of the map.
            # Draw a circle that occupies 0.5% of the map and place gold in it.
            center = Coordinate(
                self.settings.map_size.value // 2, self.settings.map_size.value // 2
            )
            radius = int(self.settings.map_size.value * 0.05)
            for x in range(center.get_x() - radius, center.get_x() + radius + 1):
                for y in range(center.get_y() - radius, center.get_y() + radius + 1):
                    if (x - center.get_x()) ** 2 + (
                        y - center.get_y()
                    ) ** 2 <= radius**2:
                        coordinate = Coordinate(x, y)
                        gold = Gold()
                        map_generation.add(gold, coordinate)
                        gold.set_coordinate(coordinate)

            # Wood need to occupe 5% of the map. It will be randomly placed
            for _ in range(int(self.settings.map_size.value**2 * 0.05)):
                wood = Wood()

                while True:
                    coordinate = Coordinate(
                        random.randint(0, self.settings.map_size.value - 1),
                        random.randint(0, self.settings.map_size.value - 1),
                    )
                    if map_generation.check_placement(wood, coordinate):
                        break

                map_generation.add(wood, coordinate)
                wood.set_coordinate(coordinate)

        if MapType(self.settings.map_type) == MapType.TEST:
            # Generate a test map 10x10 with a town center at (0,0) and a villager at (5,5)
            map_generation = Map(120)
            interactions = Interactions(map_generation, self.__network_controller)
            self.__generate_player(uuid.uuid4(), map_generation)
            ## always in the creation of a new map, the players are generated before all generation of objects
            self.__generate_player(uuid.uuid4(), map_generation)
            self.get_players()[0].collect(Wood(), 1000)
            ## Init for player 1
            town_center1 = TownCenter()
            interactions.place_object(town_center1, Coordinate(0, 0))
            interactions.link_owner(self.get_players()[0], town_center1)
            self.get_players()[0].set_max_population(
                self.get_players()[0].get_max_population()
                + town_center1.get_capacity_increase()
            )  ## increase max population
            villager1 = Villager()
            interactions.place_object(villager1, Coordinate(5, 5))
            interactions.link_owner(self.get_players()[0], villager1)
            town_center3 = TownCenter()
            villager1.set_task(
                BuildTask(
                    self.get_players()[0].get_command_manager(),
                    villager1,
                    Coordinate(6, 6),
                    town_center3,
                )
            )
            ## Init for player 2
            town_center2 = TownCenter()
            interactions.place_object(town_center2, Coordinate(100, 100))
            interactions.link_owner(self.get_players()[1], town_center2)
            self.get_players()[1].set_max_population(
                self.get_players()[1].get_max_population()
                + town_center2.get_capacity_increase()
            )
            villager2 = Villager()
            interactions.place_object(villager2, Coordinate(90, 90))
            interactions.link_owner(self.get_players()[1], villager2)
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
        # Send initial map data first

        # Then initialize AI to prevent command data being sent before map data
        self.__assign_AI()

    def exit(self) -> None:
        """Exits the game."""
        self.__running = False
        self.__ai_controller.exit()
        self.__network_controller.send(
            {
                "action": InteractionsTypes.EXIT.value,
                "player": {
                    "name": self.__players[0].get_name(),
                    "center": self.__players[0].get_centre_coordinate().__str__(),
                },
            }
        )
        self.__network_controller.close()
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
                # print(f"Command {command} is being executed")
                command.run_command()
            except (ValueError, AttributeError):
                # print(e)
                # print("Command failed.")
                command.remove_command_from_list(self.__command_list)
                command.get_entity().set_task(None)
                # exit()

    def load_task(self) -> None:
        """
        Load the task of the player.
        serves as the player's input
        """
        for player in self.__players:
            # for unit in player.get_units():
            #     # print(f"Unit {unit.get_name()} has {unit.get_task()} at {unit.get_coordinate()}")
            #     pass
            player.get_task_manager().execute_tasks()

    def game_loop(self) -> None:
        try:
            self.start()
            while self.__running:
                self.load_task()
                self.update()
                self.network_interactions()
                time.Clock().tick(self.settings.fps.value * self.get_speed())
        except Exception as e:
            raise RuntimeError(f"Game loop failed: {e}")

    def resume(self) -> None:
        """
        Resumes the game.
        """
        self.start()
        if self.__game_thread is None or not self.__game_thread.is_alive():
            self.__game_thread = threading.Thread(target=self.game_loop)
            self.__game_thread.start()
        if self.__ai_thread is None or not self.__ai_thread.is_alive():
            self.__ai_thread = threading.Thread(target=self.__ai_controller.ai_loop)
            self.__ai_thread.start()
        self.__view_controller.start_view()

    def load_game(
        self, game_map: Map, players: list[Player], command_list: list[Command]
    ) -> None:
        """
        Load the game with the given map, players and settings.

        :param map: The map.
        :type map: Map
        :param players: The players.
        :type players: list[Player]
        """
        self.__map = game_map
        self.__players = players
        self.__running = True
        self.__command_list = command_list
        self.__ai_controller.load(self)

        # Initialize view_controller if it is None
        if self.__view_controller is None:
            self.__view_controller = ViewController(self)

        # Initialize game_thread and ai_thread
        if self.__game_thread is None:
            self.__game_thread = threading.Thread(target=self.game_loop)
        if self.__ai_thread is None:
            self.__ai_thread = threading.Thread(target=self.__ai_controller.ai_loop)

        self.__view_controller.start_view()

    def get_network_controller(self) -> NetworkController:
        """
        Returns the network controller.
        :return: The network controller.
        :rtype: NetworkController
        """
        return self.__network_controller

    def get_player_with_name(self, player_name: str) -> typing.Optional[Player]:
        for player in self.__players:
            if str(player.get_name()) == str(player_name):
                return player
        return None

    def player_leave(self, player: Player):
        self.__players.remove(player)

    def get_building(self, id: int, player: Player) -> typing.Optional[Building]:
        return next((b for b in player.get_buildings() if b.get_id() == id), None)

    def get_unit(self, id: int, player: Player) -> typing.Optional[Unit]:
        return next((u for u in player.get_units() if u.get_id() == id), None)

    def get_ressource(self, id: int) -> typing.Optional[Resource]:
        return self.__map.get_object(id)

    def create_object(self, name: str) -> GameObject:
        object_classes = {
            "Barracks": Barracks,
            "Farm": Farm,
            "House": House,
            "Town Center": TownCenter,
            "Food": Food,
            "Gold": Gold,
            "Wood": Wood,
            "Archer": Archer,
            "Horseman": Horseman,
            "Swordsman": Swordsman,
            "Villager": Villager,
        }
        if name == "Place Holder":
            return GameObject("Place Holder", "x", 9999)
        return object_classes.get(name, GameObject)()

    def network_interactions(self) -> None:
        interactions = self.__network_controller.receive()
        for interaction in interactions:
            action = InteractionsTypes(interaction["action"])
            player = self.get_player_with_name(
                interaction.get("player", {}).get("name", "")
            )
            if not player and "player" in interaction:
                player = self.__generate_player(
                    interaction["player"]["name"], self.__map
                )

            if action == InteractionsTypes.PLACE_OBJECT:
                self.__handle_place_object(interaction)
            elif action == InteractionsTypes.REMOVE_OBJECT:
                self.__handle_remove_object(interaction)
            elif action == InteractionsTypes.MOVE_UNIT:
                self.__handle_move_unit(interaction, player)
            elif action == InteractionsTypes.ATTACK:
                self.__handle_attack(interaction, player)
            elif action == InteractionsTypes.COLLECT_RESOURCE:
                self.__handle_collect_resource(interaction)
            elif action == InteractionsTypes.DROP_RESOURCE:
                self.__handle_drop_resource(interaction)
            elif action == InteractionsTypes.LINK_OWNER:
                self.__handle_link_owner(interaction, player)
            elif action == InteractionsTypes.EXIT:
                self.player_leave(player)

    def __handle_place_object(self, interaction: list):
        pass
        obj = self.create_object(interaction["game_object"]["name"])
        if obj.get_name() == "Place Holder":
            obj.set_size(interaction["game_object"]["size"])
        coordinate = Coordinate(
            *map(int, interaction["game_object"]["coordinate"].strip("()").split(","))
        )
        obj.set_id(interaction["game_object"]["id"])
        obj.set_coordinate(coordinate)
        size = obj.get_size()
        for i in range(size):
            for j in range(size):
                map_object = self.__map.get(
                    Coordinate(coordinate.get_x() + i, coordinate.get_y() + j)
                )
                if (map_object):
                    self.__map.remove(
                        Coordinate(coordinate.get_x() + i, coordinate.get_y() + j)
                    )

        self.__map.add(obj, coordinate)

    def __handle_remove_object(self, interaction):
        coordinate = Coordinate(
            *map(int, interaction["coordinate"].strip("()").split(","))
        )
        object = self.__map.get(coordinate)
        if object and object.get_id() == interaction["id"]:
            self.__map.remove(coordinate)

    def __handle_move_unit(self, interaction: list, player: Player):
        unit = self.get_unit(interaction["unit"]["id"], player)
        coordinate = Coordinate(
            *map(int, interaction["unit"]["coordinate"].strip("()").split(","))
        )
        if not unit:
            unit = self.create_object(interaction["unit"]["name"])
            unit.set_id(interaction["unit"]["id"])
            player.add_unit(unit)
            unit.set_coordinate(coordinate)
            object = self.__map.get(coordinate)
            if object and object.get_id() != interaction["unit"]["id"]:
                self.__map.remove(coordinate)
            temp = self.__map.get(coordinate)
            self.__map.add(unit, coordinate)
        else:
            object = self.__map.get(coordinate)
            if self.__map.get(unit.get_coordinate()):
                self.__map.remove(unit.get_coordinate())
            if object and object.get_id() != interaction["unit"]["id"]:
                self.__map.remove(coordinate)
            unit.set_coordinate(coordinate)
            self.__map.force_move(unit, coordinate)

    def __handle_attack(self, interaction: list, player: Player):
        # {
        #     "action": InteractionsTypes.ATTACK.value,
        #     "player": attacker.get_player().get_name(),
        #     "attacker": {
        #         "id": id(attacker),
        #         "name": attacker.get_name(),
        #         "coordinate": attacker.get_coordinate().__str__(),
        #     },
        #     "target": {
        #         "id": id(target),
        #         "name": target.get_name(),
        #         "coordinate": target.get_coordinate().__str__(),
        #         "hp": target.get_hp,
        #     },
        # }
        pass
        # attacker = self.get_unit(interaction["attacker"]["id"], player)
        # target = self.get_unit(interaction["target"]["id"], player)
        # if not attacker:
        #     attacker = self.create_object(interaction["attacker"]["name"])
        #     attacker.set_id(interaction["attacker"]["id"])
        #     attacker.set_coordinate(
        #         Coordinate(
        #             *map(
        #                 int,
        #                 interaction["attacker"]["coordinate"].strip("()").split(","),
        #             )
        #         )
        #     )
        #     object = self.__map.get(attacker.get_coordinate())
        #     if object and object.get_id() != interaction["attacker"]["id"]:
        #         for i in range(object.get_size()):
        #             for j in range(object.get_size()):
        #                 if self.__map.get(
        #                     Coordinate(
        #                         attacker.get_coordinate().get_x() + i,
        #                         attacker.get_coordinate().get_y() + j,
        #                     )
        #                 ):
        #                     self.__map.remove(
        #                         Coordinate(
        #                             attacker.get_coordinate().get_x() + i,
        #                             attacker.get_coordinate().get_y() + j,
        #                         )
        #                     )
        #     self.__map.add(attacker, attacker.get_coordinate())
        #     player.add_unit(attacker)
        # if not target:
        #     target = self.create_object(interaction["target"]["name"])
        #     target.set_id(interaction["target"]["id"])
        #     target.set_coordinate(
        #         Coordinate(
        #             *map(
        #                 int, interaction["target"]["coordinate"].strip("()").split(",")
        #             )
        #         )
        #     )
        #     object = self.__map.get(target.get_coordinate())
        #     if object and object.get_id() != interaction["target"]["id"]:
        #         for i in range(object.get_size()):
        #             for j in range(object.get_size()):
        #                 if self.__map.get(
        #                     Coordinate(
        #                         target.get_coordinate().get_x() + i,
        #                         target.get_coordinate().get_y() + j,
        #                     )
        #                 ):
        #                     self.__map.remove(
        #                         Coordinate(
        #                             target.get_coordinate().get_x() + i,
        #                             target.get_coordinate().get_y() + j,
        #                         )
        #                     )
        #     self.__map.add(target, target.get_coordinate())
        #     self.__players[0].add_unit(target)
        # target.damage(attacker.get_attack_per_second())

        # if not target.is_alive():
        #     self.remove_object(target)
        #     owner = target.get_player()
        #     if isinstance(target, Building) and target.is_population_increase():
        #         owner.set_max_population(
        #             owner.get_max_population() - target.get_capacity_increase()
        #         )
        #     target.set_player(None)
        #     if isinstance(target, Building):
        #         owner.remove_building(target)
        #     if isinstance(target, Unit):
        #         owner.remove_unit(target)

    def __handle_collect_resource(self, interaction: list):
        # {
        #     "action": InteractionsTypes.COLLECT_RESOURCE.value,
        #     "player": villager.get_player().get_name(),
        #     "villager": {
        #         "id": id(villager),
        #         "name": villager.get_name(),
        #         "coordinate": villager.get_coordinate().__str__(),
        #     },
        #     "resource": {
        #         "id": id(resource),
        #         "name": resource.get_name(),
        #         "coordinate": resource.get_coordinate().__str__(),
        #         "hp": resource.get_hp(),
        #     },
        #     "amount": amount,
        # }
        pass

    def __handle_drop_resource(self, interaction: list):
        # {
        #     "action": InteractionsTypes.DROP_RESOURCE.value,
        #     "player": player.get_name(),
        #     "villager": {
        #         "id": id(villager),
        #         "name": villager.get_name(),
        #         "coordinate": villager.get_coordinate().__str__(),
        #     },
        #     "target": {
        #         "id": id(target),
        #         "name": target.get_name(),
        #         "coordinate": target.get_coordinate().__str__(),
        #     },
        #     "resources": collected_resources,
        # }
        pass

    def __handle_link_owner(self, interaction: list, player: Player):
        entity = self.create_object(interaction["entity"]["name"])
        coordinate = Coordinate(
            *map(int, interaction["entity"]["coordinate"].strip("()").split(","))
        )
        if not entity:
            entity = self.create_object(interaction["entity"]["name"])
            entity.set_id(interaction["entity"]["id"])
            entity.set_coordinate(coordinate)
            object = self.__map.get(coordinate)
            for i in range(object.get_size()):
                for j in range(object.get_size()):
                    if self.__map.get(
                        Coordinate(coordinate.get_x() + i, coordinate.get_y() + j)
                    ):
                        self.__map.remove(
                            Coordinate(coordinate.get_x() + i, coordinate.get_y() + j)
                        )
            temp = self.__map.get(coordinate)
            self.__map.add(entity, coordinate)
            if isinstance(entity, Unit):
                player.add_unit(entity)
            elif isinstance(entity, Building):
                player.add_building(entity)
        else:
            entity.set_coordinate(coordinate)
            if isinstance(entity, Unit) and entity not in player.get_units():
                object = self.__map.get(coordinate)
                if object and object.get_id() != interaction["entity"]["id"]:
                    for i in range(object.get_size()):
                        for j in range(object.get_size()):
                            self.__map.remove(
                                Coordinate(
                                    coordinate.get_x() + i, coordinate.get_y() + j
                                )
                            )
                self.__map.force_move(entity, coordinate)
                player.add_unit(entity)
            elif isinstance(entity, Building) and entity not in player.get_buildings():
                player.add_building(entity)
