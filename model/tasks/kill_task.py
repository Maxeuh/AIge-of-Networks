from controller.command_controller import CommandController
from model.commands.command import Command
from model.entity import Entity
from model.tasks.move_task import MoveTask
from model.tasks.task import Task
from model.units.unit import Unit
from util.coordinate import Coordinate
from util.state_manager import Process


class KillTask(Task):
    """This class is responsible for executing kill tasks."""
    
    def __init__(self, command_manager: CommandController, entity: Entity, target_coord: Coordinate) -> None:
        """
        Initializes the KillTask with the given command_manager, entity and target_coord.
        :param command_manager: The command manager of the player that will execute the task.
        :type command_manager: CommandController
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