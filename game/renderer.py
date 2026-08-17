"""Rendering logic for the strategy game."""

from __future__ import annotations

from pathlib import Path

import pygame

from .buildings import Building, BuildingType
from .hex_grid import HexCoord, HexGrid, TerrainType
from .ui import UIPanel
from .units import Unit


class GameRenderer:
    SCREEN_WIDTH = 1200
    SCREEN_HEIGHT = 800
    HEX_COLORS = {
        TerrainType.GRASS: (100, 180, 80),
        TerrainType.FOREST: (40, 120, 40),
        TerrainType.MOUNTAIN: (140, 120, 100),
        TerrainType.WATER: (60, 120, 200),
        TerrainType.DESERT: (200, 180, 100),
    }

    def __init__(self) -> None:
        self.assets = Path(__file__).resolve().parent.parent / "assets" / "sprites"
        self.ui_panel = UIPanel(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        self.font = pygame.font.SysFont("arial", 16)
        self.big_font = pygame.font.SysFont("arial", 48, bold=True)
        self.selected_unit: Unit | None = None
        self.selected_building: Building | None = None
        self.tooltip_text: str | None = None
        self._sprite_cache: dict[str, pygame.Surface] = {}

    def _load_sprite(self, name: str) -> pygame.Surface:
        if name not in self._sprite_cache:
            path = self.assets / name
            self._sprite_cache[name] = pygame.image.load(str(path)).convert_alpha()
        return self._sprite_cache[name]

    def _scaled_sprite(self, name: str, scale: float) -> pygame.Surface:
        sprite = self._load_sprite(name)
        size = max(16, int(sprite.get_width() * scale))
        return pygame.transform.smoothscale(sprite, (size, size))

    def _draw_hex_overlay(self, surface: pygame.Surface, grid: HexGrid, coord: HexCoord, camera, color: tuple[int, int, int, int]) -> None:
        points = [camera.world_to_screen(x, y) for x, y in grid.hex_corners(coord)]
        overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.polygon(overlay, color, points)
        surface.blit(overlay, (0, 0))

    def render_map(self, surface: pygame.Surface, grid: HexGrid, fog, camera) -> None:
        for coord in grid.all_hexes():
            terrain = grid.get_tile(coord)
            world_x, world_y = grid.axial_to_pixel(coord)
            screen_x, screen_y = camera.world_to_screen(world_x, world_y)
            sprite = self._scaled_sprite(f"{terrain.value.lower()}.png", camera.zoom)
            rect = sprite.get_rect(center=(screen_x, screen_y))
            surface.blit(sprite, rect)
            if fog.is_visible(coord):
                pygame.draw.polygon(surface, (*self.HEX_COLORS[terrain], 0), [camera.world_to_screen(x, y) for x, y in grid.hex_corners(coord)], 1)

    def render_buildings(self, surface: pygame.Surface, buildings: list[Building], fog, camera) -> None:
        for building in buildings:
            if not fog.is_visible(building.hex_pos):
                continue
            if building.building_type == BuildingType.CASTLE:
                sprite_name = f"castle_p{building.owner + 1}.png"
            elif building.building_type == BuildingType.VILLAGE:
                sprite_name = "village.png"
            elif building.building_type == BuildingType.BARRACKS:
                sprite_name = "barracks.png"
            else:
                sprite_name = "tower.png"
            world_x, world_y = building.hex_pos.to_pixel(camera.zoom * 0 + 40.0)
            screen_x, screen_y = camera.world_to_screen(world_x, world_y)
            sprite = self._scaled_sprite(sprite_name, camera.zoom * 0.9)
            rect = sprite.get_rect(center=(screen_x, screen_y - int(8 * camera.zoom)))
            surface.blit(sprite, rect)
            if self.selected_building == building:
                selected = self._scaled_sprite("selected.png", camera.zoom)
                surface.blit(selected, selected.get_rect(center=(screen_x, screen_y)))

    def render_units(self, surface: pygame.Surface, units: list[Unit], fog, camera) -> None:
        for unit in units:
            if not fog.is_visible(unit.hex_pos):
                continue
            sprite_name = f"{unit.unit_type.value.lower()}_p{unit.owner + 1}.png"
            world_x, world_y = unit.hex_pos.to_pixel(40.0)
            screen_x, screen_y = camera.world_to_screen(world_x, world_y)
            sprite = self._scaled_sprite(sprite_name, camera.zoom)
            rect = sprite.get_rect(center=(screen_x, screen_y - int(6 * camera.zoom)))
            surface.blit(sprite, rect)
            self.render_health_bar(surface, unit, (screen_x, screen_y + int(24 * camera.zoom)))
            if self.selected_unit == unit:
                selected = self._scaled_sprite("selected.png", camera.zoom)
                surface.blit(selected, selected.get_rect(center=(screen_x, screen_y)))

    def render_fog(self, surface: pygame.Surface, grid: HexGrid, fog, camera) -> None:
        overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA)
        for coord in grid.all_hexes():
            points = [camera.world_to_screen(x, y) for x, y in grid.hex_corners(coord)]
            if not fog.is_explored(coord):
                pygame.draw.polygon(overlay, (0, 0, 0, 255), points)
            elif not fog.is_visible(coord):
                pygame.draw.polygon(overlay, (0, 0, 0, 140), points)
        surface.blit(overlay, (0, 0))

    def render_health_bar(self, surface: pygame.Surface, unit: Unit, screen_pos: tuple[int, int]) -> None:
        width = max(24, int(36))
        bar_rect = pygame.Rect(screen_pos[0] - width // 2, screen_pos[1], width, 6)
        pygame.draw.rect(surface, (40, 40, 40), bar_rect)
        fill = int(bar_rect.width * (unit.hp / unit.max_hp))
        pygame.draw.rect(surface, (80, 220, 80), (bar_rect.x, bar_rect.y, fill, bar_rect.height))
        pygame.draw.rect(surface, (250, 250, 250), bar_rect, 1)

    def render_ui(self, surface: pygame.Surface, game_state, selected_unit: Unit | None = None) -> None:
        current = game_state.active_player
        current.owned_buildings_cache = game_state.get_buildings_for_player(current.id)
        self.ui_panel.draw_background(surface)
        self.ui_panel.draw_turn_info(surface, game_state)
        self.ui_panel.draw_resource_info(surface, current)
        self.ui_panel.draw_unit_info(surface, selected_unit)
        self.ui_panel.draw_action_buttons(surface)

    def render_frame(
        self,
        surface: pygame.Surface,
        game_state,
        camera,
        selected_unit: Unit | None = None,
        selected_building: Building | None = None,
        movement_range: list[HexCoord] | None = None,
        attack_range: list[HexCoord] | None = None,
        hovered_hex: HexCoord | None = None,
    ) -> None:
        surface.fill((12, 16, 24))
        self.selected_unit = selected_unit
        self.selected_building = selected_building
        fog = game_state.active_player.fog
        self.render_map(surface, game_state.grid, fog, camera)
        for coord in movement_range or []:
            if fog.is_explored(coord):
                self._draw_hex_overlay(surface, game_state.grid, coord, camera, (80, 140, 255, 90))
        for coord in attack_range or []:
            if fog.is_explored(coord):
                self._draw_hex_overlay(surface, game_state.grid, coord, camera, (255, 70, 70, 90))
        self.render_buildings(surface, game_state.buildings, fog, camera)
        self.render_units(surface, game_state.units, fog, camera)
        if hovered_hex and game_state.grid.in_bounds(hovered_hex):
            points = [camera.world_to_screen(x, y) for x, y in game_state.grid.hex_corners(hovered_hex)]
            pygame.draw.polygon(surface, (255, 255, 255), points, 2)
        self.render_fog(surface, game_state.grid, fog, camera)
        self.render_ui(surface, game_state, selected_unit)
        if self.tooltip_text:
            self.ui_panel.draw_tooltip(surface, self.tooltip_text, pygame.mouse.get_pos())
        if game_state.game_phase.value == "GAME_OVER" and game_state.winner is not None:
            winner = game_state.players[game_state.winner]
            text = self.big_font.render(f"{winner.name} Wins!", True, winner.color)
            shadow = self.big_font.render(f"{winner.name} Wins!", True, (20, 20, 20))
            rect = text.get_rect(center=(self.SCREEN_WIDTH // 2 - 100, self.SCREEN_HEIGHT // 2))
            surface.blit(shadow, rect.move(3, 3))
            surface.blit(text, rect)
