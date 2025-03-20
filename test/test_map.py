import unittest
from collections import defaultdict

from model.buildings.town_center import TownCenter
from model.units.villager import Villager
from util.coordinate import Coordinate
from util.map import Map


class TestMapCoordinate(unittest.TestCase):
    """Test cases for the Map class and its interactions with buildings and units."""

    def setUp(self):
        """Set up the test environment before each test case. Initializes a map, a building, and a unit."""
        self.map = Map(5)
        self.building = TownCenter()
        self.unit = Villager()
        self.building.set_coordinate(Coordinate(0, 0))
        self.unit.set_coordinate(Coordinate(4, 4))

    def tearDown(self):
        """Clean up the test environment after each test case. Sets the map, building, and unit to None."""
        self.map = None
        self.building = None
        self.unit = None

    def test_get_size(self):
        """Test the get_size method of the Map class. Asserts that the map size is 5."""
        self.assertEqual(self.map.get_size(), 5, "The map size should be 5")

    def test_check_placement(self):
        """Test the check_placement method of the Map class. Asserts that the building can be placed in the correct positions and not in the incorrect ones. Asserts that the unit can be placed in any position."""
        for x in range(5):
            for y in range(5):
                if x < 2 and y < 2:
                    self.assertTrue(
                        self.map.check_placement(self.building, Coordinate(x, y)),
                        f"The building should be able to be placed at position ({x}, {y})",
                    )
                else:
                    self.assertFalse(
                        self.map.check_placement(self.building, Coordinate(x, y)),
                        f"The building should not be able to be placed at position ({x}, {y})",
                    )
                self.assertTrue(
                    self.map.check_placement(self.unit, Coordinate(x, y)),
                    f"The unit should be able to be placed at position ({x}, {y})",
                )

    def test_add_building(self):
        """Test the add method of the Map class for buildings. Adds a building to the map and asserts its position."""
        self.map.add(self.building, Coordinate(0, 0))
        for x in range(5):
            for y in range(5):
                if x < 4 and y < 4:
                    self.assertEqual(
                        self.map.get(Coordinate(x, y)),
                        self.building,
                        f"The building should be at position ({x}, {y})",
                    )
                else:
                    self.assertIsNone(
                        self.map.get(Coordinate(x, y)),
                        f"There should be no building at position ({x}, {y})",
                    )

    def test_add_unit(self):
        """Test the add method of the Map class for units. Adds a unit to the map and asserts its position."""
        self.map.add(self.unit, Coordinate(4, 4))
        for x in range(5):
            for y in range(5):
                if x == 4 and y == 4:
                    self.assertEqual(
                        self.map.get(Coordinate(x, y)),
                        self.unit,
                        f"The unit should be at position ({x}, {y})",
                    )
                else:
                    self.assertIsNone(
                        self.map.get(Coordinate(x, y)),
                        f"There should be no unit at position ({x}, {y})",
                    )

    def test_remove_building(self):
        """Test the remove method of the Map class for buildings. Removes a building from the map and asserts that it is no longer present."""
        self.map.add(self.building, Coordinate(0, 0))
        self.map.remove(Coordinate(0, 0))
        for x in range(5):
            for y in range(5):
                self.assertIsNone(
                    self.map.get(Coordinate(x, y)),
                    f"There should be no building at position ({x}, {y})",
                )

    def test_remove_unit(self):
        """Test the remove method of the Map class for units. Removes a unit from the map and asserts that it is no longer present."""
        self.map.add(self.unit, Coordinate(4, 4))
        self.map.remove(Coordinate(4, 4))
        for x in range(5):
            for y in range(5):
                self.assertIsNone(
                    self.map.get(Coordinate(x, y)),
                    f"There should be no unit at position ({x}, {y})",
                )

    def test_move_unit(self):
        """Test the move method of the Map class for units. Moves a unit to a new position and asserts its new position. Asserts that moving a unit to an invalid position raises a ValueError."""
        self.map.add(self.unit, Coordinate(4, 4))
        self.map.move(self.unit, Coordinate(4, 3))
        self.unit.set_coordinate(Coordinate(4, 3))
        for x in range(5):
            for y in range(5):
                if x == 4 and y == 3:
                    self.assertEqual(
                        self.map.get(Coordinate(x, y)),
                        self.unit,
                        f"The unit should be at position ({x}, {y})",
                    )
                else:
                    self.assertIsNone(
                        self.map.get(Coordinate(x, y)),
                        f"There should be no unit at position ({x}, {y})",
                    )
        with self.assertRaises(ValueError):
            self.map.move(self.unit, Coordinate(0, 0))

    def test_get_method(self):
        """Test the get method of the Map class. Adds a building and a unit to the map and asserts their positions."""
        self.map.add(self.building, Coordinate(0, 0))
        self.map.add(self.unit, Coordinate(4, 4))
        for x in range(5):
            for y in range(5):
                if x < 4 and y < 4:
                    self.assertEqual(
                        self.map.get(Coordinate(x, y)),
                        self.building,
                        f"The building should be at position ({x}, {y})",
                    )
                elif x == 4 and y == 4:
                    self.assertEqual(
                        self.map.get(Coordinate(x, y)),
                        self.unit,
                        f"The unit should be at position ({x}, {y})",
                    )
                else:
                    self.assertIsNone(
                        self.map.get(Coordinate(x, y)),
                        f"There should be no unit at position ({x}, {y})",
                    )

    def test_get_map(self):
        """Test the get_map method of the Map class. Adds a building and a unit to the map and asserts the map's content."""
        expected = defaultdict(lambda: None)
        for x in range(4):
            for y in range(4):
                expected[Coordinate(x, y)] = self.building
        expected[Coordinate(4, 4)] = self.unit
        self.map.add(self.building, Coordinate(0, 0))
        self.map.add(self.unit, Coordinate(4, 4))
        self.assertEqual(
            self.map.get_map(),
            expected,
            "The map should contain the building and the unit",
        )

    def test_get_map_list(self):
        """Test the get_map_list method of the Map class. Adds a building and a unit to the map and asserts the map's content as a list."""
        expected = [
            [self.building if i < 4 and j < 4 else None for j in range(5)]
            for i in range(5)
        ]
        expected[4][4] = self.unit
        self.map.add(self.building, Coordinate(0, 0))
        self.map.add(self.unit, Coordinate(4, 4))
        self.assertEqual(
            self.map.get_map_list(),
            expected,
            "The map should contain the building and the unit",
        )

    def test_get_from_to(self):
        """Test the get_from_to method of the Map class. Adds a building and a unit to the map and asserts the map's content within a specified range."""
        expected = Map(5)
        expected.add(self.building, Coordinate(0, 0))
        expected.add(self.unit, Coordinate(4, 4))
        self.map.add(self.building, Coordinate(0, 0))
        self.map.add(self.unit, Coordinate(4, 4))
        self.assertEqual(
            self.map.get_from_to(Coordinate(0, 0), Coordinate(4, 4)).get_map(),
            expected.get_map(),
            "The map should contain the building and the unit",
        )

    def test_get_map_from_to(self):
        """Test the get_map_from_to method of the Map class. Adds a building and a unit to the map and asserts the map's content within a specified range as a dictionary."""
        expected = defaultdict(lambda: None)
        for x in range(2, 4):
            for y in range(2, 4):
                expected[Coordinate(x, y)] = self.building
        expected[Coordinate(4, 4)] = self.unit
        self.map.add(self.building, Coordinate(0, 0))
        self.map.add(self.unit, Coordinate(4, 4))
        self.assertEqual(
            self.map.get_map_from_to(Coordinate(2, 2), Coordinate(4, 4)),
            expected,
            "The map should contain the building and the unit",
        )

    def test_get_map_list_from_to(self):
        """Test the get_map_list_from_to method of the Map class. Adds a building and a unit to the map and asserts the map's content within a specified range as a list."""
        expected = [
            [
                self.building if i >= 2 and i < 4 and j >= 2 and j < 4 else None
                for j in range(5)
            ]
            for i in range(5)
        ]
        expected[4][4] = self.unit
        self.map.add(self.building, Coordinate(0, 0))
        self.map.add(self.unit, Coordinate(4, 4))
        self.assertEqual(
            self.map.get_map_list_from_to(Coordinate(2, 2), Coordinate(4, 4)),
            expected,
            "The map should contain the building and the unit",
        )


if __name__ == "__main__":
    unittest.main()
