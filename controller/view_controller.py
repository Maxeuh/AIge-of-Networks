import json
import os
import typing
import webbrowser

import pygame

from model.units.villager import Villager
from util.coordinate import Coordinate
from util.map import Map
from util.settings import Settings
from view.base_view import BaseView
from view.terminal_view import TerminalView
from view.view_2_5D import View2_5D

if typing.TYPE_CHECKING:
    from controller.game_controller import GameController


class ViewController:
    def __init__(self, game_controller: "GameController") -> None:
        """Initialize the view controller."""
        self.__is_terminal: bool = True
        self.__game_controller: "GameController" = game_controller
        self.__current_view: BaseView = TerminalView(self)
        self.__pause: bool = False
        self.__speed = 1  # Initialize speed

    def toggle_speed(self) -> None:
        """Toggle the speed between 1 and 60."""
        self.__speed = 10 if self.__speed == 1 else 1

    def get_speed(self) -> int:
        """Get the current speed."""
        return self.__speed if not self.__pause else 0

    def start_view(self) -> None:
        """Start the view."""
        self.__pause = False
        self.__current_view.show()

    def get_map(self) -> Map:
        """Return the map."""
        return self.__game_controller.get_map()

    def get_settings(self) -> Settings:
        """Return the settings."""
        return self.__game_controller.settings

    def pause(self) -> None:
        """Pause the game."""
        self.__pause = True
        self.__game_controller.pause()

    def exit(self) -> None:
        """Exit the game."""
        self.__game_controller.exit()

    def switch_view(self) -> None:
        """Bascule entre la vue terminale et la vue 2.5D en appuyant sur F12."""
        if self.__is_terminal:
            self.__is_terminal = False
            pygame.init()  # Ajout de l'initialisation pour éviter l'erreur
            self.__current_view = View2_5D(self)
        else:
            self.__is_terminal = True
            self.__current_view = TerminalView(self)
        self.start_view()

    def generate_player_stats(self, player) -> dict:
        """
        Generate a dictionary containing stats for a single player.

        :param player: The player whose stats are being generated.
        :return: A dictionary of player stats.
        """
        return {
            "name": player.get_name(),
            "color": player.get_color(),
            "resources": {
                type(resource).__name__: amount
                for resource, amount in player.get_resources().items()
            },
            "units": [
                {
                    "name": unit.get_name(),
                    "hp": unit.get_hp(),
                    "attack_per_second": unit.get_attack_per_second(),
                    "speed": unit.get_speed(),
                    # Include inventory if the unit has one (e.g., Villager)
                    "inventory": (
                        {
                            type(resource).__name__: amount
                            for resource, amount in getattr(
                                unit, "_Villager__inventory", {}
                            ).items()
                        }
                        if isinstance(unit, Villager)
                        else None
                    ),
                    "inventory_size": (
                        getattr(unit, "_Villager__inventory_size", None)
                        if isinstance(unit, Villager)
                        else None
                    ),
                    "collect_time_per_minute": (
                        getattr(unit, "_Villager__collect_time_per_minute", None)
                        if isinstance(unit, Villager)
                        else None
                    ),
                    "task": str(unit.get_task()),
                }
                for unit in player.get_units()
            ],
            "buildings": [
                {
                    "name": building.get_name(),
                    "hp": building.get_hp(),
                    "size": building.get_size(),
                    "cost": {
                        type(resource).__name__: amount
                        for resource, amount in building.get_cost().items()
                    },
                    "building": str(building.get_task()),
                }
                for building in player.get_buildings()
            ],
        }

    def display_stats(self) -> None:
        """
        Pause the game, and create an HTML webpage that shows stats for all players,
        game settings, and the map.
        """
        players = self.__game_controller.get_players()
        all_players_stats = [self.generate_player_stats(player) for player in players]

        # Generate HTML content
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Game Stats</title>
            <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .collapsible {{
            cursor: pointer;
            padding: 10px;
            background: #007bff;
            color: white;
            border: none;
            border-radius: 5px;
            text-align: left;
            margin-bottom: 5px;
            }}
            .content {{
            padding: 10px;
            display: none;
            background-color: #f9f9f9;
            border: 1px solid #ccc;
            border-radius: 5px;
            margin-bottom: 10px;
            }}
            pre {{
            background: #f4f4f4;
            padding: 10px;
            border-radius: 5px;
            }}
            table {{
            width: 100%;
            border-collapse: collapse;
            }}
            th, td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: center;
            }}
            th {{
            background-color: #f2f2f2;
            }}
            </style>
            <script>
            function toggleContent(id) {{
            var content = document.getElementById(id);
            content.style.display = content.style.display === "block" ? "none" : "block";
            }}
            </script>
        </head>
        <body>
            <h1>Game Stats</h1>
            <h2>Players</h2>
            {self.generate_collapsible_html(all_players_stats)}
            <h2>Settings</h2>
            <p>Map Size: {self.get_settings().map_size.value}</p>
            <p>Map Type: {self.get_settings().map_type}</p>
            <p>FPS: {self.get_settings().fps}</p>
            <p>Starting Condition: {self.get_settings().starting_condition}</p>
        </body>
        </html>
        """

        # Write HTML file
        file_path = os.path.abspath("game_stats.html")
        with open(file_path, "w") as file:
            file.write(html_content)

        # Open in browser
        webbrowser.open(f"file://{file_path}")

    def generate_collapsible_html(self, players_stats: list) -> str:
        """
        Generate collapsible sections for each player's stats.

        :param players_stats: A list of stats for all players.
        :return: An HTML string with collapsible sections.
        """
        html = ""
        for i, player_stats in enumerate(players_stats):
            player_name = player_stats["name"]
            units_html = "".join(
                f"""
                <button class="collapsible" onclick="toggleContent('unit_{i}_{j}')">Unit: {unit['name']}</button>
                <div id="unit_{i}_{j}" class="content">
                    <pre>{json.dumps(unit, indent=4)}</pre>
                </div>
                """
                for j, unit in enumerate(player_stats["units"])
            )
            buildings_html = "".join(
                f"""
                <button class="collapsible" onclick="toggleContent('building_{i}_{j}')">Building: {building['name']}</button>
                <div id="building_{i}_{j}" class="content">
                    <pre>{json.dumps(building, indent=4)}</pre>
                </div>
                """
                for j, building in enumerate(player_stats["buildings"])
            )
            html += f"""
            <button class="collapsible" onclick="toggleContent('player_{i}')">Player: {player_name}</button>
            <div id="player_{i}" class="content">
                <h3>Resources</h3>
                <pre>{json.dumps(player_stats["resources"], indent=4)}</pre>
                <h3>Units</h3>
                {units_html}
                <h3>Buildings</h3>
                {buildings_html}
            </div>
            """
        return html
