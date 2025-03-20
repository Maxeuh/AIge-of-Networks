from controller.interactions import Interactions
from util.map import Map
from model.player.player import Player
from model.game_object import GameObject
from model.units.unit import Unit
from util.coordinate import Coordinate
from model.resources.resource import Resource
from model.units.villager import Villager
from model.units.horseman import Horseman
from model.units.swordsman import Swordsman
from model.units.archer import Archer
from model.buildings.building import Building
from model.entity import Entity
from enum import Enum
from abc import ABC, abstractmethod

class Process(Enum):
    """This class is responsible for storing the processes that can be executed."""
    SPAWN = 0
    MOVE = 1
    ATTACK = 2
    COLLECT = 3
    DROP = 4
    BUILD = 5

class UnitSpawner(dict[str, Unit]):
    """This class is responsible for storing the unit spawner."""
    def __init__(self) -> None:
        self["Town Center"] = Villager()
        self["Barracks"] = Swordsman()
        self["Archery Range"] = Archer()
        self["Stable"] = Horseman()
class Command(ABC):
    """This class is responsible for executing commands."""

    def __init__(self, map: Map, player: Player, entity: Entity, process: Process, convert_coeff: int ) -> None:
        """
        Initializes the Command with the given map, player, entity, process and convert_coeff.
        param map: The map where the command will be executed.
        :type map: Map
        :param player: The player that will execute the command.
        :type player: Player
        :param entity: The entity that will execute the command.
        :type entity: Entity
        :param process: The process that the command will execute.
        :type process: Process
        :param convert_coeff: The coefficient used to convert time to tick.
        :type convert_coeff: int

        """
        self.__interactions: Interactions = Interactions(map)
        self.__process: Process = process
        self.__player: Player = player
        self.__entity: Entity = entity
        self.__convert_coeff: int = convert_coeff
        self.__time: float = 0
        self.__tick: int = 0
    def get_interactions(self) -> Interactions:
        """
        Returns the interactions of the command.
        :return: The interactions of the command.
        :rtype: Interactions
        """
        return self.__interactions
    def get_tick(self) -> int:
        """
        Returns the tick of the command.
        :return: The tick of the command.
        :rtype: int
        """
        return self.__tick
    def set_tick(self, tick: int) -> None:
        """
        Sets the tick of the command.
        :param tick: The tick of the command.
        :type tick: int
        """
        self.__tick = tick
    
    def get_time(self) -> float:
        """
        Returns the time of the command.
        :return: The time of the command.
        :rtype: float
        """
        return self.__time
    
    def set_time(self, time: float) -> None:
        """
        Sets the time of the command.
        :param time: The time of the command.
        :type time: float
        """
        self.__time = time
    
    def get_entity(self) -> Entity:
        """
        Returns the entity that will execute the command.
        :return: The entity that will execute the command.
        :rtype: Entity
        """
        return self.__entity
    
    def get_process(self) -> Process:
        """
        Returns the process that the command will execute.
        :return: The process that the command will execute.
        :rtype: Process
        """
        return self.__process
    
    def get_player(self):
        """
        Returns the player that will execute the command.
        :return: The player that will execute the command.
        :rtype: Player
        """
        return self.__player
    def get_convert_coeff(self) -> int:
        """
        Returns the coefficient used to convert time to tick.
        :return: The coefficient used to convert time to tick.
        :rtype: int
        """
        return self.__convert_coeff
    def push_command_to_list(self, command_list: list['Command']) -> None:
        """
        Pushes the command to the given list.
        :param command_list: The list where the command will be pushed.
        :type command_list: list
        """
        for command in command_list:
            if command.get_entity() == self.__entity and not (command.get_process() == Process.SPAWN):
                if command.get_process() == Process.COLLECT or command.get_process() == Process.BUILD:
                    raise ValueError("Entity is already collecting or building.")
                if (command.get_process() == Process.ATTACK or command.get_process() == Process.MOVE) and command.get_process() == self.__process:
                    raise ValueError("Entity is cooling down from attacking or moving.")
        
        command_list.append(self)
    
    def remove_command_from_list(self, command_list: list['Command']) -> None:
        """
        Removes the command from the given list.
        :param command_list: The list where the command will be removed.
        :type command_list: list
        """
        if self in command_list:
            command_list.remove(self)

    @abstractmethod
    def run_command(self):
        """
        Runs the command.
        This method must be implemented by the subclasses.
        """
        pass
    def __repr__(self):
        return f"{self.get_entity()} of {self.get_player()} at {self.get_entity().get_coordinate()} doing {self.get_process()}. Tick: {self.get_tick()}. ///"
    

