from model.units.archer import Archer
from model.units.horseman import Horseman
from model.units.swordsman import Swordsman
from model.units.unit import Unit
from model.units.villager import Villager
import typing

if typing.TYPE_CHECKING:
    from controller.network_controller import NetworkController


class UnitSpawner(dict[str, Unit]):
    """This class is responsible for storing the unit spawner."""

    def __init__(self) -> None:
        self["Town Center"] = Villager()
        self["Barracks"] = Swordsman()
        self["Archery Range"] = Archer()
        self["Stable"] = Horseman()
