from model.buildings.building import Building
from model.commands.command import Command, Process
from model.game_object import GameObject
from model.player.player import Player
from model.units.villager import Villager
from util.coordinate import Coordinate
from util.map import Map
import typing

if typing.TYPE_CHECKING:
    from controller.network_controller import NetworkController


class BuildCommand(Command):
    """This class is responsible for executing build commands."""

    def __init__(
        self,
        game_map: Map,
        player: Player,
        unit: Villager,
        network_controller: "NetworkController",
        building: Building,
        target_coord: Coordinate,
        convert_coeff: int,
        command_list: list[Command],
    ) -> None:
        """
        Initializes the BuildCommand with the given map, player, entity, process and convert_coeff.
        :param game_map: The map where the command will be executed
        :type game_map: Map
        :param player: The player that will execute the command.
        :type player: Player
        :param unit: The entity that will execute the command.
        :type unit: Unit
        :param building: The building that will be built.
        :type building: Building
        :param target_coord: The target coordinate where the entity will build.
        :type target_coord: Coordinate
        :param convert_coeff: The coefficient used to convert time to tick.
        :type convert_coeff: int
        """
        super().__init__(
            game_map, player, unit, network_controller, Process.BUILD, convert_coeff
        )
        self.set_time(building.get_spawning_time())
        self.set_tick(int(self.get_time() * convert_coeff))
        self.__building = building
        self.__target_coord = target_coord
        self.__command_list = command_list
        self.__place_holder: GameObject = GameObject("Place Holder", "x", 9999)
        self.__place_holder.set_size(building.get_size())
        self.__start: bool = True
        super().push_command_to_list(command_list)

    def run_command(self):
        """
        Runs the build command.
        """
        if not self.get_entity().get_coordinate().is_adjacent(self.__target_coord):
            super().remove_command_from_list(self.__command_list)
            raise ValueError("Target is out of range.")
        # To do: implement multi-build and another adjacent check
        if self.__start:
            self.__start = False
            if not all(
                self.get_player().check_consume(resource, amount)
                for resource, amount in self.__building.get_cost().items()
            ):
                super().remove_command_from_list(self.__command_list)
                raise ValueError(
                    f"Player: {self.get_player().get_name()} doesn't have enough resources. Needing {self.__building.get_cost()} while having {self.get_player().get_resources()}"
                )
            for resource, amount in self.__building.get_cost().items():
                self.get_player().consume(resource, amount)  # Deduct resources here
            self.get_interactions().place_object(
                self.__place_holder, self.__target_coord
            )
            self.send_network()

        if self.get_tick() <= 0:
            if self in self.__command_list:
                self.get_interactions().remove_object(self.__place_holder)
                self.get_interactions().place_object(
                    self.__building, self.__target_coord
                )
                self.send_network()
                self.get_interactions().link_owner(self.get_player(), self.__building)
                if self.__building.is_population_increase():
                    self.get_player().set_max_population(
                        self.get_player().get_max_population()
                        + self.__building.get_capacity_increase()
                    )
            super().remove_command_from_list(self.__command_list)
        self.set_tick(self.get_tick() - 1)
