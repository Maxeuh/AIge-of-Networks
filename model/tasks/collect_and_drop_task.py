from controller.command_controller import CommandController
from model.commands.command import Command
from model.resources.resource import Resource
from model.tasks.move_task import MoveTask
from model.tasks.task import Task
from model.units.villager import Villager
from util.coordinate import Coordinate
from util.state_manager import Process


class CollectAndDropTask(Task):
    """This class is responsible for executing collect and drop tasks."""
    
    def __init__(self, command_manager: CommandController, villager: Villager, target_coord: Coordinate, drop_coord: Coordinate) -> None:
        """
        Initializes the CollectAndDropTask with the given command_manager, villager, target_coord and drop_coord.
        :param command_manager: The command manager of the player that will execute the task.
        :type command_manager: CommandController
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