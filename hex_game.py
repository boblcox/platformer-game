"""Entry point for the hex-based fantasy strategy game."""

from __future__ import annotations

import argparse
import os
from collections import deque
from typing import Optional


def configure_headless(headless: bool) -> None:
    if headless:
        os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
        os.environ.setdefault("SDL_AUDIODRIVER", "dummy")


import pygame

from game.ai import AIPlayer
from game.game_state import GamePhase, GameState
from game.hex_grid import HexCoord
from game.renderer import GameRenderer
from game.camera import Camera
from game.units import UnitType


class HexStrategyGame:
    def __init__(self, headless: bool = False) -> None:
        configure_headless(headless)
        pygame.init()
        pygame.display.set_caption("Hex Fantasy Strategy")
        self.screen = pygame.display.set_mode((GameRenderer.SCREEN_WIDTH, GameRenderer.SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.headless = headless
        self.game_state = GameState.create_default()
        self.camera = Camera()
        self.renderer = GameRenderer()
        self.selected_unit = None
        self.selected_building = None
        self.hovered_hex: Optional[HexCoord] = None
        self.running = True
        self.ai_players = {player.id: AIPlayer(player.id) for player in self.game_state.players if player.is_ai}
        self.ai_delay_ms = 450
        self.turn_started_at = pygame.time.get_ticks()

    def screen_to_hex(self, pos: tuple[int, int]) -> Optional[HexCoord]:
        if pos[0] >= GameRenderer.SCREEN_WIDTH - self.renderer.ui_panel.WIDTH:
            return None
        world_x, world_y = self.camera.screen_to_world(*pos)
        coord = self.game_state.grid.pixel_to_axial(world_x, world_y)
        if self.game_state.grid.in_bounds(coord):
            return coord
        return None

    def compute_movement_range(self, unit) -> list[HexCoord]:
        frontier = deque([(unit.hex_pos, 0.0)])
        visited = {unit.hex_pos: 0.0}
        reachable = []
        while frontier:
            current, cost = frontier.popleft()
            for neighbor in self.game_state.grid.get_neighbors(current):
                step_cost = self.game_state.terrain_movement_cost(neighbor)
                if step_cost == float("inf"):
                    continue
                if self.game_state.get_unit_at(neighbor) is not None and neighbor != unit.hex_pos:
                    continue
                new_cost = cost + step_cost
                if new_cost > unit.movement:
                    continue
                if new_cost < visited.get(neighbor, float("inf")):
                    visited[neighbor] = new_cost
                    frontier.append((neighbor, new_cost))
                    reachable.append(neighbor)
        return reachable

    def compute_attack_range(self, unit) -> list[HexCoord]:
        return [
            coord
            for coord in unit.hex_pos.within(unit.attack_range)
            if self.game_state.grid.in_bounds(coord) and coord != unit.hex_pos
        ]

    def update_tooltip(self, mouse_pos: tuple[int, int]) -> None:
        coord = self.screen_to_hex(mouse_pos)
        self.hovered_hex = coord
        if coord is None:
            self.renderer.tooltip_text = None
            return
        terrain = self.game_state.grid.get_tile(coord)
        unit = self.game_state.get_unit_at(coord)
        building = self.game_state.get_building_at(coord)
        parts = [f"Hex: ({coord.q}, {coord.r})", f"Terrain: {terrain.value.title()}"]
        if unit:
            parts.append(f"Unit: {unit.name} P{unit.owner + 1} HP {unit.hp}/{unit.max_hp}")
        if building:
            owner = "Neutral" if building.owner is None else f"P{building.owner + 1}"
            parts.append(f"Building: {building.name} {owner}")
        self.renderer.tooltip_text = "\n".join(parts)

    def select_at(self, mouse_pos: tuple[int, int]) -> None:
        coord = self.screen_to_hex(mouse_pos)
        if coord is None:
            return
        fog = self.game_state.active_player.fog
        if not fog.is_explored(coord):
            return
        unit = self.game_state.get_unit_at(coord)
        building = self.game_state.get_building_at(coord)
        self.selected_unit = unit
        self.selected_building = building if building and unit is None else None

    def try_attack_or_move(self, mouse_pos: tuple[int, int]) -> None:
        coord = self.screen_to_hex(mouse_pos)
        if coord is None or self.selected_unit is None:
            return
        if self.selected_unit.owner != self.game_state.current_player or self.game_state.active_player.is_ai:
            return
        target_unit = self.game_state.get_unit_at(coord)
        if target_unit and target_unit.owner != self.selected_unit.owner:
            if self.game_state.attack_unit(self.selected_unit, target_unit):
                if not self.selected_unit.is_alive() or self.selected_unit.has_attacked:
                    self.selected_unit = None
            return
        if self.game_state.move_unit(self.selected_unit, coord) and self.selected_unit.has_moved:
            self.selected_building = self.game_state.get_building_at(coord)

    def end_turn(self) -> None:
        self.selected_unit = None
        self.selected_building = None
        self.game_state.next_turn()
        self.turn_started_at = pygame.time.get_ticks()

    def recruit_from_selection(self) -> None:
        building = self.selected_building or (self.game_state.get_building_at(self.selected_unit.hex_pos) if self.selected_unit else None)
        if building is None or building.owner != self.game_state.current_player:
            return
        recruit_order = [UnitType.ARCHER, UnitType.WARRIOR, UnitType.MAGE, UnitType.CAVALRY, UnitType.CATAPULT]
        for unit_type in recruit_order:
            if unit_type not in building.get_recruitable_units():
                continue
            created = self.game_state.recruit_unit(building, unit_type)
            if created:
                self.selected_unit = created
                self.selected_building = building
                return

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.MOUSEMOTION:
            self.update_tooltip(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.renderer.ui_panel.end_turn_button.is_clicked(event):
                    self.end_turn()
                else:
                    self.select_at(event.pos)
            elif event.button == 3:
                self.try_attack_or_move(event.pos)
            elif event.button == 4:
                self.camera.zoom_in()
            elif event.button == 5:
                self.camera.zoom_out()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.selected_unit = None
                self.selected_building = None
            elif event.key == pygame.K_e:
                self.end_turn()
            elif event.key == pygame.K_r:
                self.recruit_from_selection()

    def update(self) -> None:
        keys = pygame.key.get_pressed()
        self.camera.handle_keyboard(keys)
        self.update_tooltip(pygame.mouse.get_pos())
        if self.game_state.game_phase == GamePhase.GAME_OVER:
            return
        if self.game_state.active_player.is_ai:
            now = pygame.time.get_ticks()
            if now - self.turn_started_at >= self.ai_delay_ms:
                ai = self.ai_players[self.game_state.current_player]
                ai.execute_actions(self.game_state)
                self.end_turn()

    def render(self) -> None:
        movement_range = []
        attack_range = []
        if self.selected_unit and self.selected_unit.owner == self.game_state.current_player and not self.game_state.active_player.is_ai:
            if not self.selected_unit.has_moved:
                movement_range = self.compute_movement_range(self.selected_unit)
            attack_range = self.compute_attack_range(self.selected_unit)
        self.renderer.render_frame(
            self.screen,
            self.game_state,
            self.camera,
            selected_unit=self.selected_unit,
            selected_building=self.selected_building,
            movement_range=movement_range,
            attack_range=attack_range,
            hovered_hex=self.hovered_hex,
        )
        pygame.display.flip()

    def run(self) -> None:
        while self.running:
            for event in pygame.event.get():
                self.handle_event(event)
            self.update()
            self.render()
            self.clock.tick(60)
        pygame.quit()

    def run_headless_test(self) -> None:
        self.update_tooltip((120, 120))
        self.render()
        ai = self.ai_players[1]
        _ = ai.evaluate_board(self.game_state)
        self.game_state.players[1].fog.update(self.game_state.units, self.game_state.buildings, self.game_state.grid)
        pygame.quit()
        print("Headless test completed successfully.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Hex fantasy strategy game")
    parser.add_argument("--headless-test", action="store_true", help="Run a non-interactive validation pass.")
    args = parser.parse_args()
    configure_headless(args.headless_test)
    game = HexStrategyGame(headless=args.headless_test)
    if args.headless_test:
        game.run_headless_test()
    else:
        game.run()


if __name__ == "__main__":
    main()
