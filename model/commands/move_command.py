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


class MoveCommand(Command):
    """This class is responsible for executing move commands."""

    def __init__(
        self,
        game_map: Map,
        player: Player,
        unit: Unit,
        network_controller: "NetworkController",
        target_coord: Coordinate,
        convert_coeff: int,
        command_list: list[Command],
    ) -> None:
        """
        Initializes the MoveCommand with the given map, player, entity, process and convert_coeff.
        :param game_map: The map where the command will be executed.
        :type game_map: Map
        :param unit: The entity that will execute the command.
        :type unit: Unit
        :param process: The process that the command will execute.
        :type process: Process
        :param convert_coeff: The coefficient used to convert time to tick.
        :type convert_coeff: int
        """
        super().__init__(
            game_map, player, unit, network_controller, Process.MOVE, convert_coeff
        )
        self.set_time(unit.get_speed())
        self.set_tick(int(self.get_time() * convert_coeff))
        self.__original_x = unit.get_coordinate().get_x()  # Store x directly
        self.__original_y = unit.get_coordinate().get_y()  # Store y directly
        self.__target_coord = target_coord
        self.__command_list = command_list
        self.__start: bool = True
        super().push_command_to_list(command_list)

    def run_command(self):
        """
        Runs the move command.
        """
        if self.__start:
            self.__start = False
            self.get_interactions().move_unit(self.get_entity(), self.__target_coord)
            self.send_network()
        if self.get_tick() <= 0:
            super().remove_command_from_list(self.__command_list)
        self.set_tick(self.get_tick() - 1)

    def send_network(self):
        """
        Sends the move command information via network.
        """
        entity = self.get_entity()
        command_data = {
            "command": "MOVE",
            "entity_id": id(entity),
            "entity_type": entity.__class__.__name__,
            "entity_name": entity.get_name(),
            "player": self.get_player().get_name(),
            "from_x": self.__original_x,  # Use stored original x
            "from_y": self.__original_y,  # Use stored original y
            "to_x": self.__target_coord.get_x(),
            "to_y": self.__target_coord.get_y()
        }
        super().send_network(json.dumps(command_data))