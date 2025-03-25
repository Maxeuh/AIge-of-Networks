from model.buildings.building import Building
from model.commands.command import Command, Process
from model.commands.unit_spawner import UnitSpawner
from model.game_object import GameObject
from model.player.player import Player
from model.units.unit import Unit
from util.coordinate import Coordinate
from util.map import Map
import typing

if typing.TYPE_CHECKING:
    from controller.network_controller import NetworkController


class SpawnCommand(Command):
    """This class is responsible for executing spawn commands."""

    def __init__(
        self,
        game_map: Map,
        player: Player,
        building: Building,
        network_controller: "NetworkController",
        target_coord: Coordinate,
        convert_coeff: int,
        command_list: list[Command],
    ) -> None:
        """
        Initializes the SpawnCommand with the given map, player, building, target_coord and convert_coeff.
        :param game_map: The map where the command will be executed
        :type game_map: Map
        :param player: The player that will execute the command.
        :type player: Player
        :param building: The building that will execute the command.
        :type building: Building
        :param target_coord: The target coordinate where the entity will be spawned.
        :type target_coord: Coordinate
        :param convert_coeff: The coefficient used to convert time to tick.
        :type convert_coeff: int
        """
        super().__init__(
            game_map, player, building, network_controller, Process.SPAWN, convert_coeff
        )
        self.set_time(UnitSpawner()[building.get_name()].get_spawning_time())
        self.set_tick(int(self.get_time() * convert_coeff))
        self.__target_coord = target_coord
        self.__command_list = command_list
        self.__place_holder: GameObject = GameObject("Place Holder", "x", 9999)
        self.__start: bool = True
        super().push_command_to_list(command_list)
        # print(f"Spawning {self} for {self.get_player().get_name()}, at {self.__target_coord}")

    def get_target_coord(self) -> Coordinate:
        """
        Returns the target coordinate where the entity will be spawned.
        :return: The target coordinate where the entity will be spawned.
        :rtype: Coordinate
        """
        return self.__target_coord

    def run_command(self):
        """
        Runs the spawn command.
        """
        # print(f"Spawning {self} for {self.get_player().get_name()}, {self.get_tick()} compared to {int(self.get_convert_coeff() * self.get_time())}")
        if self.__start:
            self.__start = False
            if (
                self.get_player().get_unit_count()
                >= self.get_player().get_max_population()
            ):
                super().remove_command_from_list(self.__command_list)
                raise ValueError("Population limit reached.")
            if not all(
                self.get_player().check_consume(resource, amount)
                for resource, amount in UnitSpawner()[self.get_entity().get_name()]
                .get_cost()
                .items()
            ):
                super().remove_command_from_list(self.__command_list)
                raise ValueError(
                    f"Not enough resources. Needing {UnitSpawner()[self.get_entity().get_name()].get_cost()} while having {self.get_player().get_resources()}"
                )
            if (
                not self.get_interactions()
                .get_map()
                .check_placement(self.__place_holder, self.__target_coord)
            ):
                super().remove_command_from_list(self.__command_list)
                raise ValueError("Invalid placement.")
            for resource, amount in (
                UnitSpawner()[self.get_entity().get_name()].get_cost().items()
            ):
                self.get_player().consume(resource, amount)
                # print(f"Player {self.get_player().get_name()} consumed {amount} {resource}")
            self.get_interactions().place_object(
                self.__place_holder, self.__target_coord
            )

        if self.get_tick() <= 0:
            if self in self.__command_list:
                self.get_interactions().remove_object(self.__place_holder)
                spawned: Unit = UnitSpawner()[self.get_entity().get_name()]
                self.get_interactions().place_object(spawned, self.__target_coord)
                self.get_interactions().link_owner(self.get_player(), spawned)

                super().remove_command_from_list(self.__command_list)
            else:
                pass
        self.set_tick(self.get_tick() - 1)
