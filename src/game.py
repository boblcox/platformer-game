"""Top-level game state machine and main loop."""

from __future__ import annotations

import sys

import pygame

from src.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE,
    TILE_SIZE, TILE_GROUND, TILE_PLATFORM, TILE_WALL,
    PLAYER_START_LIVES, PLAYER_MAX_HEALTH,
    SCORE_COMPLETE_LEVEL,
    SKY_TOP, SKY_MID, SKY_BOTTOM,
    DARK_BROWN, BROWN, DARK_GRAY, GRAY, LIGHT_GRAY, GREEN, DARK_GREEN,
    STATE_MAIN_MENU, STATE_PLAYING, STATE_PAUSED,
    STATE_GAME_OVER, STATE_LEVEL_COMPLETE,
)
from src.camera import Camera
from src.map_generator import MapGenerator
from src.player import Player
from src.enemy import Enemy
from src.sprites import WeaponPickup, Projectile, Ladder
from src.ui import UI
from src.save_load import save_game, load_game, save_exists


# Colours for tile rendering
_GROUND_TOP = (110, 80, 40)
_GROUND_BODY = DARK_BROWN
_GROUND_EDGE = (80, 55, 25)
_PLATFORM_TOP = (90, 130, 60)
_PLATFORM_BODY = (70, 100, 45)
_WALL_COLOR = DARK_GRAY
_GRASS_COLOR = (80, 160, 50)


