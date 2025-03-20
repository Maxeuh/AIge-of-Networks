from controller.command_controller import CommandController
from model.commands.command import Command
from model.tasks.task import Task
from model.units.unit import Unit
from util.coordinate import Coordinate
from util.state_manager import Process


class MoveTask(Task):
    """This class is responsible for executing move tasks."""
    
    def __init__(self, command_manager: CommandController, unit: Unit, target_coord: Coordinate, avoid_from_coord: Coordinate = None, avoid_to_coord: Coordinate = None, diagonal: bool = True) -> None:
        """
        Initializes the MoveTask with the given command_manager, entity, target_coord, avoid_from_coord and avoid_to_coord.
        :param command_manager: The command manager of the player that will execute the task.
        :type command_manager: CommandController
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