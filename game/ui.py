"""User interface rendering helpers."""

from __future__ import annotations

from dataclasses import dataclass

import pygame


@dataclass
class Button:
    rect: pygame.Rect
    text: str
    bg_color: tuple[int, int, int] = (70, 70, 90)
    hover_color: tuple[int, int, int] = (100, 100, 130)
    text_color: tuple[int, int, int] = (240, 240, 240)

    def is_hovered(self, mouse_pos: tuple[int, int]) -> bool:
        return self.rect.collidepoint(mouse_pos)

    def is_clicked(self, event: pygame.event.Event) -> bool:
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos)

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        mouse_pos = pygame.mouse.get_pos()
        color = self.hover_color if self.is_hovered(mouse_pos) else self.bg_color
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, (220, 220, 220), self.rect, 2, border_radius=8)
        text_surface = font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)


class UIPanel:
    WIDTH = 200

    def __init__(self, screen_width: int, screen_height: int) -> None:
        self.rect = pygame.Rect(screen_width - self.WIDTH, 0, self.WIDTH, screen_height)
        self.font = pygame.font.SysFont("arial", 18)
        self.small_font = pygame.font.SysFont("arial", 14)
        self.title_font = pygame.font.SysFont("arial", 22, bold=True)
        self.end_turn_button = Button(pygame.Rect(self.rect.x + 25, self.rect.bottom - 75, 150, 42), "End Turn")

    def _draw_section_title(self, surface: pygame.Surface, text: str, y: int) -> int:
        rendered = self.title_font.render(text, True, (255, 255, 255))
        surface.blit(rendered, (self.rect.x + 12, y))
        return y + rendered.get_height() + 6

    def draw_background(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, (26, 28, 38), self.rect)
        pygame.draw.line(surface, (90, 96, 122), (self.rect.x, 0), (self.rect.x, self.rect.bottom), 2)

    def draw_turn_info(self, surface: pygame.Surface, game_state) -> int:
        y = self._draw_section_title(surface, "Turn", 14)
        current_name = game_state.active_player.name
        lines = [f"Turn: {game_state.turn_number}", f"Player: {current_name}"]
        for line in lines:
            rendered = self.font.render(line, True, (230, 230, 230))
            surface.blit(rendered, (self.rect.x + 14, y))
            y += 22
        return y + 8

    def draw_resource_info(self, surface: pygame.Surface, player) -> int:
        y = self._draw_section_title(surface, "Resources", 92)
        income = sum(building.gold_income for building in getattr(player, "owned_buildings_cache", []))
        lines = [f"Gold: {player.resources.gold}", f"Income: {income}"]
        for line in lines:
            rendered = self.font.render(line, True, (230, 230, 230))
            surface.blit(rendered, (self.rect.x + 14, y))
            y += 22
        return y + 8

    def draw_unit_info(self, surface: pygame.Surface, unit) -> int:
        y = self._draw_section_title(surface, "Selection", 170)
        if unit is None:
            rendered = self.font.render("Nothing selected", True, (200, 200, 200))
            surface.blit(rendered, (self.rect.x + 14, y))
            return y + 28
        lines = [
            unit.name,
            f"HP: {unit.hp}/{unit.max_hp}",
            f"ATK/DEF: {unit.attack}/{unit.defense}",
            f"Move: {unit.movement}  Range: {unit.attack_range}",
            f"Vision: {unit.vision_range}",
        ]
        for line in lines:
            rendered = self.font.render(line, True, (230, 230, 230))
            surface.blit(rendered, (self.rect.x + 14, y))
            y += 22
        bar_rect = pygame.Rect(self.rect.x + 14, y + 4, 150, 14)
        pygame.draw.rect(surface, (60, 60, 60), bar_rect)
        fill_width = int(bar_rect.width * (unit.hp / unit.max_hp))
        pygame.draw.rect(surface, (70, 200, 80), (bar_rect.x, bar_rect.y, fill_width, bar_rect.height))
        pygame.draw.rect(surface, (255, 255, 255), bar_rect, 1)
        return y + 28

    def draw_action_buttons(self, surface: pygame.Surface) -> None:
        self.end_turn_button.draw(surface, self.font)

    def draw_tooltip(self, surface: pygame.Surface, text: str, pos: tuple[int, int]) -> None:
        lines = text.splitlines() or [text]
        rendered = [self.small_font.render(line, True, (255, 255, 255)) for line in lines]
        width = max(item.get_width() for item in rendered) + 12
        height = sum(item.get_height() for item in rendered) + 10
        tooltip_rect = pygame.Rect(pos[0] + 14, pos[1] + 14, width, height)
        pygame.draw.rect(surface, (18, 18, 24), tooltip_rect, border_radius=6)
        pygame.draw.rect(surface, (230, 230, 230), tooltip_rect, 1, border_radius=6)
        y = tooltip_rect.y + 5
        for item in rendered:
            surface.blit(item, (tooltip_rect.x + 6, y))
            y += item.get_height()
