"""All UI screens and HUD rendering.

Screens:
  * Main menu      – new game / load game / quit
  * Pause menu     – resume / save / main menu
  * Game-over      – retry / main menu
  * Level-complete – next level / main menu
  * HUD            – health bar, weapon, score, level, lives
"""

from __future__ import annotations

from typing import Optional

import pygame

from src.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    PLAYER_MAX_HEALTH,
    WEAPONS,
    BLACK, WHITE, RED, DARK_RED, GREEN, DARK_GREEN,
    BLUE, LIGHT_BLUE, YELLOW, ORANGE, GOLD,
    GRAY, DARK_GRAY, LIGHT_GRAY,
    SKY_MID,
)


# ---------------------------------------------------------------------------
# Tiny helpers
# ---------------------------------------------------------------------------

def _load_font(size: int, bold: bool = False) -> pygame.font.Font:
    try:
        return pygame.font.SysFont("Arial", size, bold=bold)
    except Exception:
        return pygame.font.Font(None, size)


def _draw_text(
    surface: pygame.Surface,
    text: str,
    font: pygame.font.Font,
    color: tuple,
    cx: int,
    cy: int,
    shadow: bool = False,
) -> pygame.Rect:
    if shadow:
        shadow_surf = font.render(text, True, BLACK)
        surface.blit(shadow_surf, (cx - shadow_surf.get_width() // 2 + 2, cy - shadow_surf.get_height() // 2 + 2))
    rendered = font.render(text, True, color)
    rect = rendered.get_rect(center=(cx, cy))
    surface.blit(rendered, rect)
    return rect


# ---------------------------------------------------------------------------
# Button widget
# ---------------------------------------------------------------------------

class Button:
    PAD_X = 30
    PAD_Y = 12
    BORDER = 2
    HOVER_BRIGHTEN = 40

    def __init__(
        self,
        cx: int,
        cy: int,
        text: str,
        font: pygame.font.Font,
        color: tuple = DARK_GRAY,
        text_color: tuple = WHITE,
    ) -> None:
        rendered = font.render(text, True, text_color)
        w = rendered.get_width() + self.PAD_X * 2
        h = rendered.get_height() + self.PAD_Y * 2
        self.rect = pygame.Rect(0, 0, w, h)
        self.rect.center = (cx, cy)
        self.text = text
        self.font = font
        self.color = color
        self.text_color = text_color
        self.hovered = False

    def draw(self, surface: pygame.Surface) -> None:
        bg = self.color
        if self.hovered:
            bg = tuple(min(255, c + self.HOVER_BRIGHTEN) for c in bg)
        pygame.draw.rect(surface, bg, self.rect, border_radius=8)
        pygame.draw.rect(surface, WHITE, self.rect, self.BORDER, border_radius=8)
        _draw_text(
            surface, self.text, self.font, self.text_color,
            self.rect.centerx, self.rect.centery,
        )

    def update(self, mouse_pos: tuple) -> None:
        self.hovered = self.rect.collidepoint(mouse_pos)

    def is_clicked(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(event.pos)
        return False


# ---------------------------------------------------------------------------
# UI manager
# ---------------------------------------------------------------------------

class UI:
    """Manages all overlay screens and HUD."""

    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        self.title_font = _load_font(56, bold=True)
        self.heading_font = _load_font(36, bold=True)
        self.btn_font = _load_font(26)
        self.hud_font = _load_font(20, bold=True)
        self.small_font = _load_font(16)

        # Pre-build button lists for each screen
        cx = SCREEN_WIDTH // 2

        self.main_menu_buttons = [
            Button(cx, 280, "New Game", self.btn_font, color=(40, 80, 160)),
            Button(cx, 340, "Load Game", self.btn_font, color=(40, 100, 60)),
            Button(cx, 400, "Quit", self.btn_font, color=(140, 40, 40)),
        ]
        self.pause_buttons = [
            Button(cx, 280, "Resume", self.btn_font, color=(40, 80, 160)),
            Button(cx, 340, "Save Game", self.btn_font, color=(40, 100, 60)),
            Button(cx, 400, "Main Menu", self.btn_font, color=(100, 60, 140)),
        ]
        self.game_over_buttons = [
            Button(cx, 340, "Try Again", self.btn_font, color=(40, 80, 160)),
            Button(cx, 400, "Main Menu", self.btn_font, color=(100, 60, 140)),
        ]
        self.level_complete_buttons = [
            Button(cx, 360, "Next Level", self.btn_font, color=(40, 80, 160)),
            Button(cx, 420, "Main Menu", self.btn_font, color=(100, 60, 140)),
        ]

        self._bg_surface: Optional[pygame.Surface] = None

    # ------------------------------------------------------------------
    # Background helper
    # ------------------------------------------------------------------

    def _draw_gradient_bg(self) -> None:
        """Draw a dark gradient background for menus."""
        for y in range(SCREEN_HEIGHT):
            t = y / SCREEN_HEIGHT
            r = int(15 * (1 - t) + 40 * t)
            g = int(20 * (1 - t) + 50 * t)
            b = int(50 * (1 - t) + 100 * t)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))

    def _dim_overlay(self, alpha: int = 160) -> None:
        """Dim the current screen for overlay menus."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, alpha))
        self.screen.blit(overlay, (0, 0))

    # ------------------------------------------------------------------
    # Main menu
    # ------------------------------------------------------------------

    def draw_main_menu(self) -> None:
        self._draw_gradient_bg()
        cx = SCREEN_WIDTH // 2
        _draw_text(self.screen, "PLATFORMER ADVENTURE", self.title_font, GOLD, cx, 140, shadow=True)
        _draw_text(self.screen, "Arrow Keys / WASD  ·  Mouse to Aim  ·  Click / Z to Attack",
                   self.small_font, LIGHT_GRAY, cx, 200)

        mouse_pos = pygame.mouse.get_pos()
        for btn in self.main_menu_buttons:
            btn.update(mouse_pos)
            btn.draw(self.screen)

    def main_menu_event(self, event: pygame.event.Event) -> Optional[str]:
        """Return action string or None."""
        labels = ["new_game", "load_game", "quit"]
        for btn, action in zip(self.main_menu_buttons, labels):
            if btn.is_clicked(event):
                return action
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            return "new_game"
        return None

    # ------------------------------------------------------------------
    # Pause menu
    # ------------------------------------------------------------------

    def draw_pause_menu(self) -> None:
        self._dim_overlay(140)
        cx = SCREEN_WIDTH // 2
        _draw_text(self.screen, "PAUSED", self.title_font, WHITE, cx, 200, shadow=True)
        mouse_pos = pygame.mouse.get_pos()
        for btn in self.pause_buttons:
            btn.update(mouse_pos)
            btn.draw(self.screen)

    def pause_menu_event(self, event: pygame.event.Event) -> Optional[str]:
        labels = ["resume", "save", "main_menu"]
        for btn, action in zip(self.pause_buttons, labels):
            if btn.is_clicked(event):
                return action
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return "resume"
        return None

    # ------------------------------------------------------------------
    # Game over
    # ------------------------------------------------------------------

    def draw_game_over(self, score: int) -> None:
        self._draw_gradient_bg()
        cx = SCREEN_WIDTH // 2
        _draw_text(self.screen, "GAME OVER", self.title_font, RED, cx, 200, shadow=True)
        _draw_text(self.screen, f"Score: {score}", self.heading_font, GOLD, cx, 275)
        mouse_pos = pygame.mouse.get_pos()
        for btn in self.game_over_buttons:
            btn.update(mouse_pos)
            btn.draw(self.screen)

    def game_over_event(self, event: pygame.event.Event) -> Optional[str]:
        labels = ["retry", "main_menu"]
        for btn, action in zip(self.game_over_buttons, labels):
            if btn.is_clicked(event):
                return action
        return None

    # ------------------------------------------------------------------
    # Level complete
    # ------------------------------------------------------------------

    def draw_level_complete(self, level: int, score: int) -> None:
        self._dim_overlay(150)
        cx = SCREEN_WIDTH // 2
        _draw_text(self.screen, "LEVEL COMPLETE!", self.title_font, GOLD, cx, 200, shadow=True)
        _draw_text(self.screen, f"Level {level} finished  ·  Score: {score}",
                   self.heading_font, WHITE, cx, 280)
        mouse_pos = pygame.mouse.get_pos()
        for btn in self.level_complete_buttons:
            btn.update(mouse_pos)
            btn.draw(self.screen)

    def level_complete_event(self, event: pygame.event.Event) -> Optional[str]:
        labels = ["next_level", "main_menu"]
        for btn, action in zip(self.level_complete_buttons, labels):
            if btn.is_clicked(event):
                return action
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            return "next_level"
        return None

    # ------------------------------------------------------------------
    # Save notification
    # ------------------------------------------------------------------

    def __init_save_notif(self) -> None:
        self._save_notif_timer = 0

    def show_save_notification(self) -> None:
        self._save_notif_timer = 120  # 2 seconds

    def _draw_save_notif(self) -> None:
        if not hasattr(self, "_save_notif_timer"):
            self._save_notif_timer = 0
        if self._save_notif_timer > 0:
            self._save_notif_timer -= 1
            alpha = min(255, self._save_notif_timer * 4)
            surf = self.small_font.render("Game Saved!", True, GREEN)
            surf.set_alpha(alpha)
            self.screen.blit(surf, (SCREEN_WIDTH - surf.get_width() - 16, 16))

    # ------------------------------------------------------------------
    # HUD
    # ------------------------------------------------------------------

    def draw_hud(self, player, score: int, level: int, lives: int) -> None:
        self._draw_save_notif()

        # ── Health bar ────────────────────────────────────────────────
        bar_x, bar_y, bar_w, bar_h = 16, 16, 200, 20
        pygame.draw.rect(self.screen, DARK_RED, (bar_x, bar_y, bar_w, bar_h), border_radius=4)
        fill = int(bar_w * (player.health / PLAYER_MAX_HEALTH))
        if fill > 0:
            fill_color = GREEN if player.health > 40 else (ORANGE if player.health > 20 else RED)
            pygame.draw.rect(self.screen, fill_color, (bar_x, bar_y, fill, bar_h), border_radius=4)
        pygame.draw.rect(self.screen, WHITE, (bar_x, bar_y, bar_w, bar_h), 2, border_radius=4)
        hp_text = self.hud_font.render(f"HP {player.health}/{PLAYER_MAX_HEALTH}", True, WHITE)
        self.screen.blit(hp_text, (bar_x + 4, bar_y + 2))

        # ── Weapon ────────────────────────────────────────────────────
        info = WEAPONS[player.weapon]
        wcolor = info["color"]
        wx, wy = 16, 46
        pygame.draw.rect(self.screen, DARK_GRAY, (wx - 4, wy - 4, 180, 28), border_radius=4)
        pygame.draw.rect(self.screen, wcolor, (wx - 4, wy - 4, 180, 28), 2, border_radius=4)
        w_text = self.hud_font.render(f"⚔ {info['name']}", True, wcolor)
        self.screen.blit(w_text, (wx, wy))

        # ── Score / Level / Lives ─────────────────────────────────────
        score_text = self.hud_font.render(f"Score: {score}", True, GOLD)
        level_text = self.hud_font.render(f"Level: {level}", True, LIGHT_GRAY)
        lives_text = self.hud_font.render(f"Lives: {lives}", True, LIGHT_BLUE)

        self.screen.blit(score_text, (SCREEN_WIDTH - score_text.get_width() - 16, 16))
        self.screen.blit(level_text, (SCREEN_WIDTH - level_text.get_width() - 16, 40))
        self.screen.blit(lives_text, (SCREEN_WIDTH - lives_text.get_width() - 16, 64))

        # ── Controls hint (small, bottom left) ────────────────────────
        hint = "WASD/Arrows: Move  |  W/Space: Jump  |  Click/Z: Attack  |  Esc: Pause"
        hint_surf = self.small_font.render(hint, True, GRAY)
        self.screen.blit(hint_surf, (8, SCREEN_HEIGHT - hint_surf.get_height() - 6))
