import random
from model.player.strategies.strategy import Strategy
from model.buildings.farm import Farm
from model.buildings.house import House
from model.resources.resource import Resource
from model.units.villager import Villager
from model.tasks.collect_and_drop_task import CollectAndDropTask
from model.tasks.build_task import BuildTask
from model.buildings.building import Building

class RandomStrategy(Strategy):
    """A simple strategy that assigns random tasks to idle units."""
    
    def __init__(self, ai):
        super().__init__(ai)
        
    def execute(self):
        """Execute random actions for idle units"""
        # Get all idle villagers
        villagers = [u for u in self.get_ai().get_player().get_units() 
                    if isinstance(u, Villager) and u.get_task() is None]
        
        if not villagers:
            return
            
        center = self.get_ai().get_player().get_centre_coordinate()
        if not center:
            return
            
        # Find resource locations
        resources = self.get_ai().get_map_known().find_nearest_objects(center, Resource)
        
        # Find drop points
        drop_points = []
        for building in self.get_ai().get_player().get_buildings():
            if building.is_resources_drop_point():
                drop_points.append(building.get_coordinate())
        
        # Find building locations adjacent to existing buildings
        adjacent_build_points = self.find_adjacent_build_points()
        
        # If no adjacent points are found, fallback to finding any empty zones
        if not adjacent_build_points:
            adjacent_build_points = self.get_ai().get_map_known().find_nearest_empty_zones(center, 2)
        
        # Process each idle villager
        for villager in villagers:
            # Choose a random action: 0=collect, 1=build
            action = random.randint(0, 1)
            
            if action == 0 and resources and drop_points:
                # Collect resources
                resource_point = random.choice(resources)
                drop_point = random.choice(drop_points)
                villager.set_task(CollectAndDropTask(
                    self.get_ai().get_player().get_command_manager(),
                    villager,
                    resource_point,
                    drop_point
                ))
            elif action == 1 and adjacent_build_points:
                # Build something
                build_point = random.choice(adjacent_build_points)
                # Choose a random building: 0=Farm, 1=House
                building_type = random.randint(0, 1)
                building = Farm() if building_type == 0 else House()
                
                # Check if we have resources
                can_build = True
                for resource, amount in building.get_cost().items():
                    if not self.get_ai().get_player().check_consume(resource, amount):
                        can_build = False
                        break
                
                if can_build:
                    villager.set_task(BuildTask(
                        self.get_ai().get_player().get_command_manager(),
                        villager,
                        build_point,
                        building
                    ))
    
    def find_adjacent_build_points(self):
        """Find empty tiles adjacent to existing buildings."""
        game_map = self.get_ai().get_map_known()
        adjacent_points = []
        
        # Get all buildings owned by the player
        buildings = self.get_ai().get_player().get_buildings()
        
        # Check all adjacent tiles for each building
        for building in buildings:
            building_coord = building.get_coordinate()
            
            # Check in all 8 directions around the building
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    # Skip the building tile itself
                    if dx == 0 and dy == 0:
                        continue
                    
                    # Calculate adjacent coordinate
                    adjacent_x = building_coord.get_x() + dx
                    adjacent_y = building_coord.get_y() + dy
                    
                    # Check if within map bounds
                    map_size = game_map.get_size()
                    if 0 <= adjacent_x < map_size and 0 <= adjacent_y < map_size:
                        from util.coordinate import Coordinate
                        adjacent_coord = Coordinate(adjacent_x, adjacent_y)
                        
                        # Check if tile is empty
                        if game_map.get(adjacent_coord) is None:
                            # Also check if there's enough space for a 2x2 building
                            has_space = True
                            for bx in range(2):
                                for by in range(2):
                                    check_x = adjacent_x + bx
                                    check_y = adjacent_y + by
                                    if not (0 <= check_x < map_size and 0 <= check_y < map_size):
                                        has_space = False
                                        break
                                    check_coord = Coordinate(check_x, check_y)
                                    if game_map.get(check_coord) is not None:
                                        has_space = False
                                        break
                                if not has_space:
                                    break
                            
                            if has_space:
                                adjacent_points.append(adjacent_coord)
        
        return adjacent_points