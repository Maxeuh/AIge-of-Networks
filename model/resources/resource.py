from model.game_object import GameObject


class Resource(GameObject):
    """This class represents the resources on the map"""
    
    def __init__(self, name: str, letter: str, amount: int, spawnable: bool):
        """
        Initializes the resource.

        :param name: The name of the resource.
        :type name: str
        :param letter: The letter representing the resource.
        :type letter: str
        :param amount: The amount of the resource.
        :type amount: int
        :param spawnable: Whether the resource can spawn.
        :type spawnable: bool
        """
        super().__init__(name, letter, 1)
        self.__amount: int = amount
        self.__spawnable: bool = spawnable
        super().set_sprite_path(f"assets/sprites/resources/{self.get_name().lower()}.png")
    
    def get_amount(self) -> int:
        """
        Returns the amount of the resource.

        :return: The amount of the resource.
        :rtype: int
        """
        return self.__amount
    
    def is_spawnable(self) -> bool:
        """
        Returns whether or not the resource can spawn.

        :return: True if the resource can spawn, False otherwise.
        :rtype: bool
        """
        return self.__spawnable
    
    def collect(self, amount: int) -> int:
        """
        Collects the resource and returns the amount collected.

        :param amount: The amount to collect.
        :type amount: int
        :return: The amount collected.
        :rtype: int
        """
        if amount > self.__amount:
            amount = self.__amount
            super().damage(1)
        self.__amount -= amount
        return amount
    
    def __hash__(self):
        """
        Allows for the resource to be hashed.

        :return: The hash of the resource name.
        :rtype: int
        """
        return hash(super().get_name())
    
    def __eq__(self, other: object) -> bool:
        """
        Checks if the resource is equal to another resource.

        :param other: The other resource to compare.
        :type other: object
        :return: True if the resources are equal, False otherwise.
        :rtype: bool
        """
        if not isinstance(other, Resource):
            return False
        return super().get_name() == other.get_name()
    
    def __repr__(self) -> str:
        """
        Returns the string representation of the resource.

        :return: The string representation of the resource.
        :rtype: str
        """
        return f"{super().get_name()}"