class Game:
    """Owns the pygame window, game state, and main loop."""

    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption(TITLE)
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.ui = UI(self.screen)

        # Persistent across levels
        self.state = STATE_MAIN_MENU
        self.level = 1
        self.score = 0
        self.lives = PLAYER_START_LIVES

        # Level-local objects (created in _load_level)
        self.tiles: list = []
        self.player: Player = None  # type: ignore[assignment]
        self.enemies: list = []
        self.weapons_group = pygame.sprite.Group()
        self.projectiles_group = pygame.sprite.Group()
        self.ladder: Ladder = None  # type: ignore[assignment]
        self.camera: Camera = None  # type: ignore[assignment]
        self.player_start: tuple = (0, 0)

        # Pre-render a sky gradient surface
        self._sky_surface = self._build_sky()

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------

    def run(self) -> None:
        while True:
            self.clock.tick(FPS)
            self._handle_events()
            self._update()
            self._draw()
            pygame.display.flip()

    # ------------------------------------------------------------------
    # Events
    # ------------------------------------------------------------------

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if self.state == STATE_MAIN_MENU:
                result = self.ui.main_menu_event(event)
                if result == "new_game":
                    self._start_new_game()
                elif result == "load_game":
                    self._do_load_game()
                elif result == "quit":
                    pygame.quit()
                    sys.exit()

            elif self.state == STATE_PLAYING:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.state = STATE_PAUSED
                else:
                    self.player.handle_event(event)

            elif self.state == STATE_PAUSED:
                result = self.ui.pause_menu_event(event)
                if result == "resume":
                    self.state = STATE_PLAYING
                elif result == "save":
                    self._do_save_game()
                elif result == "main_menu":
                    self.state = STATE_MAIN_MENU

            elif self.state == STATE_GAME_OVER:
                result = self.ui.game_over_event(event)
                if result == "retry":
                    self._start_new_game()
                elif result == "main_menu":
                    self.state = STATE_MAIN_MENU

            elif self.state == STATE_LEVEL_COMPLETE:
                result = self.ui.level_complete_event(event)
                if result == "next_level":
                    self._next_level()
                elif result == "main_menu":
                    self.state = STATE_MAIN_MENU

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def _update(self) -> None:
        if self.state != STATE_PLAYING:
            return

        # Player
        self.player.update(
            self.tiles,
            self.enemies,
            self.weapons_group,
            self.ladder,
            self.projectiles_group,
            self.camera,
        )
        self.score += self.player.score_gained

        # Enemies
        for enemy in self.enemies:
            pts = enemy.update(self.tiles, self.player, self.projectiles_group)
            if pts:
                self.score += pts

        # Remove dead enemies
        self.enemies = [e for e in self.enemies if e.alive]

        # Projectiles
        for proj in list(self.projectiles_group):
            proj.update(self.tiles)

        # Weapon pickups (bob animation)
        self.weapons_group.update()

        # Camera
        self.camera.update(self.player.rect)

        # ── State transitions ──────────────────────────────────────────
        if self.player.health <= 0:
            self.lives -= 1
            if self.lives <= 0:
                self.state = STATE_GAME_OVER
            else:
                self.player.respawn(self.player_start)

        if self.player.reached_ladder:
            self.score += SCORE_COMPLETE_LEVEL
            self.state = STATE_LEVEL_COMPLETE

    # ------------------------------------------------------------------
    # Draw
    # ------------------------------------------------------------------

    def _draw(self) -> None:
        if self.state == STATE_MAIN_MENU:
            self.ui.draw_main_menu()

        elif self.state in (STATE_PLAYING, STATE_PAUSED, STATE_LEVEL_COMPLETE):
            self._draw_world()
            self.ui.draw_hud(self.player, self.score, self.level, self.lives)
            if self.state == STATE_PAUSED:
                self.ui.draw_pause_menu()
            elif self.state == STATE_LEVEL_COMPLETE:
                self.ui.draw_level_complete(self.level, self.score)

        elif self.state == STATE_GAME_OVER:
            self.ui.draw_game_over(self.score)

    def _draw_world(self) -> None:
        # Sky
        self.screen.blit(self._sky_surface, (0, 0))

        # Tiles (only those on screen)
        cam_left = self.camera.offset_x // TILE_SIZE - 1
        cam_right = (self.camera.offset_x + SCREEN_WIDTH) // TILE_SIZE + 2
        cam_top = self.camera.offset_y // TILE_SIZE - 1
        cam_bot = (self.camera.offset_y + SCREEN_HEIGHT) // TILE_SIZE + 2

        h = len(self.tiles)
        w = len(self.tiles[0]) if h else 0

        for row in range(max(0, cam_top), min(h, cam_bot + 1)):
            for col in range(max(0, cam_left), min(w, cam_right + 1)):
                tile = self.tiles[row][col]
                if tile == 0:
                    continue
                sx = col * TILE_SIZE - self.camera.offset_x
                sy = row * TILE_SIZE - self.camera.offset_y
                rect = pygame.Rect(sx, sy, TILE_SIZE, TILE_SIZE)

                if tile == TILE_GROUND:
                    pygame.draw.rect(self.screen, _GROUND_BODY, rect)
                    pygame.draw.rect(self.screen, _GROUND_TOP, (sx, sy, TILE_SIZE, 6))
                    pygame.draw.rect(self.screen, _GROUND_EDGE, rect, 1)
                elif tile == TILE_PLATFORM:
                    pygame.draw.rect(self.screen, _PLATFORM_BODY, rect)
                    pygame.draw.rect(self.screen, _PLATFORM_TOP, (sx, sy, TILE_SIZE, 6))
                    pygame.draw.rect(self.screen, _GROUND_EDGE, rect, 1)
                elif tile == TILE_WALL:
                    pygame.draw.rect(self.screen, _WALL_COLOR, rect)
                    pygame.draw.rect(self.screen, GRAY, rect, 1)

        # Ladder
        if self.ladder:
            self.ladder.draw(self.screen, self.camera)

        # Weapon pickups
        for pickup in self.weapons_group:
            pickup.draw(self.screen, self.camera)

        # Enemies
        for enemy in self.enemies:
            enemy.draw(self.screen, self.camera)

        # Projectiles
        for proj in self.projectiles_group:
            proj.draw(self.screen, self.camera)

        # Player
        self.player.draw(self.screen, self.camera)

    # ------------------------------------------------------------------
    # Sky gradient (precomputed)
    # ------------------------------------------------------------------

    @staticmethod
    def _build_sky() -> pygame.Surface:
        surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        for y in range(SCREEN_HEIGHT):
            t = y / SCREEN_HEIGHT
            r = int(SKY_TOP[0] * (1 - t) + SKY_BOTTOM[0] * t)
            g = int(SKY_TOP[1] * (1 - t) + SKY_BOTTOM[1] * t)
            b = int(SKY_TOP[2] * (1 - t) + SKY_BOTTOM[2] * t)
            pygame.draw.line(surf, (r, g, b), (0, y), (SCREEN_WIDTH, y))
        return surf

    # ------------------------------------------------------------------
    # Game management
    # ------------------------------------------------------------------

    def _start_new_game(self) -> None:
        self.level = 1
        self.score = 0
        self.lives = PLAYER_START_LIVES
        self._load_level()
        self.state = STATE_PLAYING

    def _load_level(self, saved_weapon: str = "fists", saved_health: int = PLAYER_MAX_HEALTH) -> None:
        """Build the level from the procedural generator."""
        gen = MapGenerator(self.level)
        tiles, player_pos, enemy_positions, weapon_positions, ladder_pos = gen.generate()

        self.tiles = tiles
        self.player_start = player_pos

        map_pw = len(tiles[0]) * TILE_SIZE
        map_ph = len(tiles) * TILE_SIZE

        self.player = Player(*player_pos)
        self.player.weapon = saved_weapon
        self.player.health = saved_health

        self.enemies = [Enemy(ex, ey, self.level) for ex, ey in enemy_positions]

        self.weapons_group = pygame.sprite.Group(
            WeaponPickup(wx, wy, wk) for wx, wy, wk in weapon_positions
        )
        self.projectiles_group = pygame.sprite.Group()
        self.ladder = Ladder(*ladder_pos)

        self.camera = Camera(map_pw, map_ph)
        self.camera.update(self.player.rect)

    def _next_level(self) -> None:
        saved_weapon = self.player.weapon
        saved_health = min(self.player.health + 20, PLAYER_MAX_HEALTH)  # small heal
        self.level += 1
        self._load_level(saved_weapon, saved_health)
        self.state = STATE_PLAYING

    def _do_save_game(self) -> None:
        data = {
            "level": self.level,
            "score": self.score,
            "lives": self.lives,
            "health": self.player.health,
            "weapon": self.player.weapon,
        }
        if save_game(data):
            self.ui.show_save_notification()

    def _do_load_game(self) -> None:
        data = load_game()
        if data is None:
            return  # no save – do nothing; button stays visible but benign
        self.level = data.get("level", 1)
        self.score = data.get("score", 0)
        self.lives = data.get("lives", PLAYER_START_LIVES)
        saved_health = data.get("health", PLAYER_MAX_HEALTH)
        saved_weapon = data.get("weapon", "fists")
        self._load_level(saved_weapon, saved_health)
        self.state = STATE_PLAYING
