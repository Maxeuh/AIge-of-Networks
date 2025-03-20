import typing

if typing.TYPE_CHECKING:
    from controller.view_controller import ViewController


class BaseView:
    """
    Interface for the views of the game.
    """

    def __init__(self, controller: "ViewController") -> None:
        """Initialize the menu view."""
        self.__controller = controller
        self.__running = True

    def show(self) -> None:
        """Display loop for the view."""
        raise NotImplementedError("This method should be overriden by the subclass")
