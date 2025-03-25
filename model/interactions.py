from controller.network_controller import NetworkController
from model.buildings.building import Building
from model.buildings.farm import Farm
from model.entity import Entity
from model.game_object import GameObject
from model.player.player import Player
from model.resources.resource import Resource
from model.units.unit import Unit
from model.units.villager import Villager
from util.coordinate import Coordinate
from util.map import Map
from util.state_manager import InteractionsTypes


class Interactions:
    def __init__(self, game_map: Map, network_controller: NetworkController) -> None:
        self.__map: Map = game_map
        self.__network_controller: NetworkController = network_controller

    def get_map(self) -> Map:
        """
        Returns the map.
        :return: The map.
        :rtype: Map
        """
        return self.__map

    def place_object(self, game_object: GameObject, coordinate: Coordinate) -> None:
        """
        Place an object on the map, at a certain coordinate.
        :param game_object: The object to place on the map.
        :type game_object: GameObject
        :param coordinate: The coordinate where to place the object.
        :type coordinate: Coordinate
        """
        self.__map.add(game_object, coordinate)
        game_object.set_coordinate(coordinate)
        self.__network_controller.send(
            {
                "action": InteractionsTypes.PLACE_OBJECT.value,
                "game_object": {
                    "id": id(game_object),
                    "name": game_object.get_name(),
                    "size": game_object.get_size(),
                    "coordinate": coordinate.__str__(),
                },
            }
        )

    def remove_object(self, game_object: GameObject) -> None:
        """
        Remove an object from the map.
        :param game_object: The object to remove from the map.
        :type game_object: GameObject
        """
        self.__map.remove(game_object.get_coordinate())
        self.__network_controller.send(
            {
                "action": InteractionsTypes.REMOVE_OBJECT.value,
                "game_object": {
                    "id": id(game_object),
                    "coordinate": game_object.get_coordinate().__str__(),
                },
            }
        )
        game_object.set_coordinate(None)
        game_object.set_alive(False)

    def move_unit(self, unit: Unit, coordinate: Coordinate) -> None:
        """
        Move a unit to a certain coordinate.
        :param unit: The unit to move.
        :type unit: Unit
        :param coordinate: The coordinate where to move the unit.
        :type coordinate: Coordinate
        """
        old_coordinate = unit.get_coordinate()
        self.__map.move(unit, coordinate)
        unit.set_coordinate(coordinate)
        self.__network_controller.send(
            {
                "action": InteractionsTypes.MOVE_UNIT.value,
                "player": {
                    "name": unit.get_player().get_name(),
                },
                "unit": {
                    "id": id(unit),
                    "name": unit.get_name(),
                    "coordinate": coordinate.__str__(),
                    "old_coordinate": old_coordinate.__str__(),
                },
            }
        )

    def attack(self, attacker: Unit, target_coord: Coordinate) -> None:
        """
        Attack
        :param attacker: The unit that attacks.
        :type attacker: Unit
        :param target_coord: The coordinate of the target.
        :type target_coord: Coordinate
        """
        if attacker.get_coordinate().distance(target_coord) > attacker.get_range():
            raise ValueError(
                f"Target at {target_coord} is out of range {attacker.get_coordinate()}."
            )
        target: GameObject = self.__map.get(target_coord)
        if target is None:
            raise ValueError("No target found at the given coordinate.")
        if target.get_player() == attacker.get_player():
            raise ValueError(f"Can't attack oneself's team: {attacker.get_player()} ")
        if isinstance(target, Resource):
            raise ValueError("Target is a resource.")
        target.damage(attacker.get_attack_per_second())  # Damage the target

        self.__network_controller.send(
            {
                "action": InteractionsTypes.ATTACK.value,
                "player": {
                    "name": attacker.get_player().get_name(),
                },
                "attacker": {
                    "id": id(attacker),
                    "name": attacker.get_name(),
                    "coordinate": attacker.get_coordinate().__str__(),
                },
                "target": {
                    "id": id(target),
                    "name": target.get_name(),
                    "coordinate": target.get_coordinate().__str__(),
                    "hp": target.get_hp,
                },
            }
        )

        if not target.is_alive():
            target: Entity = target
            self.remove_object(target)  # Remove the target from the map
            owner = target.get_player()
            if isinstance(target, Building) and target.is_population_increase():
                owner.set_max_population(
                    owner.get_max_population() - target.get_capacity_increase()
                )
            target.set_player(None)
            if isinstance(target, Building):
                owner.remove_building(target)
            if isinstance(target, Unit):
                owner.remove_unit(target)

    def collect_resource(
        self, villager: Villager, resource_coord: Coordinate, amount: int
    ) -> None:
        """
        Collect a resource.
        :param villager: The villager that collects the resource.
        :type villager: Villager
        :param resource_coord: The coordinate of the resource.
        :type resource_coord: Coordinate
        :param amount: The amount of resource to collect.
        :type amount: int
        """
        if not villager.get_coordinate().is_adjacent(resource_coord):
            raise ValueError("Resource is out of range.")
        resource: GameObject = self.__map.get(resource_coord)
        if resource is None:
            raise ValueError(
                f"No resource found at the given coordinate{resource_coord}."
            )
        if isinstance(resource, Farm):
            amount = resource.get_food().collect(amount)
            villager.stock_resource(resource.get_food(), 1)
            if not resource.get_food().is_alive():
                self.remove_object(resource)
        else:
            if not isinstance(resource, Resource):
                raise ValueError("Target is not a resource.")
            amount = resource.collect(amount)  # Collect the resource
            villager.stock_resource(resource, 1)
            self.__network_controller.send(
                {
                    "action": InteractionsTypes.COLLECT_RESOURCE.value,
                    "player": {
                        "name": villager.get_player().get_name(),
                    },
                    "villager": {
                        "id": id(villager),
                        "name": villager.get_name(),
                        "coordinate": villager.get_coordinate().__str__(),
                    },
                    "resource": {
                        "id": id(resource),
                        "name": resource.get_name(),
                        "coordinate": resource.get_coordinate().__str__(),
                        "hp": resource.get_hp(),
                    },
                    "amount": amount,
                }
            )
            if not resource.is_alive():
                self.remove_object(resource)  # Remove the resource from the map

    def drop_resource(
        self, player: Player, villager: Villager, target_coord: Coordinate
    ) -> None:
        """
        Drop the resources to a drop point.
        :param player: The player that owns the villager.
        :type player: Player
        :param villager: The villager that drops the resources.
        :type villager: Villager
        :param target_coord: The coordinate of the drop point.
        :type target_coord: Coordinate
        """
        if not villager.get_coordinate().is_adjacent(target_coord):
            raise ValueError("Target is out of range.")
        target: GameObject = self.__map.get(target_coord)
        if target is None:
            raise ValueError(f"No target found at the given coordinate {target_coord}.")
        if not isinstance(target, Building):
            raise ValueError(f"Target is not a building.{target_coord}")
        if not target.is_resources_drop_point():
            raise ValueError("Target is not a resource drop point.")

        collected_resources = villager.empty_resource()
        for resource, amount in collected_resources.items():
            player.collect(resource, amount)

        self.__network_controller.send(
            {
                "action": InteractionsTypes.DROP_RESOURCE.value,
                "player": {
                    "name": player.get_name(),
                },
                "villager": {
                    "id": id(villager),
                    "name": villager.get_name(),
                    "coordinate": villager.get_coordinate().__str__(),
                },
                "target": {
                    "id": id(target),
                    "name": target.get_name(),
                    "coordinate": target.get_coordinate().__str__(),
                },
                "resources": collected_resources,
            }
        )

    def link_owner(self, player: Player, entity: Entity) -> None:
        """
        Link an owner to an entity.
        :param player: The player that owns the entity.
        :type player: Player
        :param entity: The entity that is owned.
        :type entity: Entity
        """
        entity.set_player(player)
        if isinstance(entity, Building):
            player.add_building(entity)
        if isinstance(entity, Unit):
            player.add_unit(entity)

        self.__network_controller.send(
            {
                "action": InteractionsTypes.LINK_OWNER.value,
                "player": {
                    "name": player.get_name(),
                },
                "entity": {
                    "id": id(entity),
                    "name": entity.get_name(),
                    "coordinate": entity.get_coordinate().__str__(),
                },
            }
        )
