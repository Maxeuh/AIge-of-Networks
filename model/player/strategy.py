from abc import ABC, abstractmethod
import random
from util.coordinate import Coordinate
from util.map import Map
from controller.command import Task, CollectAndDropTask, MoveTask, KillTask, SpawnTask, BuildTask, UnitSpawner
from model.units.villager import Villager
from model.units.unit import Unit
from model.buildings.barracks import Barracks
from model.buildings.farm import Farm
from model.units.swordsman import Swordsman
from model.buildings.town_center import TownCenter
from model.buildings.house import House
from model.buildings.building import Building
from model.player.player import Player
from model.resources.resource import Resource
import typing
if typing.TYPE_CHECKING:
    from controller.AI_controller import AI


from abc import ABC, abstractmethod
from util.coordinate import Coordinate
from util.map import Map
from controller.command import Task, CollectAndDropTask, MoveTask, KillTask, SpawnTask, BuildTask, UnitSpawner
from model.units.villager import Villager
from model.units.unit import Unit
from model.buildings.barracks import Barracks
from model.buildings.farm import Farm
from model.units.swordsman import Swordsman
from model.buildings.town_center import TownCenter
from model.buildings.house import House
from model.buildings.building import Building
from model.player.player import Player
from model.resources.resource import Resource
#Strategy1
class Strategy(ABC):
    def __init__(self,ai:'AI'):
        self.__ai= ai
    @abstractmethod
    def execute(self):
        pass
    def get_ai(self):
        return self.__ai

