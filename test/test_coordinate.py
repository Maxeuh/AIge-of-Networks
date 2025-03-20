import unittest

from util.coordinate import Coordinate


class TestCoordinate(unittest.TestCase):
    """Test suite for the Coordinate class."""

    def setUp(self):
        """Set up the test environment."""
        self.coordinate = Coordinate(1, 1)

    def tearDown(self):
        """Tear down the test environment."""
        self.coordinate = None

    def test_set_x(self):
        """Test setting the x coordinate."""
        self.coordinate.set_x(2)
        self.assertEqual(self.coordinate.get_x(), 2, "The x coordinate should be 2")

    def test_set_y(self):
        """Test setting the y coordinate."""
        self.coordinate.set_y(2)
        self.assertEqual(self.coordinate.get_y(), 2, "The y coordinate should be 2")

    def test_get_x(self):
        """Test getting the x coordinate."""
        self.assertEqual(self.coordinate.get_x(), 1, "The x coordinate should be 1")

    def test_get_y(self):
        """Test getting the y coordinate."""
        self.assertEqual(self.coordinate.get_y(), 1, "The y coordinate should be 1")

    def test_distance(self):
        """Test calculating the distance between coordinates."""
        self.assertEqual(
            self.coordinate.distance(Coordinate(1, 1)), 0, "The distance should be 0"
        )
        self.assertEqual(
            self.coordinate.distance(Coordinate(1, 2)), 1, "The distance should be 1"
        )
        self.assertEqual(
            self.coordinate.distance(Coordinate(2, 1)), 1, "The distance should be 1"
        )
        self.assertEqual(
            self.coordinate.distance(Coordinate(2, 2)),
            2**0.5,
            "The distance should be 2**0.5",
        )

    def test_is_in_range(self):
        """Test checking if a coordinate is within a certain range."""
        self.assertTrue(
            self.coordinate.is_in_range(Coordinate(1, 1), 0),
            "The distance should be in range",
        )
        self.assertTrue(
            self.coordinate.is_in_range(Coordinate(1, 2), 1),
            "The distance should be in range",
        )
        self.assertTrue(
            self.coordinate.is_in_range(Coordinate(2, 1), 1),
            "The distance should be in range",
        )
        self.assertTrue(
            self.coordinate.is_in_range(Coordinate(2, 2), 2**0.5),
            "The distance should be in range",
        )
        self.assertFalse(
            self.coordinate.is_in_range(Coordinate(2, 3), 2**0.5),
            "The distance should not be in range",
        )

    def test_is_adjacent(self):
        """Test checking if a coordinate is adjacent to another."""
        for x in range(4):
            for y in range(4):
                if x == 1 and y == 1:
                    self.assertFalse(
                        self.coordinate.is_adjacent(Coordinate(x, y)),
                        f"The coordinates should not be adjacent to itself",
                    )
                elif abs(x - 1) <= 1 and abs(y - 1) <= 1:
                    self.assertTrue(
                        self.coordinate.is_adjacent(Coordinate(x, y)),
                        f"The coordinates ({x}, {y}) should be adjacent",
                    )
                else:
                    self.assertFalse(
                        self.coordinate.is_adjacent(Coordinate(x, y)),
                        f"The coordinates ({x}, {y}) should not be adjacent",
                    )

    def test_hash(self):
        """Test the hash function of the coordinate."""
        self.assertEqual(
            hash(self.coordinate), hash((1, 1)), "The hash should be equal to the tuple"
        )

    def test_eq(self):
        """Test the equality operator for coordinates."""
        for x in range(4):
            for y in range(4):
                if x == 1 and y == 1:
                    self.assertEqual(
                        self.coordinate,
                        Coordinate(x, y),
                        f"The coordinates should be equal to itself",
                    )
                else:
                    self.assertNotEqual(
                        self.coordinate,
                        Coordinate(x, y),
                        f"The coordinates should not be equal to ({x}, {y})",
                    )

    def test_lt(self):
        """Test the less than operator for coordinates."""
        for x in range(4):
            for y in range(4):
                if 1 < x and 1 < y:
                    self.assertLess(
                        self.coordinate,
                        Coordinate(x, y),
                        f"The coordinates ({x}, {y}) should be less than (1, 1)",
                    )
                else:
                    self.assertFalse(
                        self.coordinate < Coordinate(x, y),
                        f"The coordinates ({x}, {y}) should not be less than (1, 1)",
                    )

    def test_le(self):
        """Test the less than or equal to operator for coordinates."""
        for x in range(4):
            for y in range(4):
                if 1 <= x and 1 <= y:
                    self.assertLessEqual(
                        self.coordinate,
                        Coordinate(x, y),
                        f"The coordinates ({x}, {y}) should be less than or equal to (1, 1)",
                    )
                else:
                    self.assertFalse(
                        self.coordinate <= Coordinate(x, y),
                        f"The coordinates ({x}, {y}) should not be less than or equal to (1, 1)",
                    )

    def test_gt(self):
        """Test the greater than operator for coordinates."""
        for x in range(4):
            for y in range(4):
                if 1 > x and 1 > y:
                    self.assertGreater(
                        self.coordinate,
                        Coordinate(x, y),
                        f"The coordinates ({x}, {y}) should be greater than (1, 1)",
                    )
                else:
                    self.assertFalse(
                        self.coordinate > Coordinate(x, y),
                        f"The coordinates ({x}, {y}) should not be greater than (1, 1)",
                    )

    def test_ge(self):
        """Test the greater than or equal to operator for coordinates."""
        for x in range(4):
            for y in range(4):
                if 1 >= x and 1 >= y:
                    self.assertGreaterEqual(
                        self.coordinate,
                        Coordinate(x, y),
                        f"The coordinates ({x}, {y}) should be greater than or equal to (1, 1)",
                    )
                else:
                    self.assertFalse(
                        self.coordinate >= Coordinate(x, y),
                        f"The coordinates ({x}, {y}) should not be greater than or equal to (1, 1)",
                    )

    def test_add(self):
        """Test the addition operator for coordinates."""
        self.assertEqual(
            self.coordinate + Coordinate(2, 2),
            Coordinate(3, 3),
            "The coordinates should be added",
        )

    def test_sub(self):
        """Test the subtraction operator for coordinates."""
        self.assertEqual(
            self.coordinate - Coordinate(2, 2),
            Coordinate(-1, -1),
            "The coordinates should be subtracted",
        )

    def test_mul(self):
        """Test the multiplication operator for coordinates."""
        self.assertEqual(
            self.coordinate * Coordinate(2, 2),
            Coordinate(2, 2),
            "The coordinates should be multiplied",
        )

    def test_true_div(self):
        """Test the true division operator for coordinates."""
        self.assertEqual(
            self.coordinate / Coordinate(2, 2),
            Coordinate(0.5, 0.5),
            "The coordinates should be divided",
        )

    def test_floordiv(self):
        """Test the floor division operator for coordinates."""
        self.assertEqual(
            self.coordinate // Coordinate(2, 2),
            Coordinate(0, 0),
            "The coordinates should be divided",
        )

    def test_mod(self):
        """Test the modulo operator for coordinates."""
        self.assertEqual(
            self.coordinate % Coordinate(2, 2),
            Coordinate(1, 1),
            "The coordinates should be divided",
        )

    def test_pow(self):
        """Test the power operator for coordinates."""
        self.assertEqual(
            self.coordinate ** Coordinate(2, 2),
            Coordinate(1, 1),
            "The coordinates should be divided",
        )

    def test_lshift(self):
        """Test the left shift operator for coordinates."""
        self.assertEqual(
            self.coordinate << Coordinate(2, 2),
            Coordinate(4, 4),
            "The coordinates should be divided",
        )

    def test_rshift(self):
        """Test the right shift operator for coordinates."""
        self.assertEqual(
            self.coordinate >> Coordinate(2, 2),
            Coordinate(0, 0),
            "The coordinates should be divided",
        )

    def test_and(self):
        """Test the bitwise AND operator for coordinates."""
        self.assertEqual(
            self.coordinate & Coordinate(2, 2),
            Coordinate(0, 0),
            "The coordinates should be divided",
        )

    def test_xor(self):
        """Test the bitwise XOR operator for coordinates."""
        self.assertEqual(
            self.coordinate ^ Coordinate(2, 2),
            Coordinate(3, 3),
            "The coordinates should be divided",
        )

    def test_or(self):
        """Test the bitwise OR operator for coordinates."""
        self.assertEqual(
            self.coordinate | Coordinate(2, 2),
            Coordinate(3, 3),
            "The coordinates should be divided",
        )

    def test_neg(self):
        """Test the negation operator for coordinates."""
        self.assertEqual(
            -self.coordinate, Coordinate(-1, -1), "The coordinates should be negated"
        )

    def test_pos(self):
        """Test the unary plus operator for coordinates."""
        self.assertEqual(
            +self.coordinate, Coordinate(1, 1), "The coordinates should be positive"
        )

    def test_abs(self):
        """Test the absolute value function for coordinates."""
        self.assertEqual(
            abs(self.coordinate), Coordinate(1, 1), "The coordinates should be positive"
        )

    def test_invert(self):
        """Test the bitwise inversion operator for coordinates."""
        self.assertEqual(
            ~self.coordinate, Coordinate(-2, -2), "The coordinates should be inverted"
        )

    def test_str(self):
        """Test the string representation of the coordinate."""
        self.assertEqual(
            str(self.coordinate), "(1,1)", "The string should be equal to (1, 1)"
        )

    def test_repr(self):
        """Test the official string representation of the coordinate."""
        self.assertEqual(
            repr(self.coordinate),
            "Coordinate(1, 1)",
            "The string should be equal to Coordinate(1, 1)",
        )


if __name__ == "__main__":
    unittest.main()
