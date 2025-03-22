def get_items_data(game_controller, max_items=100) -> list[dict]:
    """Returns a list of dictionaries with item positions and info."""
    items_info = []
    count = 0
    
    # Collect unit information (with limit)
    for player in game_controller.get_players():
        # Get units
        for unit in player.get_units():
            if count >= max_items:
                break
                
            if unit.get_coordinate():
                try:
                    items_info.append({
                        "type": "unit",
                        "owner": player.get_name(),
                        "name": unit.get_name(),
                        "coordinate": (unit.get_coordinate().get_x(), unit.get_coordinate().get_y()),
                        "health": unit.get_health() if hasattr(unit, "get_health") else None,
                        "max_health": unit.get_max_health() if hasattr(unit, "get_max_health") else None
                    })
                    count += 1
                except Exception as e:
                    print(f"Error getting unit data: {e}")
        
        if count >= max_items:
            break
                
        # Get buildings
        for building in player.get_buildings():
            if count >= max_items:
                break
                
            if building.get_coordinate():
                try:
                    items_info.append({
                        "type": "building",
                        "owner": player.get_name(),
                        "name": building.get_name(),
                        "coordinate": (building.get_coordinate().get_x(), building.get_coordinate().get_y()),
                        "health": building.get_health() if hasattr(building, "get_health") else None,
                        "max_health": building.get_max_health() if hasattr(building, "get_max_health") else None
                    })
                    count += 1
                except Exception as e:
                    print(f"Error getting building data: {e}")
        
        if count >= max_items:
            break
    
    # Get resources on the map (with limit)
    try:
        map_obj = game_controller.get_map()
        
        # Safe access to get_resources with error handling
        try:
            resources = map_obj.get_resources()
        except AttributeError:
            print("Warning: Map.get_resources() not implemented")
            resources = []
            
        for resource in resources:
            if count >= max_items:
                break
                
            if resource.get_coordinate():
                try:
                    items_info.append({
                        "type": "resource",
                        "name": resource.get_name(),
                        "coordinate": (resource.get_coordinate().get_x(), resource.get_coordinate().get_y()),
                        "amount": resource.get_amount() if hasattr(resource, "get_amount") else None
                    })
                    count += 1
                except Exception as e:
                    print(f"Error getting resource data: {e}")
    except Exception as e:
        print(f"Error processing map resources: {e}")
    
    return items_info