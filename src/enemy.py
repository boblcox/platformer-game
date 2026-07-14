"""Enemy AI with patrol, chase, and attack states."""

from __future__ import annotations

import math
from typing import List

import pygame

from src.settings import (
    TILE_SIZE, TILE_GROUND, TILE_PLATFORM, TILE_WALL,
    GRAVITY, MAX_FALL_SPEED,
    ENEMY_WIDTH, ENEMY_HEIGHT, ENEMY_BASE_HEALTH,
    ENEMY_SPEED, ENEMY_PATROL_RANGE, ENEMY_SIGHT_RANGE,
    ENEMY_ATTACK_RANGE, ENEMY_ATTACK_DAMAGE, ENEMY_ATTACK_COOLDOWN,
    AI_PATROL, AI_CHASE, AI_ATTACK,
    SCORE_KILL_ENEMY,
    RED, DARK_RED, WHITE, BLACK, GREEN, ORANGE,
)


def _get_solid_tiles(tiles: list, rect: pygame.Rect) -> List[pygame.Rect]:
    h = len(tiles)
    w = len(tiles[0]) if h else 0
    lc = max(0, rect.left // TILE_SIZE)
    rc = min(w - 1, rect.right // TILE_SIZE)
    tr = max(0, rect.top // TILE_SIZE)
    br = min(h - 1, rect.bottom // TILE_SIZE)
    solid = []
    for row in range(tr, br + 1):
        for col in range(lc, rc + 1):
            if tiles[row][col] in (TILE_GROUND, TILE_PLATFORM, TILE_WALL):
                solid.append(pygame.Rect(col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE))
    return solid


class Enemy:
    """A simple melee enemy."""

    def __init__(self, x: int, y: int, level: int = 1) -> None:
        self.rect = pygame.Rect(x, y, ENEMY_WIDTH, ENEMY_HEIGHT)
        self.vel_x = ENEMY_SPEED
        self.vel_y = 0.0
        self.on_ground = False
        self.facing = 1

        # Scale stats with level
        self.max_health = ENEMY_BASE_HEALTH + (level - 1) * 15
        self.health = self.max_health
        self.speed = ENEMY_SPEED + (level - 1) * 0.2
        self.attack_damage = ENEMY_ATTACK_DAMAGE + (level - 1) * 3

        self.ai_state = AI_PATROL
        self.patrol_start_x = float(x)
        self.attack_cooldown = 0
        self.alive = True
        self.hit_flash = 0   # frames to flash white after being hit

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def update(self, tiles: list, player, projectiles_group: pygame.sprite.Group) -> int:
        """Update enemy state. Returns score points earned this frame."""
        if not self.alive:
            return 0

        self._update_ai(player)
        self._apply_physics(tiles)
        self._try_attack(player)

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        if self.hit_flash > 0:
            self.hit_flash -= 1

        # Check damage from player projectiles
        points = 0
        for proj in list(projectiles_group):
            if proj.owner == "player" and self.rect.colliderect(proj.rect):
                points += self.take_damage(proj.damage)
                proj.kill()
        return points

    # ------------------------------------------------------------------
    # AI state machine
    # ------------------------------------------------------------------

    def _update_ai(self, player) -> None:
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)

        if dist <= ENEMY_ATTACK_RANGE:
            self.ai_state = AI_ATTACK
        elif dist <= ENEMY_SIGHT_RANGE:
            self.ai_state = AI_CHASE
        else:
            self.ai_state = AI_PATROL

        if self.ai_state == AI_PATROL:
            self._do_patrol()
        elif self.ai_state == AI_CHASE:
            self._do_chase(dx)
        else:
            self.vel_x = 0.0

    def _do_patrol(self) -> None:
        """Walk back and forth within patrol range."""
        if abs(self.rect.x - self.patrol_start_x) > ENEMY_PATROL_RANGE:
            self.vel_x = -self.vel_x
        if self.vel_x > 0:
            self.facing = 1
        elif self.vel_x < 0:
            self.facing = -1
        if self.vel_x == 0:
            self.vel_x = self.speed

    def _do_chase(self, dx: float) -> None:
        """Move toward the player."""
        if dx > 0:
            self.vel_x = self.speed
            self.facing = 1
        else:
            self.vel_x = -self.speed
            self.facing = -1

    def _try_attack(self, player) -> None:
        """Melee attack the player when in range and cooldown is ready."""
        if self.ai_state != AI_ATTACK:
            return
        if self.attack_cooldown > 0:
            return
        dist = math.hypot(
            player.rect.centerx - self.rect.centerx,
            player.rect.centery - self.rect.centery,
        )
        if dist <= ENEMY_ATTACK_RANGE + 10:
            player.take_damage(self.attack_damage, source_x=self.rect.centerx)
            self.attack_cooldown = ENEMY_ATTACK_COOLDOWN

    # ------------------------------------------------------------------
    # Physics (same tile-based approach as player)
    # ------------------------------------------------------------------

    def _apply_physics(self, tiles: list) -> None:
        self.vel_y += GRAVITY
        if self.vel_y > MAX_FALL_SPEED:
            self.vel_y = MAX_FALL_SPEED

        # X
        self.rect.x += int(self.vel_x)
        for tr in _get_solid_tiles(tiles, self.rect):
            if self.rect.colliderect(tr):
                if self.vel_x > 0:
                    self.rect.right = tr.left
                elif self.vel_x < 0:
                    self.rect.left = tr.right
                self.vel_x = -self.vel_x  # turn around on walls
                self.facing = int(math.copysign(1, self.vel_x))

        # Y
        self.rect.y += int(self.vel_y)
        self.on_ground = False
        for tr in _get_solid_tiles(tiles, self.rect):
            if self.rect.colliderect(tr):
                if self.vel_y > 0:
                    self.rect.bottom = tr.top
                    self.on_ground = True
                elif self.vel_y < 0:
                    self.rect.top = tr.bottom
                self.vel_y = 0

        # Turn around at edges (don't walk off platforms)
        if self.on_ground and self.ai_state == AI_PATROL:
            probe_x = (
                self.rect.right + 2 if self.vel_x > 0 else self.rect.left - 2
            )
            probe_y = self.rect.bottom + 4
            probe_col = probe_x // TILE_SIZE
            probe_row = probe_y // TILE_SIZE
            h = len(tiles)
            w = len(tiles[0]) if h else 0
            if 0 <= probe_row < h and 0 <= probe_col < w:
                if tiles[probe_row][probe_col] not in (TILE_GROUND, TILE_PLATFORM):
                    self.vel_x = -self.vel_x
                    self.facing = int(math.copysign(1, self.vel_x))

    # ------------------------------------------------------------------
    # Damage / death
    # ------------------------------------------------------------------

    def take_damage(self, amount: int) -> int:
        """Apply *amount* damage. Returns score if enemy dies, else 0."""
        self.health -= amount
        self.hit_flash = 8
        if self.health <= 0:
            self.alive = False
            return SCORE_KILL_ENEMY
        return 0

    # ------------------------------------------------------------------
    # Draw
    # ------------------------------------------------------------------

    def draw(self, surface: pygame.Surface, camera) -> None:
        if not self.alive:
            return
        sr = camera.apply(self.rect)
        body_color = WHITE if self.hit_flash > 0 else RED
        pygame.draw.rect(surface, body_color, sr, border_radius=3)
        pygame.draw.rect(surface, DARK_RED, sr, 2, border_radius=3)

        # Eyes
        eye_y = sr.top + 8
        eye_off = 4 if self.facing == 1 else -4
        pygame.draw.circle(surface, BLACK, (sr.centerx + eye_off, eye_y), 2)
        # Menacing dot brows
        pygame.draw.circle(surface, BLACK, (sr.centerx + eye_off, eye_y - 4), 1)

        # Attack indicator
        if self.ai_state == AI_ATTACK and self.attack_cooldown == 0:
            pygame.draw.circle(surface, ORANGE, (sr.centerx, sr.top - 6), 5)

        # Health bar
        bar_w = sr.width
        bar_h = 4
        bx, by = sr.left, sr.top - 8
        pygame.draw.rect(surface, DARK_RED, (bx, by, bar_w, bar_h))
        fill = int(bar_w * (self.health / self.max_health))
        if fill > 0:
            pygame.draw.rect(surface, GREEN, (bx, by, fill, bar_h))
