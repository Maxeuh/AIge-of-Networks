from model.commands.command import Command, Process
from model.player.player import Player
from model.units.villager import Villager
from util.coordinate import Coordinate
from util.map import Map
import typing

if typing.TYPE_CHECKING:
    from controller.network_controller import NetworkController


class DropCommand(Command):
    """This class is responsible for executing drop commands."""

    def __init__(
        self,
        map: Map,
        player: Player,
        unit: Villager,
        network_controller: "NetworkController",
        target_coord: Coordinate,
        convert_coeff: int,
        command_list: list[Command],
    ) -> None:
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
        super().__init__(
            map, player, unit, network_controller, Process.DROP, convert_coeff
        )
        self.__target_coord = target_coord
        self.__command_list = command_list
        super().push_command_to_list(command_list)

    def run_command(self):
        """
        Runs the drop command.
        """
        self.get_interactions().drop_resource(
            self.get_player(), self.get_entity(), self.__target_coord
        )
        super().remove_command_from_list(self.__command_list)
