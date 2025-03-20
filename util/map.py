import typing
from collections import defaultdict

from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder

from model.buildings.farm import Farm
from model.entity import Entity
from model.game_object import GameObject
from model.resources.resource import Resource
from util.coordinate import Coordinate

if typing.TYPE_CHECKING:
    from model.player.player import Player

"""
This file contains the Map class which is used to represent the map of the game and the methods associated with it.
It serves as the heart of the model-the representation of datas
"""


class Map:
    DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    """
    The Map class is used to represent the map of the game. It contains the matrix of the map and the methods associated with it.
    """

    def __init__(self, size: int):
        """
        Create a map with a certain size.

        :param size: The size of the map.
        :type size: int
        """
        self.__size: int = size
        self.__matrix: defaultdict[Coordinate, GameObject] = defaultdict(lambda: None)

    def get_size(self) -> int:
        """
        Get the size of the map.

        :return: The size of the map.
        :rtype: int
        """
        return self.__size

    def check_placement(self, object: GameObject, coordinate: Coordinate) -> bool:
        """
        Check if an entity can be placed at a certain coordinate.

        :param object: The game object to be placed.
        :type object: GameObject
        :param coordinate: The coordinate where the object is to be placed.
        :type coordinate: Coordinate
        :return: True if the object can be placed, False otherwise.
        :rtype: bool
        """
        for x in range(object.get_size()):
            for y in range(object.get_size()):
                if coordinate is None or not (
                    Coordinate(0, 0) <= coordinate
                    and (coordinate + object.get_size() - 1)
                    <= Coordinate(self.get_size() - 1, self.get_size() - 1)
                ):
                    return False
                if (
                    self.get(Coordinate(coordinate.get_x() + x, coordinate.get_y() + y))
                    is not None
                ):
                    return False
        return True

    def add(self, object: GameObject, coordinate: Coordinate):
        """
        Add an entity at a certain coordinate. It also claims other tiles depending on the size.

        :param object: The game object to be added.
        :type object: GameObject
        :param coordinate: The coordinate where the object is to be added.
        :type coordinate: Coordinate
        :raises ValueError: If the object cannot be placed at the given coordinate.
        """
        if not self.check_placement(object, coordinate):
            raise ValueError(
                f"Cannot place object at the given coordinate {coordinate}."
            )
        for x in range(object.get_size()):
            for y in range(object.get_size()):
                self.__matrix[
                    Coordinate(coordinate.get_x() + x, coordinate.get_y() + y)
                ] = object

    def __force_add(self, object: GameObject, coordinate: Coordinate):
        """
        Forcefully add an entity at a certain coordinate.

        :param object: The game object to be added.
        :type object: GameObject
        :param coordinate: The coordinate where the object is to be added.
        :type coordinate: Coordinate
        """
        self.__matrix[coordinate] = object

    def remove(self, coordinate: Coordinate) -> GameObject:
        """
        Remove the entity at a certain coordinate. It also removes other tiles depending on the size.

        :param coordinate: The coordinate from which the object is to be removed.
        :type coordinate: Coordinate
        :return: The removed game object.
        :rtype: GameObject
        :raises ValueError: If the coordinate is out of bounds or there is no entity at the given coordinate.
        """
        if not (
            Coordinate(0, 0)
            <= coordinate
            <= Coordinate(self.get_size(), self.get_size())
        ):
            raise ValueError(f"Coordinate is out of bounds.{coordinate}")
        object: GameObject = self.__matrix[coordinate]
        if object is None:
            raise ValueError(f"No entity at the given coordinate.{coordinate}")
        for x in range(object.get_size()):
            for y in range(object.get_size()):
                self.__matrix[
                    Coordinate(coordinate.get_x() + x, coordinate.get_y() + y)
                ] = None
        return object

    def __force_remove(self, coordinate: Coordinate) -> GameObject:
        """
        Forcefully remove the entity at a certain coordinate.

        :param coordinate: The coordinate from which the object is to be removed.
        :type coordinate: Coordinate
        :return: The removed game object.
        :rtype: GameObject
        """
        object: GameObject = self.__matrix[coordinate]
        self.__matrix[coordinate] = None
        return object

    def move(self, object: GameObject, new_coordinate: Coordinate):
        """
        Move an entity to a new adjacent coordinate (8 surrounding coordinates).

        :param object: The game object to be moved.
        :type object: GameObject
        :param new_coordinate: The new coordinate where the object is to be moved.
        :type new_coordinate: Coordinate
        :raises ValueError: If the new coordinate is not adjacent or not available.
        """
        if not object.get_coordinate().is_adjacent(new_coordinate):
            raise ValueError(
                f"New coordinate {new_coordinate} is not adjacent to the entity's current coordinate { object.get_coordinate()}."
            )
        if not self.check_placement(object, new_coordinate):
            raise ValueError("New coordinate is not available.")
        self.remove(object.get_coordinate())
        self.add(object, new_coordinate)

    def __force_move(self, object: GameObject, new_coordinate: Coordinate):
        """
        Forcefully move an entity to a new coordinate.

        :param object: The game object to be moved.
        :type object: GameObject
        :param new_coordinate: The new coordinate where the object is to be moved.
        :type new_coordinate: Coordinate
        """
        self.__force_remove(object.get_coordinate())
        self.__force_add(object, new_coordinate)

    def get(self, coordinate: Coordinate) -> GameObject:
        """
        Get the entity at a certain coordinate.

        :param coordinate: The coordinate from which the object is to be retrieved.
        :type coordinate: Coordinate
        :return: The game object at the given coordinate.
        :rtype: GameObject
        """
        return self.__matrix[coordinate]

    def get_map(self) -> defaultdict[Coordinate, GameObject]:
        """
        Get the map as a matrix.

        :return: The map as a matrix.
        :rtype: defaultdict[Coordinate, GameObject]
        """
        return self.__matrix

    def get_map_list(self) -> list[list[GameObject]]:
        """
        Get the map as a list of lists.

        :return: The map as a list of lists.
        :rtype: list[list[GameObject]]
        """
        return [
            [self.__matrix[Coordinate(i, j)] for j in range(self.get_size())]
            for i in range(self.get_size())
        ]

    def get_from_to(self, from_coord: Coordinate, to_coord: Coordinate) -> "Map":
        """
        Get the map from a certain coordinate to another as a new Map with size based on the range between coordinates.

        :param from_coord: The starting coordinate.
        :type from_coord: Coordinate
        :param to_coord: The ending coordinate.
        :type to_coord: Coordinate
        :return: A new map from the starting coordinate to the ending coordinate.
        :rtype: Map
        """
        new_size = max(
            to_coord.get_x() - from_coord.get_x(), to_coord.get_y() - from_coord.get_y()
        )
        new_map = Map(new_size)
        for x in range(from_coord.get_x(), to_coord.get_x() + 1):
            for y in range(from_coord.get_y(), to_coord.get_y() + 1):
                obj = self.get(Coordinate(x, y))
                if obj is not None:
                    new_map.__force_add(
                        obj, Coordinate(x - from_coord.get_x(), y - from_coord.get_y())
                    )
        return new_map

    def get_map_from_to(
        self, from_coord: Coordinate, to_coord: Coordinate
    ) -> defaultdict[Coordinate, GameObject]:
        """
        Get the map from a certain coordinate to another as a matrix.

        :param from_coord: The starting coordinate.
        :type from_coord: Coordinate
        :param to_coord: The ending coordinate.
        :type to_coord: Coordinate
        :return: A matrix from the starting coordinate to the ending coordinate.
        :rtype: defaultdict[Coordinate, GameObject]
        """
        result = defaultdict(lambda: None)
        for x in range(from_coord.get_x(), to_coord.get_x() + 1):
            for y in range(from_coord.get_y(), to_coord.get_y() + 1):
                obj = self.get(Coordinate(x, y))
                if obj is not None:
                    result[Coordinate(x, y)] = obj
        return result

    def get_map_list_from_to(
        self, from_coord: Coordinate, to_coord: Coordinate
    ) -> list[list[GameObject]]:
        """
        Get the map as a list of lists from a certain coordinate to another.

        :param from_coord: The starting coordinate.
        :type from_coord: Coordinate
        :param to_coord: The ending coordinate.
        :type to_coord: Coordinate
        :return: A list of lists from the starting coordinate to the ending coordinate.
        :rtype: list[list[GameObject]]
        """
        size = self.get_size()
        result = [[None for _ in range(size)] for _ in range(size)]
        for x in range(from_coord.get_x(), to_coord.get_x() + 1):
            for y in range(from_coord.get_y(), to_coord.get_y() + 1):
                result[x][y] = self.get(Coordinate(x, y))
        return result

    def tabler_str(self) -> str:
        """
        Get the string representation of the map in tabler format.

        :return: The matrix of the map as a string in tabler format.
        :rtype: str
        """
        horizontal_line = lambda length: "┌" + "┬".join(["─" * 3] * length) + "┐"
        middle_line = lambda length: "├" + "┼".join(["─" * 3] * length) + "┤"
        bottom_line = lambda length: "└" + "┴".join(["─" * 3] * length) + "┘"

        rows = [horizontal_line(self.get_size())]
        for y in range(self.get_size()):
            row = []
            for x in range(self.get_size()):
                object = self.get(Coordinate(x, y))
                row.append(f" {object.get_letter() if object is not None else ' '} ")
            rows.append("│" + "│".join(row) + "│")
            if x < self.get_size() - 1:
                rows.append(middle_line(self.get_size()))
        rows.append(bottom_line(self.get_size()))
        return "\n".join(rows)

    def __str__(self) -> str:
        """
        Get the string representation of the map.

        :return: The matrix of the map as a string.
        :rtype: str
        """
        rows = []
        for y in range(self.get_size()):
            row = []
            for x in range(self.get_size()):
                obj = self.get(Coordinate(x, y))
                row.append(obj.get_letter() if obj else "·")
            rows.append("".join(row))
        return "\n".join(rows)

    def __repr__(self) -> str:
        """
        Get the string representation of the map for testing purposes.

        :return: The string representation of the map.
        :rtype: str
        """
        rows = []
        for y in range(self.get_size()):
            row = []
            for x in range(self.get_size()):
                obj = self.get(Coordinate(x, y))
                row.append(obj.get_letter() if obj else "·")
            rows.append("".join(row))
        return "\n".join(rows)

    def path_finding(self, start: Coordinate, end: Coordinate) -> list[Coordinate]:
        """
        Find the path for a unit to go from start to end.

        :param start: The starting coordinate.
        :type start: Coordinate
        :param end: The ending coordinate.
        :type end: Coordinate
        :return: A list of coordinates representing the path from start to end.
        :rtype: list[Coordinate]
        """
        m = [
            [
                (
                    1
                    if self.get(Coordinate(x, y)) is None
                    or Coordinate(x, y) == start
                    or Coordinate(x, y) == end
                    else 0
                )
                for x in range(self.get_size())
            ]
            for y in range(self.get_size())
        ]
        grid = Grid(matrix=m)
        start_node = grid.node(start.get_x(), start.get_y())
        end_node = grid.node(end.get_x(), end.get_y())
        finder = AStarFinder(diagonal_movement=DiagonalMovement.always)
        path, _ = finder.find_path(start_node, end_node, grid)

        return [Coordinate(x, y) for x, y in path[1:]]

    def path_finding_avoid(
        self,
        start: Coordinate,
        end: Coordinate,
        avoid_from: Coordinate,
        avoid_to: Coordinate,
    ) -> list[Coordinate]:
        """
        Find the path for a unit to go from start to end while avoiding a specific area.

        :param start: The starting coordinate.
        :type start: Coordinate
        :param end: The ending coordinate.
        :type end: Coordinate
        :param avoid_from: The starting coordinate of the area to avoid.
        :type avoid_from: Coordinate
        :param avoid_to: The ending coordinate of the area to avoid.
        :type avoid_to: Coordinate
        :return: A list of coordinates representing the path from start to end while avoiding the specified area.
        :rtype: list[Coordinate]
        """

        matrix = [
            [
                (
                    1
                    if self.get(Coordinate(x, y)) is None
                    or Coordinate(x, y) == start
                    or Coordinate(x, y) == end
                    else 0
                )
                for x in range(self.get_size())
            ]
            for y in range(self.get_size())
        ]

        # Mark the avoid area as non-walkable
        for x in range(avoid_from.get_x(), avoid_to.get_x() + 1):
            for y in range(avoid_from.get_y(), avoid_to.get_y() + 1):
                if 0 <= x < self.get_size() and 0 <= y < self.get_size():
                    matrix[y][x] = 0
        matrix[end.get_y()][end.get_x()] = 1

        grid = Grid(matrix=matrix)
        start_node = grid.node(start.get_x(), start.get_y())
        end_node = grid.node(end.get_x(), end.get_y())
        finder = AStarFinder(diagonal_movement=DiagonalMovement.always)
        path, _ = finder.find_path(start_node, end_node, grid)

        return [Coordinate(x, y) for x, y in path[1:]]

    def path_finding_non_diagonal(
        self, start: Coordinate, end: Coordinate
    ) -> list[Coordinate]:
        """
        Find the path for a unit to go from start to end without diagonal movement.

        :param start: The starting coordinate.
        :type start: Coordinate
        :param end: The ending coordinate.
        :type end: Coordinate
        :return: A list of coordinates representing the path from start to end without diagonal movement.
        :rtype: list[Coordinate]
        """
        m = [
            [
                (
                    1
                    if self.get(Coordinate(x, y)) is None
                    or Coordinate(x, y) == start
                    or Coordinate(x, y) == end
                    else 0
                )
                for x in range(self.get_size())
            ]
            for y in range(self.get_size())
        ]
        grid = Grid(matrix=m)
        start_node = grid.node(start.get_x(), start.get_y())
        end_node = grid.node(end.get_x(), end.get_y())
        finder = AStarFinder(diagonal_movement=DiagonalMovement.never)
        path, _ = finder.find_path(start_node, end_node, grid)

        return [Coordinate(x, y) for x, y in path[1:]]

    def find_nearest_empty_zones(
        self, coordinate: Coordinate, size: int
    ) -> list[Coordinate]:
        """
        Find the nearest empty zone to a given coordinate.

        :param coordinate: The starting coordinate.
        :type coordinate: Coordinate
        :param size: The size of the zone.
        :type size: int
        :return: The nearest empty coordinate.
        :rtype: list[Coordinate]
        """
        map = self.capture()
        zone_list = []
        radius = 1
        size += 1
        size_checker = GameObject("", "", 1)
        size_checker.set_size(size)
        while radius < map.get_size():
            for x in range(
                coordinate.get_x() - radius, coordinate.get_x() + radius + 1
            ):
                if map.check_placement(
                    size_checker, Coordinate(x, coordinate.get_y() - radius)
                ):
                    current = Coordinate(x, coordinate.get_y() - radius)
                    zone_list.append(current + 1)
                    map.add(size_checker, current)
                if map.check_placement(
                    size_checker, Coordinate(x, coordinate.get_y() + radius)
                ):
                    current = Coordinate(x, coordinate.get_y() + radius)
                    zone_list.append(current + 1)
                    map.add(size_checker, current)

            for y in range(
                coordinate.get_y() - radius, coordinate.get_y() + radius + 1
            ):
                if map.check_placement(
                    size_checker, Coordinate(coordinate.get_x() - radius, y)
                ):
                    current = Coordinate(coordinate.get_x() - radius, y)
                    zone_list.append(current + 1)
                    map.add(size_checker, current)
                if map.check_placement(
                    size_checker, Coordinate(coordinate.get_x() + radius, y)
                ):
                    current = Coordinate(coordinate.get_x() + radius, y)
                    zone_list.append(current + 1)
                    map.add(size_checker, current)
            radius += 1
            if size == 2 and len(zone_list) > 0:
                break
        return zone_list

    def find_nearest_objects(
        self, coordinate: Coordinate, object_type: type
    ) -> list[Coordinate]:
        """
        Find the nearest object of the same type to a given coordinate.

        :param coordinate: The starting coordinate.
        :type coordinate: Coordinate
        :param object_type: The type of the object to find.
        :type object_type: type
        :return: The list of coordinate of nearest objects of the same type.
        :rtype: List[Coordinate]
        """
        visited = set()
        queue = [coordinate]
        list_of_objects = []
        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)
            if isinstance(self.get(current), object_type):
                list_of_objects.append(current)
            # Include farms when searching for resources
            if object_type == Resource and isinstance(self.get(current), Farm):
                list_of_objects.append(current)
            for dx, dy in Map.DIRECTIONS:
                neighbor = Coordinate(current.get_x() + dx, current.get_y() + dy)
                if (
                    Coordinate(0, 0)
                    <= neighbor
                    <= Coordinate(self.get_size() - 1, self.get_size() - 1)
                ):
                    queue.append(neighbor)

        return list_of_objects

    def find_nearest_enemies(
        self, coordinate: Coordinate, player: "Player"
    ) -> list[Coordinate]:
        """
        Find the nearest enemies to a given coordinate.

        :param coordinate: The starting coordinate.
        :type coordinate: Coordinate
        :param player: The player to find the nearest enemy of.
        :type player: Player
        :return: A list of coordinates of the nearest enemies.
        :rtype: list[Coordinate]
        """
        list_of_enemies_coordinate = [
            coord
            for coord in self.find_nearest_objects(coordinate, Entity)
            if self.get(coord).get_player() == player
        ]
        return list_of_enemies_coordinate

    def capture(self) -> "Map":
        """
        Copy the map.

        :return: A copy of the map.
        :rtype: Map
        """
        new_map = Map(self.__size)
        new_map.__matrix = self.__matrix.copy()
        return new_map

    def indicate_color(self, coordinate: Coordinate) -> str:
        """
        Get the color of the object coordinate.

        :param coordinate: The coordinate to get the color of.
        :type coordinate: Coordinate
        :return: The color of the coordinate.
        :rtype: str
        """
        object: GameObject = self.get(coordinate)
        if object is None:
            return "white"
        if isinstance(object, Entity):
            return object.get_player().get_color()
        return "white"

    def __getstate__(self):
        # Méthode spéciale pour la sérialisation
        state = self.__dict__.copy()
        state["_Map__matrix"] = dict(
            self.__matrix
        )  # Convertir defaultdict en dict pour la sérialisation
        return state

    def __setstate__(self, state):
        # Méthode spéciale pour la désérialisation
        self.__dict__.update(state)
        self.__matrix = defaultdict(lambda: None, state["_Map__matrix"])
