from model.resources.food import Food
from model.resources.gold import Gold
from model.resources.wood import Wood
from model.units.unit import Unit


class Archer(Unit):
    """This class represents the Archer unit on the map, inheriting from Unit"""
    def __init__(self):
        super().__init__("Archer", "a", 30,{ Wood(): 25, Gold(): 45 }, 35, 4, 1.0)
        super().set_range(4)
    
        
