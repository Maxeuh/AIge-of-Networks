from abc import ABC, abstractmethod

from model.interactions import Interactions
from model.entity import Entity
from model.player.player import Player
from util.map import Map
from util.state_manager import Process
import typing

if typing.TYPE_CHECKING:
    from controller.network_controller import NetworkController


class Command(ABC):
    """This class is responsible for executing commands."""

    def __init__(
        self,
        game_map: Map,
        player: Player,
        entity: Entity,
        network_controller: "NetworkController",
        process: Process,
        convert_coeff: int,
    ) -> None:
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
        self.__interactions: Interactions = Interactions(game_map)
        self.__process: Process = process
        self.__player: Player = player
        self.__entity: Entity = entity
        self.__network_controller: "NetworkController" = network_controller
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

    def push_command_to_list(self, command_list: list["Command"]) -> None:
        """
        Pushes the command to the given list.
        :param command_list: The list where the command will be pushed.
        :type command_list: list
        """
        for command in command_list:
            if command.get_entity() == self.__entity and not (
                command.get_process() == Process.SPAWN
            ):
                if (
                    command.get_process() == Process.COLLECT
                    or command.get_process() == Process.BUILD
                ):
                    raise ValueError("Entity is already collecting or building.")
                if (
                    command.get_process() == Process.ATTACK
                    or command.get_process() == Process.MOVE
                ) and command.get_process() == self.__process:
                    raise ValueError("Entity is cooling down from attacking or moving.")
        command_list.append(self)

    def remove_command_from_list(self, command_list: list["Command"]) -> None:
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

    def send_network(self, data):
        """Sends command data over the network."""
        # print(f"[DEBUG] Command sending network data: {data[:50]}...")
        # Format: "COMMAND_TYPE;{json_data}"
        # command_type = self.get_process().name
        # message = f"{command_type};{data}"
        # self.__network_controller.send(message)
        self.__network_controller.send(data)