class SpawnCommand(Command):
    """This class is responsible for executing spawn commands."""

    def __init__(self, map: Map, player: Player, building: Building, target_coord: Coordinate, convert_coeff: int, command_list: list[Command]) -> None:
        """
        Initializes the SpawnCommand with the given map, player, building, target_coord and convert_coeff.
        :param map: The map where the command will be executed
        :type map: Map
        :param player: The player that will execute the command.
        :type player: Player
        :param building: The building that will execute the command.
        :type building: Building
        :param target_coord: The target coordinate where the entity will be spawned.
        :type target_coord: Coordinate
        :param convert_coeff: The coefficient used to convert time to tick.
        :type convert_coeff: int
        """
        super().__init__(map, player, building, Process.SPAWN, convert_coeff)
        self.set_time(UnitSpawner()[building.get_name()].get_spawning_time())
        self.set_tick(int(self.get_time() * convert_coeff))
        self.__target_coord = target_coord
        self.__command_list = command_list
        self.__place_holder: GameObject = GameObject("Place Holder",'x',9999)
        self.__start: bool = True
        super().push_command_to_list(command_list)
        #print(f"Spawning {self} for {self.get_player().get_name()}, at {self.__target_coord}")
    def get_target_coord(self) -> Coordinate:
        """
        Returns the target coordinate where the entity will be spawned.
        :return: The target coordinate where the entity will be spawned.
        :rtype: Coordinate
        """
        return self.__target_coord
    def run_command(self):
        """
        Runs the spawn command.
        """
        #print(f"Spawning {self} for {self.get_player().get_name()}, {self.get_tick()} compared to {int(self.get_convert_coeff() * self.get_time())}")
        if self.__start:
            self.__start = False
            if self.get_player().get_unit_count() >= self.get_player().get_max_population():
                super().remove_command_from_list(self.__command_list)
                raise ValueError("Population limit reached.")
            if not all(self.get_player().check_consume(resource, amount) for resource, amount in UnitSpawner()[self.get_entity().get_name()].get_cost().items()):
                super().remove_command_from_list(self.__command_list)
                raise ValueError(f"Not enough resources. Needing {UnitSpawner()[self.get_entity().get_name()].get_cost()} while having {self.get_player().get_resources()}")
            if not self.get_interactions().get_map().check_placement(self.__place_holder, self.__target_coord):
                super().remove_command_from_list(self.__command_list)
                raise ValueError("Invalid placement.")
            for resource, amount in UnitSpawner()[self.get_entity().get_name()].get_cost().items():
                self.get_player().consume(resource, amount)
                #print(f"Player {self.get_player().get_name()} consumed {amount} {resource}")
            self.get_interactions().place_object(self.__place_holder, self.__target_coord)

        
        if self.get_tick() <= 0:
            if self in self.__command_list:
                self.get_interactions().remove_object(self.__place_holder)
                spawned: Unit = UnitSpawner()[self.get_entity().get_name()]
                self.get_interactions().place_object(spawned, self.__target_coord)
                self.get_interactions().link_owner(self.get_player(), spawned)
                
                super().remove_command_from_list(self.__command_list)
            else:
                pass
        self.set_tick(self.get_tick() - 1)
class MoveCommand(Command):
    """This class is responsible for executing move commands."""
    
    def __init__(self, map: Map, player: Player, unit: Unit, target_coord: Coordinate, convert_coeff: int, command_list: list[Command]) -> None:
        """
        Initializes the MoveCommand with the given map, player, entity, process and convert_coeff.
        :param map: The map where the command will be executed.
        :type map: Map
        :param unit: The entity that will execute the command.
        :type unit: Unit
        :param process: The process that the command will execute.
        :type process: Process
        :param convert_coeff: The coefficient used to convert time to tick.
        :type convert_coeff: int
        """
        super().__init__(map, player, unit, Process.MOVE, convert_coeff)
        self.set_time(unit.get_speed())
        self.set_tick(int(self.get_time() * convert_coeff))
        self.__target_coord = target_coord
        self.__command_list = command_list
        self.__start: bool = True
        super().push_command_to_list(command_list)
    
    def run_command(self):
        """
        Runs the move command.
        """
        if self.__start:
            self.__start = False
            self.get_interactions().move_unit(self.get_entity(), self.__target_coord)
        if self.get_tick() <=0:
            super().remove_command_from_list(self.__command_list)
        self.set_tick(self.get_tick() - 1)
    
