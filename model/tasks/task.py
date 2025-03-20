from abc import ABC, abstractmethod

from controller.command_controller import CommandController
from model.entity import Entity
from util.coordinate import Coordinate


class Task(ABC):
    """
    This class is responsible for executing tasks.
    """
    def __init__(self,command_manager: CommandController,  entity: Entity, target_coord: Coordinate) -> None:
        """
        Initializes the task with the given command_manager, entity and target_coord.
        :param command_manager: The command manager of the player that will execute the task.
        :type command_manager: CommandController
        :param entity: The entity that will execute the task.
        :type entity: Entity
        :param target_coord: The target coordinate where the entity will execute the task.
        :type target_coord: Coordinate
        """
        self.__entity: Entity = entity
        self.__target_coord: Coordinate = target_coord
        self.__command_manager : CommandController = command_manager
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

    def get_command_manager(self) -> CommandController:
        """
        Returns the command manager of the task.
        :return: The command manager of the task.
        :rtype: CommandController
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