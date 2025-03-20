from controller.command_controller import CommandController


class TaskController:
    """This class is responsible for managing tasks."""

    def __init__(self, command_manager: CommandController) -> None:
        """
        Initializes the TaskController with the given CommandController.
        :param command_manager: The command manager of the player that will execute the task.
        :type command_manager: CommandController
        """
        self.__command_manager: CommandController = command_manager

    def execute_tasks(self) -> None:
        """
        Executes all assigned tasks in
        """
        for unit in self.__command_manager.get_player().get_units():
            if unit.get_task() is not None:
                try:
                    unit.get_task().execute_task()
                except (ValueError, IndexError) as e:
                    # print(f"Error executing task by {unit.get_name()} at {unit.get_coordinate()}")
                    # import traceback
                    # print(traceback.format_exc())
                    # print(e)
                    # exit()
                    unit.set_task(None)
        for building in self.__command_manager.get_player().get_buildings():
            if building.get_task() is not None:
                try:
                    building.get_task().execute_task()
                except (ValueError, IndexError):
                    building.set_task(None)