class AttackCommand(Command):
    """This class is responsible for executing attack commands."""
    
    def __init__(self, map: Map, player: Player, unit: Unit, target_coord: Coordinate, convert_coeff: int, command_list: list[Command]) -> None:
        """
        Initializes the AttackCommand with the given map, player, entity, process and convert_coeff.
        :param map: The map where the command will be executed
        :type map: Map
        :param player: The player that will execute the command.
        :type player: Player
        :param unit: The entity that will execute the command.
        :type unit: Unit
        :param target_coord: The target coordinate where the entity will attack.
        :type target_coord: Coordinate
        :param convert_coeff: The coefficient used to convert time to tick.
        :type convert_coeff: int
        """
        super().__init__(map, player, unit, Process.ATTACK, convert_coeff)
        self.set_time(1)
        self.set_tick(int(self.get_time() * convert_coeff))
        self.__target_coord = target_coord
        self.__command_list = command_list
        self.__start: bool = True
        super().push_command_to_list(command_list)
    
    def run_command(self):
        """
        Runs the attack command.
        """
        if self.__start:
            self.__start = False
            self.get_interactions().attack(self.get_entity(), self.__target_coord)
    
        if self.get_tick() <= 0:
            super().remove_command_from_list(self.__command_list)
        self.set_tick(self.get_tick() - 1)

class CollectCommand(Command):
    """This class is responsible for executing collect commands."""
    
    def __init__(self, map: Map, player: Player, unit: Villager, target_coord: Coordinate, convert_coeff: int, command_list: list[Command]) -> None:
        """
        Initializes the CollectCommand with the given map, player, entity, process and convert_coeff.
        :param map: The map where the command will be executed
        :type map: Map
        :param player: The player that will execute the command.
        :type player: Player
        :param unit: The entity that will execute the command.
        :type unit: Unit
        :param target_coord: The target coordinate where the entity will collect.
        :type target_coord: Coordinate
        :param convert_coeff: The coefficient used to convert time to tick.
        :type convert_coeff: int
        """
        super().__init__(map, player, unit, Process.COLLECT, convert_coeff)
        self.set_time(25.0/60)
        self.set_tick(int(self.get_time() * convert_coeff))
        self.__target_coord = target_coord
        self.__command_list = command_list
        super().push_command_to_list(command_list)
    
    def run_command(self):
        """
        Runs the collect command.
        """
        if self.get_tick() <= 0:
            if self in self.__command_list:
                self.get_interactions().collect_resource(self.get_entity(), self.__target_coord,1)
                super().remove_command_from_list(self.__command_list)
        self.set_tick(self.get_tick() - 1)

class DropCommand(Command):
    """This class is responsible for executing drop commands."""
    
    def __init__(self, map: Map, player: Player, unit: Villager, target_coord: Coordinate, convert_coeff: int, command_list: list[Command]) -> None:
        """
        Initializes the DropCommand with the given map, player, entity, process and convert_coeff.
        :param map: The map where the command will be executed
        :type map: Map
        :param player: The player that will execute the command.
        :type player: Player
        :param unit: The entity that will execute the command.
        :type unit: Unit
        :param target_coord: The target coordinate where the entity will drop.
        :type target_coord: Coordinate
        :param convert_coeff: The coefficient used to convert time to tick.
        :type convert_coeff: int
        """
        super().__init__(map, player, unit, Process.DROP, convert_coeff)
        self.__target_coord = target_coord
        self.__command_list = command_list
        super().push_command_to_list(command_list)
        
    def run_command(self):
        """
        Runs the drop command.
        """
        self.get_interactions().drop_resource(self.get_player(), self.get_entity(), self.__target_coord)
        super().remove_command_from_list(self.__command_list)
    
