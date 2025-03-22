from model.game_object import GameObject
from model.resources.resource import Resource
import typing
if typing.TYPE_CHECKING:
    from model.player.player import Player
    from controller.command import Task

class Entity(GameObject):
    """This class represents the entities (Units and Buildings) on the map."""
    
    def __init__(self, name: str, letter: str, hp: int, cost: dict['Resource', int], spawning_time: int):
        """
        Initializes the entity.

        :param name: The name of the entity.
        :type name: str
        :param letter: The letter representing the entity.
        :type letter: str
        :param hp: The hit points of the entity.
        :type hp: int
        :param cost: The cost of the entity in resources.
        :type cost: dict['Resource', int]
        :param spawning_time: The time it takes to spawn the entity.
        :type spawning_time: int
        """
        super().__init__(name, letter, hp)
        self.__cost: dict[Resource, int] = cost
        self.__spawning_time: int = spawning_time
        self.__player: 'Player' = None
        self.__task: 'Task' = None

    def __repr__(self):
        return f"{self.get_name()} Hp: {self.get_hp()}. Coordinate: {self.get_coordinate()}"
    
    def __repr__(self):
        return f"{self.get_name()} Hp: {self.get_hp()}. Coordinate: {self.get_coordinate()}"
    
    def get_cost(self) -> dict[Resource, int]:
        """
        Returns the cost of the entity.

        :return: The cost of the entity in resources.
        :rtype: dict['Resource', int]
        """
        return self.__cost
    
    def get_spawning_time(self) -> int:
        """
        Returns the spawning time of the entity.

        :return: The spawning time of the entity.
        :rtype: int
        """
        return self.__spawning_time
    def get_player(self) -> 'Player':
        """
        Returns the player associated with the entity.

        :return: The player associated with the entity.
        :rtype: Player
        """
        return self.__player
    def set_player(self, player: 'Player') -> None:
        """
        Sets the player associated with the entity.

        :param player: The player to associate with the entity.
        :type player: Player
        """
        self.__player = player
    
    def get_task(self) -> 'Task':
        """
        Returns the task associated with the entity.

        :return: The task associated with the entity.
        :rtype: Task
        """
        return self.__task
    
    def set_task(self, task: 'Task') -> None:
        """
        Sets the task associated with the entity.

        :param task: The task to associate with the entity.
        :type task: Task
        """
        self.__task = task

    # When a move event happens, make sure any debug prints are controlled
    def move_to(self, coordinate):
        # Get the state before the move
        old_position = None
        if hasattr(self, "get_coordinate") and self.get_coordinate():
            old_position = {
                "x": self.get_coordinate().get_x(),
                "y": self.get_coordinate().get_y()
            }
        
        # Perform the move using your existing code
        self._coordinate = coordinate  # Or however you update position
        
        # Send network update
        if hasattr(self, "_owner") and hasattr(self._owner, "get_game_controller"):
            game_controller = self._owner.get_game_controller()
            if hasattr(game_controller, "event_sender"):
                # Use debug_print instead of print for any debug information
                if hasattr(game_controller, "debug_print"):
                    game_controller.debug_print(f"Entity {self.get_id()} moving to {coordinate.get_x()}, {coordinate.get_y()}")
                event_data = {
                    "entity_id": self.get_id() if hasattr(self, "get_id") else str(id(self)),
                    "entity_type": self.__class__.__name__,
                    "player_id": self._owner.get_id() if hasattr(self, "_owner") else None,
                    "old_position": old_position,
                    "new_position": {
                        "x": coordinate.get_x(),
                        "y": coordinate.get_y()
                    }
                }
                game_controller.event_sender.send_event("MOVE", event_data)

    def get_id(self):
        """Get a unique identifier for this entity"""
        if not hasattr(self, "_entity_id"):
            self._entity_id = str(id(self))
        return self._entity_id

