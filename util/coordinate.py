class Coordinate:
    """Used to represent the coordinates of the tiles in the grid."""

    def __init__(self, x: int, y: int):
        """
        Initialize a Coordinate object.

        :param x: The x coordinate.
        :type x: int
        :param y: The y coordinate.
        :type y: int
        """
        self.__x = x
        self.__y = y

    def set_x(self, x: int) -> None:
        """
        Setter method for the x coordinate.

        :param x: The new x coordinate.
        :type x: int
        """
        self.__x = x

    def set_y(self, y: int) -> None:
        """
        Setter method for the y coordinate.

        :param y: The new y coordinate.
        :type y: int
        """
        self.__y = y

    def get_x(self) -> int:
        """
        Getter method for the x coordinate.

        :return: The x coordinate.
        :rtype: int
        """
        return self.__x

    def get_y(self) -> int:
        """
        Getter method for the y coordinate.

        :return: The y coordinate.
        :rtype: int
        """
        return self.__y

    def distance(self, other: "Coordinate") -> float:
        """
        Calculate the Euclidean distance between two coordinates.

        :param other: The other coordinate.
        :type other: Coordinate
        :return: The Euclidean distance.
        :rtype: float
        """
        if not isinstance(other, Coordinate):
            return None
        return (
            (self.get_x() - other.get_x()) ** 2 + (self.get_y() - other.get_y()) ** 2
        ) ** 0.5

    def is_in_range(self, other: "Coordinate", distance_range: float) -> bool:
        """
        Check if the distance between two coordinates is within a certain range.

        :param other: The other coordinate.
        :type other: Coordinate
        :param distance_range: The distance range.
        :type distance_range: float
        :return: True if the distance is within the range, False otherwise.
        :rtype: bool
        """
        if not isinstance(other, Coordinate):
            return False
        return self.distance(other) <= distance_range + 1e-16

    def is_adjacent(self, other: "Coordinate") -> bool:
        """
        Check if two coordinates are adjacent (including diagonals).

        :param other: The other coordinate.
        :type other: Coordinate
        :return: True if the coordinates are adjacent, False otherwise.
        :rtype: bool
        """
        if not isinstance(other, Coordinate):
            return False
        return self != other and self.is_in_range(other, 2**0.5)

    def __hash__(self) -> int:
        """
        Hash for the coordinates to be used in dictionaries.

        :return: The hash value.
        :rtype: int
        """
        return hash((self.get_x(), self.get_y()))

    def __eq__(self, other: object) -> bool:
        """
        Equality check for the coordinates.

        :param other: The other coordinate.
        :type other: object
        :return: True if the coordinates are equal, False otherwise.
        :rtype: bool
        """
        if not isinstance(other, Coordinate):
            return False
        return self.get_x() == other.get_x() and self.get_y() == other.get_y()

    def __lt__(self, other: "Coordinate") -> bool:
        """
        Less than comparison between two coordinates. (Symbol: <)

        Is less than all the coordinates where the following conditions are all true:
        - self.get_x() is less than other.get_x()
        - self.get_y() is less than other.get_y()

        :param other: The other coordinate.
        :type other: Coordinate
        :return: True if self is less than other, False otherwise.
        :rtype: bool
        """
        if not isinstance(other, Coordinate):
            return False
        return self.get_x() < other.get_x() and self.get_y() < other.get_y()

    def __le__(self, other: "Coordinate") -> bool:
        """
        Less than or equal to comparison between two coordinates. (Symbol: <=)

        Is less than or equal to all the coordinates where the following conditions are all true:
        - self.get_x() is less than or equal to other.get_x()
        - self.get_y() is less than or equal to other.get_y()

        :param other: The other coordinate.
        :type other: Coordinate
        :return: True if self is less than or equal to other, False otherwise.
        :rtype: bool
        """
        if not isinstance(other, Coordinate):
            return False
        return self.get_x() <= other.get_x() and self.get_y() <= other.get_y()

    def __gt__(self, other: "Coordinate") -> bool:
        """
        Less than or equal to comparison between two coordinates. (Symbol: <=)

        Is less than or equal to all the coordinates where the following conditions are all true:
        - self.get_x() is less than or equal to other.get_x()
        - self.get_y() is less than or equal to other.get_y()

        :param other: The other coordinate.
        :type other: Coordinate
        :return: True if self is greater than other, False otherwise.
        :rtype: bool
        """
        if not isinstance(other, Coordinate):
            return False
        return self.get_x() > other.get_x() and self.get_y() > other.get_y()

    def __ge__(self, other: "Coordinate") -> bool:
        """
        Greater than or equal to comparison between two coordinates. (Symbol: >=)

        Is greater than or equal to all the coordinates where the following conditions are all true:
        - self.get_x() is greater than or equal to other.get_x()
        - self.get_y() is greater than or equal to other.get_y()

        :param other: The other coordinate.
        :type other: Coordinate
        :return: True if self is greater than or equal to other, False otherwise.
        :rtype: bool
        """
        if not isinstance(other, Coordinate):
            return False
        return self.get_x() >= other.get_x() and self.get_y() >= other.get_y()

    def __add__(self, other: "Coordinate") -> "Coordinate":
        """
        Addition of a coordinate with another coordinate or an integer.

        :param other: The other coordinate or integer.
        :type other: Coordinate or int
        :return: The resulting coordinate.
        :rtype: Coordinate
        """
        if isinstance(other, int):
            return Coordinate(self.get_x() + other, self.get_y() + other)
        if not isinstance(other, Coordinate):
            return None
        return Coordinate(self.get_x() + other.get_x(), self.get_y() + other.get_y())

    def __sub__(self, other: "Coordinate") -> "Coordinate":
        """
        Subtraction of a coordinate with another coordinate or an integer.

        :param other: The other coordinate or integer.
        :type other: Coordinate or int
        :return: The resulting coordinate.
        :rtype: Coordinate
        """
        if isinstance(other, int):
            return Coordinate(self.get_x() - other, self.get_y() - other)
        if not isinstance(other, Coordinate):
            return None
        return Coordinate(self.get_x() - other.get_x(), self.get_y() - other.get_y())

    def __mul__(self, other: "Coordinate") -> "Coordinate":
        """
        Multiplication of a coordinate with another coordinate or an integer.

        :param other: The other coordinate or integer.
        :type other: Coordinate or int
        :return: The resulting coordinate.
        :rtype: Coordinate
        """
        if isinstance(other, int):
            return Coordinate(self.get_x() * other, self.get_y() * other)
        if not isinstance(other, Coordinate):
            return None
        return Coordinate(self.get_x() * other.get_x(), self.get_y() * other.get_y())

    def __truediv__(self, other: "Coordinate") -> "Coordinate":
        """
        Division of a coordinate with another coordinate or an integer.

        :param other: The other coordinate or integer.
        :type other: Coordinate or int
        :return: The resulting coordinate.
        :rtype: Coordinate
        """
        if isinstance(other, int):
            return Coordinate(self.get_x() / other, self.get_y() / other)
        if not isinstance(other, Coordinate):
            return None
        return Coordinate(self.get_x() / other.get_x(), self.get_y() / other.get_y())

    def __floordiv__(self, other: "Coordinate") -> "Coordinate":
        """
        Floor division of a coordinate with another coordinate or an integer.

        :param other: The other coordinate or integer.
        :type other: Coordinate or int
        :return: The resulting coordinate.
        :rtype: Coordinate
        """
        if isinstance(other, int):
            return Coordinate(self.get_x() // other, self.get_y() // other)
        if not isinstance(other, Coordinate):
            return None
        return Coordinate(self.get_x() // other.get_x(), self.get_y() // other.get_y())

    def __mod__(self, other: "Coordinate") -> "Coordinate":
        """
        Modulus of a coordinate with another coordinate or an integer.

        :param other: The other coordinate or integer.
        :type other: Coordinate or int
        :return: The resulting coordinate.
        :rtype: Coordinate
        """
        if isinstance(other, int):
            return Coordinate(self.get_x() % other, self.get_y() % other)
        if not isinstance(other, Coordinate):
            return None
        return Coordinate(self.get_x() % other.get_x(), self.get_y() % other.get_y())

    def __pow__(self, other: "Coordinate") -> "Coordinate":
        """
        Power of a coordinate with another coordinate or an integer.

        :param other: The other coordinate or integer.
        :type other: Coordinate or int
        :return: The resulting coordinate.
        :rtype: Coordinate
        """
        if isinstance(other, int):
            return Coordinate(self.get_x() ** other, self.get_y() ** other)
        if not isinstance(other, Coordinate):
            return None
        return Coordinate(self.get_x() ** other.get_x(), self.get_y() ** other.get_y())

    def __lshift__(self, other: "Coordinate") -> "Coordinate":
        """
        Left shift of a coordinate with another coordinate or an integer.

        :param other: The other coordinate or integer.
        :type other: Coordinate or int
        :return: The resulting coordinate.
        :rtype: Coordinate
        """
        if isinstance(other, int):
            return Coordinate(self.get_x() << other, self.get_y() << other)
        if not isinstance(other, Coordinate):
            return None
        return Coordinate(self.get_x() << other.get_x(), self.get_y() << other.get_y())

    def __rshift__(self, other: "Coordinate") -> "Coordinate":
        """
        Right shift of a coordinate with another coordinate or an integer.

        :param other: The other coordinate or integer.
        :type other: Coordinate or int
        :return: The resulting coordinate.
        :rtype: Coordinate
        """
        if isinstance(other, int):
            return Coordinate(self.get_x() >> other, self.get_y() >> other)
        if not isinstance(other, Coordinate):
            return None
        return Coordinate(self.get_x() >> other.get_x(), self.get_y() >> other.get_y())

    def __and__(self, other: "Coordinate") -> "Coordinate":
        """
        Bitwise and of a coordinate with another coordinate or an integer.

        :param other: The other coordinate or integer.
        :type other: Coordinate or int
        :return: The resulting coordinate.
        :rtype: Coordinate
        """
        if isinstance(other, int):
            return Coordinate(self.get_x() & other, self.get_y() & other)
        if not isinstance(other, Coordinate):
            return None
        return Coordinate(self.get_x() & other.get_x(), self.get_y() & other.get_y())

    def __xor__(self, other: "Coordinate") -> "Coordinate":
        """
        Bitwise xor of a coordinate with another coordinate or an integer.

        :param other: The other coordinate or integer.
        :type other: Coordinate or int
        :return: The resulting coordinate.
        :rtype: Coordinate
        """
        if isinstance(other, int):
            return Coordinate(self.get_x() ^ other, self.get_y() ^ other)
        if not isinstance(other, Coordinate):
            return None
        return Coordinate(self.get_x() ^ other.get_x(), self.get_y() ^ other.get_y())

    def __or__(self, other: "Coordinate") -> "Coordinate":
        """
        Bitwise or of a coordinate with another coordinate or an integer.

        :param other: The other coordinate or integer.
        :type other: Coordinate or int
        :return: The resulting coordinate.
        :rtype: Coordinate
        """
        if isinstance(other, int):
            return Coordinate(self.get_x() | other, self.get_y() | other)
        if not isinstance(other, Coordinate):
            return None
        return Coordinate(self.get_x() | other.get_x(), self.get_y() | other.get_y())

    def __neg__(self) -> "Coordinate":
        """
        Negation of the coordinates.

        :return: The negated coordinate.
        :rtype: Coordinate
        """
        return Coordinate(-self.get_x(), -self.get_y())

    def __pos__(self) -> "Coordinate":
        """
        Positive of the coordinates.

        :return: The positive coordinate.
        :rtype: Coordinate
        """
        return Coordinate(+self.get_x(), +self.get_y())

    def __abs__(self) -> "Coordinate":
        """
        Absolute value of the coordinates.

        :return: The absolute coordinate.
        :rtype: Coordinate
        """
        return Coordinate(abs(self.get_x()), abs(self.get_y()))

    def __invert__(self) -> "Coordinate":
        """
        Invert the coordinates.

        :return: The inverted coordinate.
        :rtype: Coordinate
        """
        return Coordinate(~self.get_x(), ~self.get_y())

    def __str__(self) -> str:
        """
        String representation of the coordinates.

        :return: The string representation.
        :rtype: str
        """
        return f"({self.get_x()},{self.get_y()})"

    def __repr__(self) -> str:
        """
        Representation of the coordinates.

        :return: The representation.
        :rtype: str
        """
        return f"Coordinate({self.get_x()}, {self.get_y()})"