class BuildCommand(Command):
    """This class is responsible for executing build commands."""
    
    def __init__(self, map: Map, player: Player, unit: Villager, building: Building, target_coord: Coordinate, convert_coeff: int, command_list: list[Command]) -> None:
        """
        Initializes the BuildCommand with the given map, player, entity, process and convert_coeff.
        :param map: The map where the command will be executed
        :type map: Map
        :param player: The player that will execute the command.
        :type player: Player
        :param unit: The entity that will execute the command.
        :type unit: Unit
        :param building: The building that will be built.
        :type building: Building
        :param target_coord: The target coordinate where the entity will build.
        :type target_coord: Coordinate
        :param convert_coeff: The coefficient used to convert time to tick.
        :type convert_coeff: int
        """
        super().__init__(map, player, unit, Process.BUILD, convert_coeff)
        self.set_time(building.get_spawning_time())
        self.set_tick(int(self.get_time() * convert_coeff))
        self.__building = building
        self.__target_coord = target_coord
        self.__command_list = command_list
        self.__place_holder: GameObject = GameObject("Place Holder",'x',9999)
        self.__place_holder.set_size(building.get_size())
        self.__start: bool = True
        super().push_command_to_list(command_list)
    
    def run_command(self):
        """
        Runs the build command.
        """
        if not self.get_entity().get_coordinate().is_adjacent(self.__target_coord):
            super().remove_command_from_list(self.__command_list)
            raise ValueError("Target is out of range.")
        # To do: implement multi-build and another adjacent check
        if self.__start:
            self.__start = False
            if not all(self.get_player().check_consume(resource, amount) for resource, amount in self.__building.get_cost().items()):
                super().remove_command_from_list(self.__command_list)
                raise ValueError(f"Player: {self.get_player().get_name() } don't have enough resources. Needing {self.__building.get_cost()} while having {self.get_player().get_resources()}")
            for resource, amount in self.__building.get_cost().items():
                self.get_player().consume(resource, amount)
            self.get_interactions().place_object(self.__place_holder, self.__target_coord)
        
        if self.get_tick() <= 0:
            if self in self.__command_list:
                self.get_interactions().remove_object(self.__place_holder)
                self.get_interactions().place_object(self.__building, self.__target_coord)
                self.get_interactions().link_owner(self.get_player(), self.__building)
                if self.__building.is_population_increase():
                    self.get_player().set_max_population(self.get_player().get_max_population() + self.__building.get_capacity_increase())
            super().remove_command_from_list(self.__command_list)
        self.set_tick(self.get_tick() - 1)


class CommandManager:
    """This class is responsible for managing commands of a single player, using the same list of commands for all players."""

    def __init__(self, map: Map, player: Player, convert_coeff: int, command_list: list[Command]) -> None:
        """
        Initializes the CommandManager with the given map, player and convert_coeff.
        :param map: The map where the command will be executed.
        :type map: Map
        :param player: The player that will execute the command.
        :type player: Player
        :param convert_coeff: The coefficient used to convert time to tick.
        :type convert_coeff: int
        """
        self.__map: Map = map
        self.__player: Player = player
        self.__convert_coeff: int = convert_coeff
        self.__command_list: list[Command] = command_list
    def get_map(self):
        """
        Returns the map where the command will be executed.
        :return: The map where the command will be executed.
        :rtype: Map
        """
        return self.__map
    def get_command_list(self) -> list[Command]:
        """
        Returns the command list.
        :return: The command list.
        :rtype: list
        """
        return self.__command_list
    def get_player(self) -> Player:
        return self.__player
    
    def command(self, entity: Entity, process: Process, target_coord: Coordinate, building: Building = None ) -> Command:
        """
        Creates a command with the given entity, process and target coordinate.
        :param entity: The entity that will execute the command.
        :type entity: Entity
        :param process: The process that the command will execute.
        :type process: Process
        :param target_coord: The target coordinate where the entity will execute the command.
        :type target_coord: Coordinate
        :param building: The building that will be built. It is only used when the process is Process.BUILD, otherwise it is None.   
        :type building: Building
        """
        if process == Process.SPAWN:
            return SpawnCommand(self.__map, self.__player, entity, target_coord, self.__convert_coeff, self.__command_list)
        elif process == Process.MOVE:
            return MoveCommand(self.__map, self.__player, entity, target_coord, self.__convert_coeff, self.__command_list)
        elif process == Process.ATTACK:
            return AttackCommand(self.__map, self.__player, entity, target_coord, self.__convert_coeff, self.__command_list)
        elif process == Process.COLLECT:
            return CollectCommand(self.__map, self.__player, entity, target_coord, self.__convert_coeff, self.__command_list)
        elif process == Process.DROP:
            return DropCommand(self.__map, self.__player, entity, target_coord, self.__convert_coeff, self.__command_list)
        elif process == Process.BUILD:
            return BuildCommand(self.__map, self.__player, entity, building, target_coord, self.__convert_coeff, self.__command_list)
    