class Strategy1(Strategy):
    """
    This is the first strategy
    where player will switch between 2 modes Defend, Attack base on the conditions:
     The difference between the player's number of units and the nearest enemy's number of units
    the nearest enemy is the enemy that is compared by the distance between the player's first building and the enemy's first building (in the list)
    """
    DEFEND = 0
    ATTACK = 1
    def __init__(self,ai: 'AI', unit_difference:int):
        super().__init__(ai)
        self.__unit_difference: int = unit_difference
        self.__mode = self.DEFEND
        self.__target_player = None
        self.__villager_task_count = 0
  
    def execute(self): ## run every AI-loop
        if not self.get_ai().get_enemies():
            self.random_actions()
        else:
            self.analyse()
            if self.__mode == self.DEFEND:
                self.defend()
            elif self.__mode == self.ATTACK:
                self.attack()

    def analyse(self):
        if not self.get_ai().get_enemies():
            self.random_actions()
        else:
        
            self.__target_player: Player = self.find_target_player()
            unit_difference: int = self.get_ai().get_player().get_unit_count() - self.__target_player.get_unit_count()
            if self.__unit_difference <= unit_difference or self.get_ai().get_player().get_unit_count() >= 0.3 * self.get_ai().get_player().get_max_population():
                self.__mode = self.ATTACK
            else:
                self.__mode = self.DEFEND

    def find_target_player(self):
        if not self.get_ai().get_enemies():
            self.random_actions()
        else:
            ai: 'AI' = self.get_ai()
            player: Player = ai.get_player()
            target_player: Player = None
            player_coord: Coordinate = self.get_ai().get_player().get_centre_coordinate()
            target_distance: int = 999999
            for enemy in ai.get_enemies():
                avg_coord: Coordinate = enemy.get_centre_coordinate()
                distance = player_coord.distance(avg_coord)
                if distance < target_distance:
                    target_distance = distance
                    target_player = enemy
            return target_player

    def defend(self):
        if not self.get_ai().get_enemies():
            self.random_actions()
        else:
            
            villagers = [u for u in self.get_ai().get_player().get_units() if isinstance(u, Villager) and u.get_task() is None]
            center_coordinate = self.get_ai().get_player().get_centre_coordinate()
            build_points = self.get_ai().get_map_known().find_nearest_empty_zones(center_coordinate, TownCenter().get_size())
            collect_points = self.get_ai().get_map_known().find_nearest_objects(center_coordinate, Resource) 
            for i, villager in enumerate(villagers):
                match self.__villager_task_count% 3:
                    case 0:
                        if all(self.get_ai().get_player().check_consume(resource, amount) for resource, amount in Farm().get_cost().items()) and build_points:
                            self.build(Farm(), villager, build_points[(i//3) % len(build_points)])
                        elif collect_points:
                            self.collect(villager,collect_points[(i//3) % len(collect_points)])
                    case 1:
                        if all(self.get_ai().get_player().check_consume(resource, amount) for resource, amount in House().get_cost().items()) and build_points:
                            self.build(House(), villager, build_points[(i//3) + 1 % len(build_points)])
                        elif collect_points:
                            self.collect(villager,collect_points[(i//3) % len(collect_points)])
                    case 2:
                        if collect_points:
                            self.collect(villager,collect_points[(i//3) % len(collect_points)])
            self.__villager_task_count += 1
            self.spawnAll(TownCenter)
            self.dispatchAttackers(Swordsman)


    def attack(self):
        if not self.get_ai().get_enemies():
            self.random_actions()
        else:
            
            villagers = [u for u in self.get_ai().get_player().get_units() if isinstance(u, Villager) and u.get_task() is None]
            center_coordinate = self.get_ai().get_player().get_centre_coordinate()
            build_points = self.get_ai().get_map_known().find_nearest_empty_zones(center_coordinate, TownCenter().get_size())
            collect_points = self.get_ai().get_map_known().find_nearest_objects(center_coordinate, Resource) 
            for i, villager in enumerate(villagers):
                match self.__villager_task_count% 2:
                    case 0:
                        if all(self.get_ai().get_player().check_consume(resource, amount) for resource, amount in Barracks().get_cost().items()) and build_points:
                            self.build(Barracks(), villager, build_points[(i//3) % len(build_points)])
                        elif all(self.get_ai().get_player().check_consume(resource, amount) for resource, amount in Farm().get_cost().items()) and build_points:
                            self.build(Farm(), villager, build_points[(i//3) % len(build_points)])
                        elif collect_points:
                            self.collect(villager,collect_points[(i//3) % len(collect_points)])
                    case 1:
                        if all(self.get_ai().get_player().check_consume(resource, amount) for resource, amount in Farm().get_cost().items()) and build_points:
                            self.build(House(), villager, build_points[(i//3) + 1 % len(build_points)])
                        elif collect_points:
                            self.collect(villager,collect_points[(i//3) % len(collect_points)])
            self.__villager_task_count += 1
            self.spawnAll(TownCenter)
            self.dispatchAttackers(Swordsman)
            self.spawnAll(Barracks)

    def collect(self, villager: Villager, collect_point: Coordinate):

            
            u = villager
            drop_point = next(( drop_coord for drop_coord in self.get_ai().get_map_known().find_nearest_objects(u.get_coordinate(), Building) if self.get_ai().get_map_known().get(drop_coord).is_resources_drop_point() and self.get_ai().get_map_known().get(drop_coord).get_player() == self.get_ai().get_player() ), None)
            #print(f"Villager {u} is collecting {self.get_ai().get_map_known().get(collect_point)} and dropping at {self.get_ai().get_map_known().get(drop_point)}")
            if drop_point and collect_point: 
                u.set_task(CollectAndDropTask(self.get_ai().get_player().get_command_manager(), u, collect_point, drop_point))
    
    def build(self, building: Building, villager: Villager, build_point: Coordinate):

            task =BuildTask(self.get_ai().get_player().get_command_manager(), villager, build_point, building)
            villager.set_task(task)

    def spawn(self, building: Building):

                task = SpawnTask(self.get_ai().get_player().get_command_manager(), building)
                building.set_task(task)
    
    def kill(self,unit: Unit, target_coord: Coordinate):
        if not self.get_ai().get_enemies():
            self.random_actions()
        else:
            task = KillTask(self.get_ai().get_player().get_command_manager(), unit, target_coord)
            unit.set_task(task)

    def dispatchAttackers(self, object_type: type)->None:
        if not self.get_ai().get_enemies():
            self.random_actions()
        else:
            units = [u for u in self.get_ai().get_player().get_units() if isinstance(u, object_type) and u.get_task() is None]
            targets = self.get_ai().get_map_known().find_nearest_enemies(self.get_ai().get_player().get_centre_coordinate(), self.__target_player)
            for i, unit in enumerate(units):
                if i < len(targets):
                    self.kill(unit, targets[i])
                else:
                    self.kill(unit, targets[0])
    
    def spawnAll(self, object_type: type):

            buildings = [b for b in self.get_ai().get_player().get_buildings() if isinstance(b, object_type) and b.get_task() is None]
            unit = UnitSpawner()[object_type().get_name()]
            for building in buildings:
                    if all(self.get_ai().get_player().get_resources().get(key, 0) >= cost for key, cost in unit.get_cost().items()) and self.get_ai().get_player().get_unit_count() < self.get_ai().get_player().get_max_population():
                        self.spawn(building)
                    
    # Add a new method for random actions when no enemies are present
    def random_actions(self):
        # Random actions for villagers
        villagers = [u for u in self.get_ai().get_player().get_units() if isinstance(u, Villager) and u.get_task() is None]
        center_coordinate = self.get_ai().get_player().get_centre_coordinate()
        build_points = self.get_ai().get_map_known().find_nearest_empty_zones(center_coordinate, TownCenter().get_size())
        collect_points = self.get_ai().get_map_known().find_nearest_objects(center_coordinate, Resource)
        
        # Setup possible building types for random construction
        building_types = [Farm, House, Barracks]
        
        for villager in villagers:
            # Random choice between collecting, building, or exploring
            action = random.randint(0, 2)
            
            if action == 0 and collect_points:  # Collect resources
                self.collect(villager, random.choice(collect_points))
            elif action == 1 and build_points:  # Build random building
                building_class = random.choice(building_types)
                if all(self.get_ai().get_player().check_consume(resource, amount) for resource, amount in building_class().get_cost().items()):
                    self.build(building_class(), villager, random.choice(build_points))
            # action == 2 is explore - villager will remain without task and get a new one next cycle
        
        # Random spawning from buildings
        spawn_buildings = [b for b in self.get_ai().get_player().get_buildings() 
                         if (isinstance(b, TownCenter) or isinstance(b, Barracks)) 
                         and b.get_task() is None]
        
        for building in spawn_buildings:
            if random.random() < 0.3:  # 30% chance to spawn
                self.spawn(building)
        
        # Random movements for military units
        military_units = [u for u in self.get_ai().get_player().get_units() 
                        if isinstance(u, Swordsman) and u.get_task() is None]
        
        map_size = self.get_ai().get_map_known().get_size()
        for unit in military_units:
            # Choose random coordinates to explore
            random_x = random.randint(0, map_size.get_width() - 1)
            random_y = random.randint(0, map_size.get_height() - 1)
            random_coord = Coordinate(random_x, random_y)
            task = MoveTask(self.get_ai().get_player().get_command_manager(), unit, random_coord)
            unit.set_task(task)
         