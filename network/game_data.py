def get_items_data(game_controller) -> list[dict]:
    """Returns a list of dictionaries with item positions and info."""
    items_info = []
    
    # Collect unit information
    for player in game_controller.get_players():
        # Get units
        for unit in player.get_units():
            if unit.get_coordinate():
                items_info.append({
                    "type": "unit",
                    "owner": player.get_name(),
                    "name": unit.get_name(),
                    "coordinate": (unit.get_coordinate().get_x(), unit.get_coordinate().get_y()),
                    "health": unit.get_health() if hasattr(unit, "get_health") else None,
                    "max_health": unit.get_max_health() if hasattr(unit, "get_max_health") else None
                })
                
        # Get buildings
        for building in player.get_buildings():
            if building.get_coordinate():
                items_info.append({
                    "type": "building",
                    "owner": player.get_name(),
                    "name": building.get_name(),
                    "coordinate": (building.get_coordinate().get_x(), building.get_coordinate().get_y()),
                    "health": building.get_health() if hasattr(building, "get_health") else None,
                    "max_health": building.get_max_health() if hasattr(building, "get_max_health") else None
                })
    
    # Get resources on the map
    map_obj = game_controller.get_map()
    for resource in map_obj.get_resources():  # This line causes the error!
        if resource.get_coordinate():
            items_info.append({
                "type": "resource",
                "name": resource.get_name(),
                "coordinate": (resource.get_coordinate().get_x(), resource.get_coordinate().get_y()),
                "amount": resource.get_amount() if hasattr(resource, "get_amount") else None
            })
    
    return items_info