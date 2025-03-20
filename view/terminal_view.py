import threading
import time
import typing

from blessed import Terminal

from util.coordinate import Coordinate
from util.map import Map
from view.base_view import BaseView

if typing.TYPE_CHECKING:
    from controller.view_controller import ViewController

# NOTE: On Terminal, the first line is ALWAYS HIDDEN. So the first line showing is actually the 2nd line.
# The same goes for the last line: the last line "n" is actually the line "n+1".
#
# Example:
# [1] 0 > hidden to keep height = 4 and because you wrote on line 4
# [2] 1 >
# [3] 2 > (3,1)
# [4] 3 > (3,1)
# [5] 4 > Bottom is here


class TerminalView(BaseView):
    """
    Terminal view for the game. It's used to display the game map and allow the player to navigate it using ZQSD and the arrow keys.
    Print the map in the Terminal depending on the player's position and the size of the viewport.
    Automatically update each tick.
    """

    def __init__(self, controller: "ViewController") -> None:
        """Initialize the menu view."""
        super().__init__(controller)
        self.__terminal = Terminal()
        self.__from_coord = Coordinate(0, 0)
        self.__to_coord = Coordinate(0, 0)
        self.__stop_event = threading.Event()

        self.__size()
        self.__map: Map = self._BaseView__controller.get_map()

        self.__display_thread = threading.Thread(target=self.__display_loop)
        # self.__input_thread = threading.Thread(target=self.__input_loop)
        self.__isFaster = False

    def show(self) -> None:
        """Start the display and input threads."""
        self.__stop_event.clear()
        if not self.__display_thread.is_alive():
            self.__display_thread = threading.Thread(target=self.__display_loop)
            self.__display_thread.start()
        # self.__input_thread.start()
        self.__input_loop()

    def __size(self) -> None:
        """
        Take care of the fact that the first line is always hidden and the last line is the n+1 line.
        """
        self.__terminal_width = self.__terminal.width
        self.__terminal_height = self.__terminal.height - 1

    def __str_frame(self):
        """
        Using "┌", "┐", "└", "┘", "─" and "│" characters, create a frame with the size of the terminal or the map, whichever is smaller.
        The frame is used to separate the map from the text.
        """
        frame_width = min(self.__terminal_width, self.__map.get_size() + 2)
        frame_height = min(self.__terminal_height, self.__map.get_size() + 2)

        frame = []
        frame.append("┌" + "─" * (frame_width - 2) + "┐")
        for _ in range(frame_height - 2):
            frame.append("│" + " " * (frame_width - 2) + "│")
        frame.append("└" + "─" * (frame_width - 2) + "┘")
        return frame

    def __str_map(self) -> list[str]:
        """
        Print the map in the terminal using the string representation of the Map object.
        Using the __from_coord coordinate and the self.__terminal_width and self.__terminal_height, calculate the from and to coordinates to print the map.
        Use the method Map.get_from_to(from_coord, to_coord) to get the map part to print.
        Consider the fact that the map is displayed inside the frame, so the map is shifted by 1 to the left, 1 to the top, 1 to the right and 1 to the bottom.
        """
        map_width = min(self.__terminal_width - 2, self.__map.get_size())
        map_height = min(self.__terminal_height - 2, self.__map.get_size())
        self.__to_coord = self.__from_coord + Coordinate(map_width, map_height)
        self.__view = self.__map.get_from_to(self.__from_coord, self.__to_coord)
        map_lines = str(self.__view).split("\n")
        cropped_lines = [line[:map_width] for line in map_lines[:map_height]]
        return cropped_lines

    def __colored_line(self, line: str, frame_line: str, y: int) -> str:
        """
        Color the map elements: uppercase letters in red and bold, lowercase letters in blue, and hide empty spaces.
        Include the frame in the colored line.
        """
        x = 0
        colored_line = ""
        abs_y = self.__from_coord.get_y() + y
        for char in line:
            abs_x = self.__from_coord.get_x() + x
            if char == "·":
                colored_line += " "
            elif char == "G":  # Gold
                colored_line += f"\033[33mG\033[0m"  # Yellow
            elif char == "W":  # Wood
                colored_line += f"\033[38;5;94mW\033[0m"  # Brown
            elif char == "F":  # Food
                colored_line += f"\033[32mF\033[0m"  # Green
            else:
                color = self.__map.indicate_color(Coordinate(abs_x, abs_y))
                if color == "white":
                    colored_line += char
                elif color == "blue":
                    colored_line += f"\033[34m{char}\033[0m"
                elif color == "red":
                    colored_line += f"\033[31m{char}\033[0m"
                elif color == "green":
                    colored_line += f"\033[32m{char}\033[0m"
                elif color == "yellow":
                    colored_line += f"\033[33m{char}\033[0m"
                elif color == "purple":
                    colored_line += f"\033[35m{char}\033[0m"
                elif color == "cyan":
                    colored_line += f"\033[36m{char}\033[0m"
                elif color == "pink":
                    colored_line += f"\033[95m{char}\033[0m"
                elif color == "orange":
                    colored_line += f"\033[93m{char}\033[0m"
                else:
                    # Default color handling
                    colored_line += f"\033[33m{char}\033[0m"
            x += 1
        return (
            frame_line[:1]
            + colored_line
            + self.__terminal.normal
            + frame_line[1 + len(line) :]
        )

    def __add_coord(self, line: list[str]) -> list[str]:
        """
        Add the top left coordinate on the top left corner of the frame.
        Add the bottom right coordinate on the bottom right corner of the frame.
        Append 'x1' or 'x60' based on the value of self.__isFaster.
        """
        # Coordinates
        top_left = f"({self.__from_coord.get_x()}, {self.__from_coord.get_y()})"
        bottom_right_coord = self.__to_coord - 1
        bottom_right = f"({bottom_right_coord.get_x()}, {bottom_right_coord.get_y()})"

        # Determine speed factor based on self.__isFaster
        speed_factor = "x10" if self.__isFaster else "x1"

        # Add the speed factor to the coordinates
        top_left = f"{top_left} {speed_factor}"

        # Update the top-left and bottom-right coordinates in the line
        line[0] = f"{top_left}{line[0][len(top_left):]}"
        line[-1] = f"{line[-1][:len(line[-1]) - len(bottom_right)]}{bottom_right}"

        return line

    def __display_loop(self) -> None:
        """
        Display the map in the terminal and update it each tick (depending on the FPS).
        """
        with self.__terminal.fullscreen(), self.__terminal.cbreak(), self.__terminal.hidden_cursor():
            while not self.__stop_event.is_set():
                self.__size()
                if self.__terminal_width < 10 or self.__terminal_height < 10:
                    print(self.__terminal.clear(), end="")
                    print(
                        self.__terminal.bold_red(
                            "Error: Terminal size is too small. Please resize the terminal."
                        )
                    )
                    self.__terminal.flush()
                    time.sleep(1)
                    continue

                frame = self.__str_frame()
                map_part = self.__str_map()
                output = []
                y = 0
                for i, line in enumerate(
                    map_part[: min(len(map_part), self.__terminal_height - 2)]
                ):
                    frame[i + 1] = self.__colored_line(line, frame[i + 1], y)
                    y += 1
                frame = self.__add_coord(frame)

                # Join the frame into a single string to minimize I/O calls
                output.append("\n".join(frame))
                print(
                    self.__terminal.move(0, 0) + "".join(output), end=""
                )  # Use cursor positioning
                self.__terminal.flush()
                time.sleep(1 / self._BaseView__controller.get_settings().fps.value)

    def __input_loop(self) -> None:
        """
        Handle the user input to move the viewport.

        ZQSD or WASD or arrow keys are used to move the viewport.
        MAJ + ZQSD or MAJ + WASD or MAJ + arrow keys are used to move the viewport by 5 cells.
        P is used to pause the game.
        TAB is used to pause the game and display the stats menu.
        ECHAP is used to exit the game.
        F9 is used to take switch view.
        V is used to toggle speed between 1 and 60.

        :return: None
        """
        while not self.__stop_event.is_set():
            key = self.__terminal.inkey()
            if key in ["z", "w"] or key.code == self.__terminal.KEY_UP:
                self.__from_coord += Coordinate(0, -1)
            elif key == "s" or key.code == self.__terminal.KEY_DOWN:
                self.__from_coord += Coordinate(0, 1)
            elif key in ["q", "a"] or key.code == self.__terminal.KEY_LEFT:
                self.__from_coord += Coordinate(-1, 0)
            elif key == "d" or key.code == self.__terminal.KEY_RIGHT:
                self.__from_coord += Coordinate(1, 0)
            elif key in ["U", "u"]:  # Sauvegarde
                self._BaseView__controller.save_game()
            elif key in ["Z", "W"]:
                self.__from_coord += Coordinate(0, -5)
            elif key == "S":
                self.__from_coord += Coordinate(0, 5)
            elif key in ["Q", "A"]:
                self.__from_coord += Coordinate(-5, 0)
            elif key == "D":
                self.__from_coord += Coordinate(5, 0)
            elif key in ["p", "P"]:
                self.exit()
                self._BaseView__controller.pause()
            elif key.code == self.__terminal.KEY_TAB:
                self.exit()
                self._BaseView__controller.display_stats()
                self._BaseView__controller.pause()
            elif key.code == self.__terminal.KEY_ESCAPE:
                self.exit()
                self._BaseView__controller.exit()
            elif key.code == self.__terminal.KEY_F9:
                self.exit()
                self._BaseView__controller.switch_view()
            elif key.lower() == "v":
                self._BaseView__controller.toggle_speed()
                if self.__isFaster == False:
                    self.__isFaster = True
                else:
                    self.__isFaster = False

            self.__from_coord = Coordinate(
                max(
                    0,
                    min(
                        self.__map.get_size() - self.__terminal_width + 2,
                        self.__from_coord.get_x(),
                    ),
                ),
                max(
                    0,
                    min(
                        self.__map.get_size() - self.__terminal_height + 2,
                        self.__from_coord.get_y(),
                    ),
                ),
            )

    def exit(self):
        self.__stop_event.set()
        if threading.current_thread() != self.__display_thread:
            self.__display_thread.join()
        # if threading.current_thread() != self.__input_thread:
        #     self.__input_thread.join()