class Task(ABC):
    def __init__(self,command_manager: CommandManager,  entity: Entity, target_coord: Coordinate) -> None:
        """
        Initializes the task with the given command_manager, entity and target_coord.
        :param command_manager: The command manager of the player that will execute the task.
        :type command_manager: CommandManager
        :param entity: The entity that will execute the task.
        :type entity: Entity
        :param target_coord: The target coordinate where the entity will execute the task.
        :type target_coord: Coordinate
        """
        self.__entity: Entity = entity
        self.__target_coord: Coordinate = target_coord
        self.__command_manager : CommandManager = command_manager
        self.__waiting: bool = False
        self.__name: str = ""
    @abstractmethod
    def get_name(self) -> str:
        """
        Returns the name of the task.
        :return: The name of the task.
        :rtype: str
        """
        return self.__name
    def __repr__(self):
        return f"{self.get_name()}. Target {self.__target_coord}"

    @abstractmethod
    def execute_task(self):
        """
        Execute the task, meaning that it will add a command(init the command) to the list or wait .
        This method must be implemented by the subclasses.
        """
        pass
    def get_command_manager(self) -> CommandManager:
        """
        Returns the command manager of the task.
        :return: The command manager of the task.
        :rtype: CommandManager
        """
        return self.__command_manager
    
    def get_entity(self) -> Entity:
        """
        Returns the entity that will execute the task.
        :return: The entity that will execute the task.
        :rtype: Entity
        """
        return self.__entity
    
    def get_target_coord(self) -> Coordinate:
        """
        Returns the target coordinate where the entity will execute the task.
        :return: The target coordinate where the entity will execute the task.
        :rtype: Coordinate
        """
        return self.__target_coord
    
    def get_waiting(self) -> bool:
        """
        Returns whether the task is waiting or not.
        :return: True if the task is waiting, False otherwise.
        :rtype: bool
        """
        return self.__waiting
    
    def set_waiting(self, waiting: bool) -> None:
        """
        Sets whether the task is waiting or not.
        :param waiting: True if the task is waiting, False otherwise.
        :type waiting: bool
        """
        self.__waiting = waiting
    

class MoveTask(Task):
    def __init__(self, command_manager: CommandManager, unit: Unit, target_coord: Coordinate, avoid_from_coord: Coordinate = None, avoid_to_coord: Coordinate = None, diagonal: bool = True) -> None:
        """
        Initializes the MoveTask with the given command_manager, entity, target_coord, avoid_from_coord and avoid_to_coord.
        :param command_manager: The command manager of the player that will execute the task.
        :type command_manager: CommandManager
        :param entity: The entity that will execute the task.
        :type entity: Entity
        :param target_coord: The target coordinate where the entity will move.
        :type target_coord: Coordinate
        :param avoid_from_coord: The coordinate from where the entity will avoid.
        :type avoid_from_coord: Coordinate
        :param avoid_to_coord: The coordinate to where the entity will avoid.
        :type avoid_to_coord: Coordinate
        """
        super().__init__(command_manager, unit, target_coord)
        if avoid_from_coord and avoid_to_coord:
            self.__path: list[Coordinate] = self.get_command_manager().get_map().path_finding_avoid(self.get_entity().get_coordinate(), self.get_target_coord(), avoid_from_coord, avoid_to_coord)
        else:
            if diagonal:
                self.__path: list[Coordinate] = self.get_command_manager().get_map().path_finding(self.get_entity().get_coordinate(), self.get_target_coord())
            else:
                self.__path: list[Coordinate] = self.get_command_manager().get_map().path_finding_non_diagonal(self.get_entity().get_coordinate(), self.get_target_coord())
        #print(self.__path)
        self.__step: int = 0
        self.__command: Command = None
        self.__name : str = "MoveTask"
    def get_name(self) -> str:
        """
        Returns the name of the task.
        :return: The name of the task.
        :rtype: str
        """
        return self.__name
    
    def execute_task(self):
        """
        Execute the move task.
        """
        try:
            if not (self.get_waiting()):
                self.__command = self.get_command_manager().command(self.get_entity(), Process.MOVE, self.__path[self.__step])
                self.set_waiting(True)
            if self.__command.get_tick() <= 0:
                self.set_waiting(False)
                self.__step += 1
        except ValueError:
            self.set_waiting(False)
            self.get_entity().set_task(None)
            

