import typing

import pygame

from model.player.player import Player
from util.map import Map
from view.base_view import BaseView
from view.tile_manager import TileManager

if typing.TYPE_CHECKING:
    from controller.view_controller import ViewController


class View2_5D(BaseView):
    """
    Main class for 2.5D view.
    """

    def __init__(self, controller: "ViewController") -> None:
        """Initialize the menu view."""
        super().__init__(controller)
        self.__map: Map = self._BaseView__controller.get_map()
        self.__running: bool = False

        self.width, self.height = 0, 0
        self.camera_x = 0
        self.camera_y = 0
        self.camera_speed = 2  # Vitesse de déplacement de la caméra
        self.viewport_width = 20  # Nombre de tuiles affichées horizontalement
        self.viewport_height = 15  # Nombre de tuiles affichées verticalement
        self.tile_manager = TileManager()

        # Taille de la carte (en tuiles)
        self.map_size = self.__map.get_size()
        self.tile_size = 40  # Taille d'une tuile
        self.minimap_size = 150  # Taille de la mini-map
        self.minimap_pos = (
            self.width - self.minimap_size - 10,
            self.height - self.minimap_size - 10,
        )

    def render_map(self):
        """
        Render only the visible part of the map using the camera.
        """
        if not self.__running:
            return

        # Chargement de la texture du sol
        grass_block = pygame.transform.scale(
            pygame.image.load("src/block_aoe.png"), (128, 128)
        )

        # Dessiner toute la carte avec un décalage caméra
        for x in range(self.map_size):
            for y in range(self.map_size):
                iso_x = (
                    (x - self.camera_x) * self.tile_size
                    - (y - self.camera_y) * self.tile_size
                    + self.width // 2
                )
                iso_y = (
                    (x - self.camera_x) * (self.tile_size // 2)
                    + (y - self.camera_y) * (self.tile_size // 2)
                    + self.height // 4
                )

                self.screen.blit(grass_block, (iso_x, iso_y))

        # Dessiner les objets à leurs positions
        for coordinate, obj in self.__map.get_map().items():
            if not coordinate or not obj:
                continue

            x, y = coordinate.get_x(), coordinate.get_y()

            iso_x = (
                (x - self.camera_x) * self.tile_size
                - (y - self.camera_y) * self.tile_size
                + self.width // 2
            )
            iso_y = (
                (x - self.camera_x) * (self.tile_size // 2)
                + (y - self.camera_y) * (self.tile_size // 2)
                + self.height // 4
            )

            if obj.get_letter() == "T":
                self.screen.blit(
                    self.tile_manager.get_texture("town_center"), (iso_x, iso_y)
                )

            elif obj.get_letter() == "v":
                self.screen.blit(
                    self.tile_manager.get_texture("villager"), (iso_x, iso_y)
                )

            elif obj.get_letter() == "s":
                self.screen.blit(
                    self.tile_manager.get_texture("swordsman"), (iso_x, iso_y)
                )

            elif obj.get_letter() == "h":
                self.screen.blit(
                    self.tile_manager.get_texture("horseman"), (iso_x, iso_y)
                )

            elif obj.get_letter() == "a":
                self.screen.blit(
                    self.tile_manager.get_texture("archer"), (iso_x, iso_y)
                )

            elif obj.get_letter() == "H":
                self.screen.blit(self.tile_manager.get_texture("house"), (iso_x, iso_y))

            elif obj.get_letter() == "C":
                self.screen.blit(self.tile_manager.get_texture("camp"), (iso_x, iso_y))

            elif obj.get_letter() == "B":
                self.screen.blit(
                    self.tile_manager.get_texture("barracks"), (iso_x, iso_y)
                )

            elif obj.get_letter() == "S":
                self.screen.blit(
                    self.tile_manager.get_texture("stable"), (iso_x, iso_y)
                )

            elif obj.get_letter() == "A":
                self.screen.blit(
                    self.tile_manager.get_texture("archery_range"), (iso_x, iso_y)
                )

            elif obj.get_letter() == "K":
                self.screen.blit(self.tile_manager.get_texture("keep"), (iso_x, iso_y))

            elif obj.get_letter() == "W":
                self.screen.blit(self.tile_manager.get_texture("wood"), (iso_x, iso_y))

            elif obj.get_letter() == "F":
                self.screen.blit(self.tile_manager.get_texture("food"), (iso_x, iso_y))

            elif obj.get_letter() == "G":
                self.screen.blit(self.tile_manager.get_texture("gold"), (iso_x, iso_y))

            elif obj.get_letter() == "x":
                # Add a "🚧" (emoji) to show that something is under construction here
                self.screen.blit(
                    self.tile_manager.get_texture("construction"), (iso_x, iso_y)
                )

            # self.renderer.render_tile(x, y, texture, self.camera)

    def render_minimap(self):
        """
        Render a minimap in the bottom-right corner of the screen.
        It shows the entire map with a rectangle indicating the visible area.
        """
        if not self.__running:
            return

        # Définition de la taille et de la position de la mini-map
        minimap_width = 200
        minimap_height = 200
        minimap_x = self.width - minimap_width - 20  # Décalage de 20px du bord droit
        minimap_y = self.height - minimap_height - 20  # Décalage de 20px du bas

        # Dessiner le fond de la mini-map (bordure noire + fond vert)
        pygame.draw.rect(
            self.screen,
            (0, 0, 0),
            (minimap_x - 2, minimap_y - 2, minimap_width + 4, minimap_height + 4),
        )  # Bordure noire
        pygame.draw.rect(
            self.screen,
            (34, 139, 34),
            (minimap_x, minimap_y, minimap_width, minimap_height),
        )  # Fond vert

        # Échelle de réduction pour que la carte entière tienne dans la mini-map
        scale_x = minimap_width / self.map_size
        scale_y = minimap_height / self.map_size
        # Dessiner les objets sur la mini-map
        for coordinate, obj in self.__map.get_map().items():
            x, y = coordinate.get_x(), coordinate.get_y()
            pixel_x = int(minimap_x + x * scale_x)
            pixel_y = int(minimap_y + y * scale_y)

            # Couleurs différentes selon les objets
            if coordinate is None or obj is None:  # Case vide
                color = (34, 139, 34)  # Par défaut blanc (terrain)
            elif obj.get_letter() == "T":  # Town Center
                color = (255, 215, 0)  # Or
            elif obj.get_letter() == "W":  # Bois
                color = (139, 69, 19)  # Marron
            elif obj.get_letter() == "G":  # Or
                color = (255, 223, 0)  # Jaune
            elif obj.get_letter() == "F":  # Nourriture
                color = (255, 0, 0)  # Rouge
            else:  # Unité
                color = (0, 0, 255)  # Bleu

            pygame.draw.rect(
                self.screen, color, (pixel_x, pixel_y, 3, 3)
            )  # Carré de 3x3 pixels

        # Dessiner un rectangle indiquant la zone actuellement visible sur la grande carte
        viewport_x = int(minimap_x + self.camera_x * scale_x)
        viewport_y = int(minimap_y + self.camera_y * scale_y)
        viewport_width = int(self.viewport_width * scale_x)
        viewport_height = int(self.viewport_height * scale_y)

        pygame.draw.rect(
            self.screen,
            (255, 0, 0),
            (viewport_x, viewport_y, viewport_width, viewport_height),
            2,
        )  # Rouge pour la position caméra

    def show(self) -> None:
        """
        Main loop for the 2.5D view.
        """
        # Initialisation de Pygame
        pygame.init()
        self.width, self.height = (
            pygame.display.Info().current_w,
            pygame.display.Info().current_h,
        )
        self.screen = pygame.display.set_mode(
            (self.width, self.height), pygame.RESIZABLE | pygame.FULLSCREEN
        )
        pygame.display.set_caption("2.5D View")
        self.clock = pygame.time.Clock()
        self.__running = True

        self.__input_loop()

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
        while self.__running:
            # Effacer l'écran et afficher la carte mise à jour
            self.screen.fill((0, 0, 0))
            self.render_map()
            self.render_minimap()
            pygame.display.flip()
            self.clock.tick(self._BaseView__controller.get_settings().fps.value)

            # Gestion des événements
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit()
                    self._BaseView__controller.exit()
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.exit()
                        self._BaseView__controller.exit()
                        return
                    elif event.key == pygame.K_F9:
                        self.exit()
                        self._BaseView__controller.switch_view()
                        return
                    elif event.key == pygame.K_TAB:
                        self.exit()
                        self._BaseView__controller.display_stats()
                        self._BaseView__controller.pause()
                        return
                    elif event.key == pygame.K_p:
                        self.exit()
                        self._BaseView__controller.pause()
                        return
                    elif (
                        event.key == pygame.K_LEFT
                        or event.key == pygame.K_a
                        or event.key == pygame.K_q
                    ) and pygame.key.get_mods() & pygame.KMOD_SHIFT:  # MAJ + ←
                        self.camera_x = max(0, self.camera_x - 5)
                        self.camera_y = min(
                            self.map_size - self.viewport_height, self.camera_y + 5
                        )
                    elif (
                        event.key == pygame.K_LEFT
                        or event.key == pygame.K_q
                        or event.key == pygame.K_a
                    ):  # ←, Q, ou A
                        self.camera_x = max(0, self.camera_x - 1)
                        self.camera_y = min(
                            self.map_size - self.viewport_height, self.camera_y + 1
                        )
                    elif (
                        event.key == pygame.K_RIGHT or event.key == pygame.K_d
                    ) and pygame.key.get_mods() & pygame.KMOD_SHIFT:  # MAJ + →
                        self.camera_x = min(
                            self.map_size - self.viewport_width, self.camera_x + 5
                        )
                        self.camera_y = max(0, self.camera_y - 5)
                    elif (
                        event.key == pygame.K_RIGHT or event.key == pygame.K_d
                    ):  # → ou D
                        self.camera_x = min(
                            self.map_size - self.viewport_width, self.camera_x + 1
                        )
                        self.camera_y = max(0, self.camera_y - 1)
                    elif (
                        event.key == pygame.K_UP
                        or event.key == pygame.K_z
                        or event.key == pygame.K_w
                    ) and pygame.key.get_mods() & pygame.KMOD_SHIFT:  # MAJ + ↑
                        self.camera_x = max(0, self.camera_x - 5)
                        self.camera_y = max(0, self.camera_y - 5)
                    elif (
                        event.key == pygame.K_UP
                        or event.key == pygame.K_z
                        or event.key == pygame.K_w
                    ):  # ↑, Z, ou W
                        self.camera_x = max(0, self.camera_x - 1)
                        self.camera_y = max(0, self.camera_y - 1)
                    elif (
                        event.key == pygame.K_DOWN or event.key == pygame.K_s
                    ) and pygame.key.get_mods() & pygame.KMOD_SHIFT:  # MAJ + ↓
                        self.camera_x = min(
                            self.map_size - self.viewport_width, self.camera_x + 5
                        )
                        self.camera_y = min(
                            self.map_size - self.viewport_height, self.camera_y + 5
                        )
                    elif (
                        event.key == pygame.K_DOWN or event.key == pygame.K_s
                    ):  # ↓ ou S
                        self.camera_x = min(
                            self.map_size - self.viewport_width, self.camera_x + 1
                        )
                        self.camera_y = min(
                            self.map_size - self.viewport_height, self.camera_y + 1
                        )

        self.exit()

    def exit(self) -> None:
        # Close the window
        self.__running = False
        pygame.display.quit()
        pygame.quit()
