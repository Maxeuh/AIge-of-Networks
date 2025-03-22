from model.commands.command import Command
from model.player.player import Player
from model.units.unit import Unit
from util.coordinate import Coordinate
from util.map import Map
from util.state_manager import Process
import typing
import json

if typing.TYPE_CHECKING:
    from controller.network_controller import NetworkController


class CollectCommand(Command):
    """This class is responsible for executing collect commands."""

    def __init__(
        self,
        game_map: Map,
        player: Player,
        unit: Unit,
        network_controller: "NetworkController",
        target_coord: Coordinate,
        convert_coeff: int,
        command_list: list[Command],
    ):
        """
        Initializes the CollectCommand with the given map, player, entity, process and convert_coeff.
        :param game_map: The map where the command will be executed
        :type game_map: Map
        :param player: The player that will execute the command.
        :type player: Player
        :param unit: The entity that will execute the command.
        :type unit: Unit
        :param target_coord: The target coordinate where the entity will collect.
        :type target_coord: Coordinate
        :param convert_coeff: The coefficient used to convert time to tick.
        :type convert_coeff: int
        """
        super().__init__(
            game_map, player, unit, network_controller, Process.COLLECT, convert_coeff
        )
        self.set_time(25.0 / 60)
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
                self.get_interactions().collect_resource(
                    self.get_entity(), self.__target_coord, 1
                )
                self.send_network()
                super().remove_command_from_list(self.__command_list)
        self.set_tick(self.get_tick() - 1)

    def send_network(self):
        """
        Sends the collect command information via network.
        """
        entity = self.get_entity()
        # Get resource type being collected
        target_obj = self.get_interactions().get_map().get(self.__target_coord)
        resource_type = target_obj.__class__.__name__ if target_obj else "Unknown"
        
        command_data = {
            "command": "COLLECT",
            "entity_id": id(entity),
            "entity_type": entity.__class__.__name__, 
            "entity_name": entity.get_name(),
            "player": self.get_player().get_name(),
            "resource_x": self.__target_coord.get_x(),
            "resource_y": self.__target_coord.get_y(),
            "resource_type": resource_type
        }
        super().send_network(json.dumps(command_data))