class KillTask(Task):
    def __init__(self, command_manager: CommandManager, entity: Entity, target_coord: Coordinate) -> None:
        """
        Initializes the KillTask with the given command_manager, entity and target_coord.
        :param command_manager: The command manager of the player that will execute the task.
        :type command_manager: CommandManager
        :param entity: The entity that will execute the task.
        :type entity: Entity
        :param target_coord: The target coordinate where the entity will attack.
        :type target_coord: Coordinate
        """
        super().__init__(command_manager, entity, target_coord)
        self.__move_task: MoveTask = MoveTask(self.get_command_manager(), self.get_entity(), self.get_target_coord())
        self.__command: Command = None
        self.__name : str = "KillTask"
        
    def get_name(self) -> str:
        """
        Returns the name of the task.
        :return: The name of the task.
        :rtype: str
        """
        return self.__name
    
    def execute_task(self):
        """
        Execute the kill task.
        """
        attacker: Unit = self.get_entity()
        if not attacker.get_coordinate().is_in_range(self.get_target_coord(), attacker.get_range()): ## out of range case MOVE
            if attacker.get_coordinate().is_adjacent(self.get_target_coord()) and not self.__move_task.get_waiting(): # diagonal out of range case
                self.__move_task = MoveTask(self.get_command_manager(), self.get_entity(), self.get_target_coord(), None, None, False)
                self.__move_task.execute_task()
            if not attacker.get_coordinate().is_adjacent(self.get_target_coord()):
                self.__move_task.execute_task()
        else: ## in range case ATTACK
            if not self.get_waiting():
                if self.get_command_manager().get_map().get(self.get_target_coord()):
                    self.__command = self.get_command_manager().command(self.get_entity(), Process.ATTACK, self.get_target_coord())
                    self.set_waiting(True)
                else:
                    self.get_entity().set_task(None)
            if not self.__command or self.__command.get_tick() <= 0:
                self.set_waiting(False)
                self.get_entity().set_task(None)
            
 ##reminder: if raise then pass by TaskManager       

class CollectAndDropTask(Task):
    def __init__(self, command_manager: CommandManager, villager: Villager, target_coord: Coordinate, drop_coord: Coordinate) -> None:
        """
        Initializes the CollectAndDropTask with the given command_manager, villager, target_coord and drop_coord.
        :param command_manager: The command manager of the player that will execute the task.
        :type command_manager: CommandManager
        :param villager: The villager that will execute the task.
        :type villager: Villager
        :param target_coord: The target coordinate where the villager will collect.
        :type target_coord: Coordinate
        :param drop_coord: The drop coordinate where the villager will drop.
        :type drop_coord: Coordinate
        """
        super().__init__(command_manager, villager, target_coord)
        self.__drop_coord: Coordinate = drop_coord
        self.__move_task_go: MoveTask = MoveTask(self.get_command_manager(), self.get_entity(), self.get_target_coord())
        self.__move_task_back: MoveTask = None
        self.__target_resource: Resource = self.get_command_manager().get_map().get(self.get_target_coord()) if isinstance(self.get_command_manager().get_map().get(self.get_target_coord()), Resource) else self.get_command_manager().get_map().get(self.get_target_coord()).get_food()
        self.__command: Command = None
        self.__name : str = "CollectAndDropTask"
    
    def get_name(self) -> str:
        """
        Returns the name of the task.
        :return: The name of the task.
        :rtype: str
        """
        return self.__name
    
    def calculate_path(self):
        """
        Calculate the path to the target.
        """
        self.__move_task_go = MoveTask(self.get_command_manager(), self.get_entity(), self.get_target_coord())
    def calculate_way_back(self):
        """
        Calculate the way back to the drop point.
        """
        if self.__move_task_back is None:
            self.__move_task_back: MoveTask = MoveTask(self.get_command_manager(), self.get_entity(), self.__drop_coord)
    
    def execute_task(self):
        """
        Execute the collect and drop task.
        """
        collecter : Villager = self.get_entity()
        if self.__target_resource and collecter.get_inventory()[self.__target_resource] < collecter.get_inventory_size(): ## COLLECT
            if not self.get_entity().get_coordinate().is_adjacent(self.get_target_coord()): ## out of range case MOVE  
                self.__move_task_go.execute_task()
            else: ## in range case COLLECT
                if not self.get_waiting():
                    self.__command = self.get_command_manager().command(self.get_entity(), Process.COLLECT, self.get_target_coord())
                    self.set_waiting(True)
                if not self.__command or self.__command.get_tick() <= 0:
                    self.set_waiting(False)
                    self.get_entity().set_task(None)
        else: ##DROP
            if not self.get_entity().get_coordinate().is_adjacent(self.__drop_coord): ## out of range case MOVE  
                self.calculate_way_back()
                self.__move_task_back.execute_task()
            else:
                self.__command = self.get_command_manager().command(self.get_entity(), Process.DROP, self.__drop_coord)
                self.get_entity().set_task(None)

                
