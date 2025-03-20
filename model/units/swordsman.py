from model.resources.food import Food
from model.resources.gold import Gold
from model.resources.wood import Wood
from model.units.unit import Unit


class Swordsman(Unit):
    """This class represents the Swordsman unit on the map, inheriting from Unit"""
    def __init__(self):
        super().__init__("Swordsman", "s", 40, { Food(): 50, Gold(): 20 },20, 4, 0.9)

    
        