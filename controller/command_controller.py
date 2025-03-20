from model.buildings.building import Building
from model.commands.attack_command import AttackCommand
from model.commands.build_command import BuildCommand
from model.commands.collect_command import CollectCommand
from model.commands.command import Command
from model.commands.drop_command import DropCommand
from model.commands.move_command import MoveCommand
from model.commands.spawn_command import SpawnCommand
from model.entity import Entity
from model.player.player import Player
from util.coordinate import Coordinate
from util.map import Map
from util.state_manager import Process


class CommandController:
    """This class is responsible for managing commands of a single player, using the same list of commands for all players."""

    def __init__(
        self,
        game_map: Map,
        player: Player,
        convert_coeff: int,
        command_list: list[Command],
    ) -> None:
        """
        Initializes the CommandController with the given map, player and convert_coeff.
        :param map: The map where the command will be executed.
        :type map: Map
        :param player: The player that will execute the command.
        :type player: Player
        :param convert_coeff: The coefficient used to convert time to tick.
        :type convert_coeff: int
        """
        self.__map: Map = game_map
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

    def command(
        self,
        entity: Entity,
        process: Process,
        target_coord: Coordinate,
        building: Building = None,
    ) -> Command:
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
            return SpawnCommand(
                self.__map,
                self.__player,
                entity,
                target_coord,
                self.__convert_coeff,
                self.__command_list,
            )
        elif process == Process.MOVE:
            return MoveCommand(
                self.__map,
                self.__player,
                entity,
                target_coord,
                self.__convert_coeff,
                self.__command_list,
            )
        elif process == Process.ATTACK:
            return AttackCommand(
                self.__map,
                self.__player,
                entity,
                target_coord,
                self.__convert_coeff,
                self.__command_list,
            )
        elif process == Process.COLLECT:
            return CollectCommand(
                self.__map,
                self.__player,
                entity,
                target_coord,
                self.__convert_coeff,
                self.__command_list,
            )
        elif process == Process.DROP:
            return DropCommand(
                self.__map,
                self.__player,
                entity,
                target_coord,
                self.__convert_coeff,
                self.__command_list,
            )
        elif process == Process.BUILD:
            return BuildCommand(
                self.__map,
                self.__player,
                entity,
                building,
                target_coord,
                self.__convert_coeff,
                self.__command_list,
            )