class BuildTask(Task):
    def __init__(self, command_manager: CommandManager, villager: Villager, target_coord: Coordinate, building: Building) -> None:
        """
        Initializes the BuildTask with the given command_manager, villager, target_coord and building.
        :param command_manager: The command manager of the player that will execute the task.
        :type command_manager: CommandManager
        :param villager: The villager that will execute the task.
        :type villager: Villager
        :param target_coord: The target coordinate where the villager will build.
        :type target_coord: Coordinate
        :param building: The building that will be built.
        :type building: Building
        """
        super().__init__(command_manager, villager, target_coord)
        self.__building: Building = building
        self.__move_task: MoveTask = MoveTask(self.get_command_manager(), self.get_entity(), self.get_target_coord(), self.get_target_coord(), self.get_target_coord() + (self.__building.get_size()-1))
        self.__command: Command = None
        self.__name : str = "BuildTask"
    
    def get_name(self) -> str:
        """
        Returns the name of the task.
        :return: The name of the task.
        :rtype: str
        """
        return self.__name
    
    def execute_task(self):
        """
        Execute the build task.
        """
        if not self.get_entity().get_coordinate().is_adjacent(self.get_target_coord()): ## out of range case MOVE  
            self.__move_task.execute_task()
        else:
            if not self.get_waiting():
                    self.__command =self.get_command_manager().command(self.get_entity(), Process.BUILD, self.get_target_coord(), self.__building) 
                    self.set_waiting(True)
            if not self.__command or self.__command.get_tick() <= 0:
                    self.set_waiting(False)
                    self.get_entity().set_task(None)
            

class SpawnTask(Task):
    def __init__(self, command_manager: CommandManager, building: Building) -> None:
        """
        Initializes the SpawnTask with the given command_manager and entity.
        :param command_manager: The command manager of the player that will execute the task.
        :type command_manager: CommandManager
        :param building: The building that will execute the task.
        :type building: Building
        """
        target_coord : Coordinate = command_manager.get_map().find_nearest_empty_zones(building.get_coordinate(), 1)[0]
        super().__init__(command_manager, building, target_coord)
        self.__name : str = "SpawnTask"
        self.__command: Command = None
    
    def get_name(self) -> str:
        """
        Returns the name of the task.
        :return: The name of the task.
        :rtype: str
        """
        return self.__name
    
    def execute_task(self):
        if not self.get_waiting():
            self.__command =self.get_command_manager().command(self.get_entity(), Process.SPAWN, self.get_target_coord())
            self.set_waiting(True)
        if not self.__command or self.__command.get_tick() <= (self.__command.get_convert_coeff() * 20):
            self.set_waiting(False)
            self.get_entity().set_task(None)

class TaskManager:
    def __init__(self, command_manager: CommandManager) -> None:
        """
        Initializes the TaskManager with the given command_manager.
        :param command_manager: The command manager of the player that will execute the task.
        :type command_manager: CommandManager
        """
        self.__command_manager: CommandManager = command_manager
    
    def execute_tasks(self) -> None:
        """
        Executes all assigned tasks in 
        """
        for unit in self.__command_manager.get_player().get_units():
                if unit.get_task() is not None:
                    try:
                        unit.get_task().execute_task()
                    except (ValueError,IndexError) as e:
                        #print(f"Error executing task by {unit.get_name()} at {unit.get_coordinate()}")
                        #import traceback
                        #print(traceback.format_exc())
                        #print(e)
                        #exit()
                        unit.set_task(None)
        for building in self.__command_manager.get_player().get_buildings():
            if building.get_task() is not None:
                try:
                    building.get_task().execute_task()
                except (ValueError, IndexError):
                    building.set_task(None)

