from controller.command_controller import CommandController
from model.buildings.building import Building
from model.commands.command import Command
from model.tasks.task import Task
from util.coordinate import Coordinate
from util.state_manager import Process


class SpawnTask(Task):
    """This class is responsible for executing spawn tasks."""
    
    def __init__(self, command_manager: CommandController, building: Building) -> None:
        """
        Initializes the SpawnTask with the given command_manager and entity.
        :param command_manager: The command manager of the player that will execute the task.
        :type command_manager: CommandController
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