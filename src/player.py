"""Player character with physics, keyboard/mouse input, and combat."""

from __future__ import annotations

import math
from typing import List, Optional

import pygame

from src.settings import (
    TILE_SIZE, TILE_GROUND, TILE_PLATFORM, TILE_WALL,
    GRAVITY, JUMP_POWER, PLAYER_SPEED, MAX_FALL_SPEED,
    PLAYER_MAX_HEALTH, PLAYER_WIDTH, PLAYER_HEIGHT, PLAYER_INVINCIBLE_FRAMES,
    WEAPONS,
    BLUE, LIGHT_BLUE, SKIN, WHITE, BLACK, RED, DARK_RED, GREEN, GOLD, YELLOW,
)
from src.sprites import Projectile


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Player
# ---------------------------------------------------------------------------

class Player:
    """The player character."""

    KNOCKBACK = 6   # pixels of horizontal knockback when hit

    def __init__(self, x: int, y: int) -> None:
        self.rect = pygame.Rect(x, y, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.on_ground = False
        self.facing = 1          # 1 = right, -1 = left
        self.health = PLAYER_MAX_HEALTH
        self.weapon = "fists"    # current weapon key
        self.attack_cooldown = 0
        self.invincible_timer = 0
        self.reached_ladder = False
        self._jump_pressed = False
        self._attack_queued = False
        self.score_gained = 0    # accumulates kill points between game frames

    # ------------------------------------------------------------------
    # Event handler (called once per pygame event)
    # ------------------------------------------------------------------

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_w, pygame.K_UP, pygame.K_SPACE):
                self._jump_pressed = True
            if event.key in (pygame.K_z, pygame.K_x):
                self._attack_queued = True
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._attack_queued = True

    # ------------------------------------------------------------------
    # Update (called every frame)
    # ------------------------------------------------------------------

    def update(
        self,
        tiles: list,
        enemies: list,
        weapons_group: pygame.sprite.Group,
        ladder,
        projectiles_group: pygame.sprite.Group,
        camera,
    ) -> None:
        self.score_gained = 0
        self._handle_movement(tiles)
        self._handle_attack(enemies, projectiles_group, camera)
        self._check_weapon_pickups(weapons_group)
        self._check_ladder(ladder)

        if self.invincible_timer > 0:
            self.invincible_timer -= 1

    # ------------------------------------------------------------------
    # Movement
    # ------------------------------------------------------------------

    def _handle_movement(self, tiles: list) -> None:
        keys = pygame.key.get_pressed()

        # Horizontal
        self.vel_x = 0.0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vel_x = -PLAYER_SPEED
            self.facing = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vel_x = PLAYER_SPEED
            self.facing = 1

        # Jump
        if self._jump_pressed and self.on_ground:
            self.vel_y = JUMP_POWER
        self._jump_pressed = False

        # Gravity
        self.vel_y += GRAVITY
        if self.vel_y > MAX_FALL_SPEED:
            self.vel_y = MAX_FALL_SPEED

        # Move X then collide
        self.rect.x += int(self.vel_x)
        for tr in _get_solid_tiles(tiles, self.rect):
            if self.rect.colliderect(tr):
                if self.vel_x > 0:
                    self.rect.right = tr.left
                elif self.vel_x < 0:
                    self.rect.left = tr.right
                self.vel_x = 0

        # Move Y then collide
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

    # ------------------------------------------------------------------
    # Combat
    # ------------------------------------------------------------------

    def _handle_attack(
        self,
        enemies: list,
        projectiles_group: pygame.sprite.Group,
        camera,
    ) -> None:
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        if not self._attack_queued:
            return
        self._attack_queued = False

        if self.attack_cooldown > 0:
            return

        info = WEAPONS[self.weapon]
        self.attack_cooldown = info["cooldown"]

        # Determine aim direction toward mouse cursor
        mx, my = pygame.mouse.get_pos()
        world_mx = mx + camera.offset_x
        world_my = my + camera.offset_y
        dx = world_mx - self.rect.centerx
        dy = world_my - self.rect.centery
        dist = max(1.0, math.hypot(dx, dy))
        nx, ny = dx / dist, dy / dist
        # Use facing direction for near-zero horizontal aim
        if abs(dx) < 10:
            nx = float(self.facing)
            ny = 0.0

        if info["type"] == "melee":
            self._melee_attack(enemies, nx, ny, info["attack_range"], info["damage"])
        else:
            self._ranged_attack(
                projectiles_group,
                nx, ny,
                info["proj_speed"],
                info["proj_size"],
                info["damage"],
                info["color"],
            )

    def _melee_attack(
        self,
        enemies: list,
        nx: float,
        ny: float,
        attack_range: int,
        damage: int,
    ) -> None:
        """Check all enemies within arc in front of the player."""
        hitbox = pygame.Rect(
            self.rect.centerx + nx * 10 - attack_range // 2,
            self.rect.centery + ny * 10 - attack_range // 2,
            attack_range,
            attack_range,
        )
        for enemy in enemies:
            if hitbox.colliderect(enemy.rect):
                self.score_gained += enemy.take_damage(damage)

    def _ranged_attack(
        self,
        projectiles_group: pygame.sprite.Group,
        nx: float,
        ny: float,
        speed: float,
        size: int,
        damage: int,
        color: tuple,
    ) -> None:
        proj = Projectile(
            self.rect.centerx,
            self.rect.centery,
            nx * speed,
            ny * speed,
            damage,
            size,
            color,
            owner="player",
        )
        projectiles_group.add(proj)

    # ------------------------------------------------------------------
    # Pickups & triggers
    # ------------------------------------------------------------------

    def _check_weapon_pickups(self, weapons_group: pygame.sprite.Group) -> None:
        for pickup in weapons_group:
            if self.rect.colliderect(pickup.rect):
                self.weapon = pickup.weapon_key
                pickup.kill()

    def _check_ladder(self, ladder) -> None:
        if ladder and self.rect.colliderect(ladder.rect):
            self.reached_ladder = True

    # ------------------------------------------------------------------
    # Taking damage
    # ------------------------------------------------------------------

    def take_damage(self, amount: int, source_x: Optional[float] = None) -> None:
        if self.invincible_timer > 0:
            return
        self.health -= amount
        self.invincible_timer = PLAYER_INVINCIBLE_FRAMES
        if source_x is not None:
            knockback_dir = 1 if self.rect.centerx > source_x else -1
            self.vel_x += knockback_dir * self.KNOCKBACK
            self.vel_y = -4

    def respawn(self, pos: tuple) -> None:
        self.rect.topleft = pos
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.health = PLAYER_MAX_HEALTH
        self.invincible_timer = PLAYER_INVINCIBLE_FRAMES * 2
        self.reached_ladder = False

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------

    def draw(self, surface: pygame.Surface, camera) -> None:
        sr = camera.apply(self.rect)

        # Flicker when invincible
        if self.invincible_timer > 0 and (self.invincible_timer // 5) % 2 == 1:
            return

        # Body
        body_color = BLUE
        pygame.draw.rect(surface, body_color, sr, border_radius=4)
        pygame.draw.rect(surface, LIGHT_BLUE, sr, 2, border_radius=4)

        # Head
        head_rect = pygame.Rect(sr.left + 2, sr.top - 2, sr.width - 4, 14)
        pygame.draw.ellipse(surface, SKIN, head_rect)

        # Eyes
        eye_y = head_rect.centery - 1
        eye_off = 4 if self.facing == 1 else -4
        pygame.draw.circle(surface, BLACK, (sr.centerx + eye_off, eye_y), 2)

        # Weapon indicator
        info = WEAPONS[self.weapon]
        tip_x = sr.right + 4 if self.facing == 1 else sr.left - 4
        tip_y = sr.centery
        pygame.draw.circle(surface, info["color"], (tip_x, tip_y), 5)

        # Health bar (small, above sprite)
        self._draw_health_bar(surface, sr)

    def _draw_health_bar(self, surface: pygame.Surface, sr: pygame.Rect) -> None:
        bar_w = sr.width
        bar_h = 4
        bx = sr.left
        by = sr.top - 8
        # Background
        pygame.draw.rect(surface, DARK_RED, (bx, by, bar_w, bar_h))
        # Fill
        fill_w = int(bar_w * (self.health / PLAYER_MAX_HEALTH))
        if fill_w > 0:
            pygame.draw.rect(surface, GREEN, (bx, by, fill_w, bar_h))
