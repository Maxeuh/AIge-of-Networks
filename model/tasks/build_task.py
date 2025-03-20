from controller.command_controller import CommandController
from model.buildings.building import Building
from model.commands.command import Command
from model.tasks.move_task import MoveTask
from model.tasks.task import Task
from model.units.villager import Villager
from util.coordinate import Coordinate
from util.state_manager import Process


class BuildTask(Task):
    """This class is responsible for executing build tasks."""
    
    def __init__(self, command_manager: CommandController, villager: Villager, target_coord: Coordinate, building: Building) -> None:
        """
        Initializes the BuildTask with the given command_manager, villager, target_coord and building.
        :param command_manager: The command manager of the player that will execute the task.
        :type command_manager: CommandController
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