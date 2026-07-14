# ── Display ───────────────────────────────────────────────────────────────────
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 600
FPS = 60
TITLE = "Platformer Adventure"

# ── Colours ───────────────────────────────────────────────────────────────────
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (220, 50, 50)
DARK_RED = (160, 0, 0)
GREEN = (60, 180, 60)
DARK_GREEN = (0, 120, 0)
BLUE = (50, 100, 220)
LIGHT_BLUE = (100, 160, 255)
YELLOW = (255, 220, 0)
ORANGE = (255, 140, 0)
PURPLE = (160, 40, 200)
GRAY = (128, 128, 128)
DARK_GRAY = (60, 60, 60)
LIGHT_GRAY = (200, 200, 200)
BROWN = (140, 90, 50)
DARK_BROWN = (80, 50, 20)
CYAN = (0, 200, 220)
GOLD = (255, 215, 0)
SKIN = (230, 190, 140)
SKY_TOP = (15, 20, 50)
SKY_MID = (35, 60, 110)
SKY_BOTTOM = (65, 110, 170)

# ── Physics ───────────────────────────────────────────────────────────────────
GRAVITY = 0.65
JUMP_POWER = -14.0
PLAYER_SPEED = 4.5
MAX_FALL_SPEED = 16.0

# ── Tiles ─────────────────────────────────────────────────────────────────────
TILE_SIZE = 32
TILE_EMPTY = 0
TILE_GROUND = 1
TILE_PLATFORM = 2
TILE_WALL = 3

# ── Map (in tiles) ────────────────────────────────────────────────────────────
BASE_MAP_WIDTH = 80
MAP_HEIGHT = 19

# ── Player ────────────────────────────────────────────────────────────────────
PLAYER_MAX_HEALTH = 100
PLAYER_WIDTH = 22
PLAYER_HEIGHT = 34
PLAYER_START_LIVES = 3
PLAYER_INVINCIBLE_FRAMES = 60  # 1 second after being hit

# ── Enemy ─────────────────────────────────────────────────────────────────────
ENEMY_WIDTH = 22
ENEMY_HEIGHT = 30
ENEMY_BASE_HEALTH = 40
ENEMY_SPEED = 1.5
ENEMY_PATROL_RANGE = 100
ENEMY_SIGHT_RANGE = 220
ENEMY_ATTACK_RANGE = 38
ENEMY_ATTACK_DAMAGE = 8
ENEMY_ATTACK_COOLDOWN = 80  # frames

# Enemy AI state labels
AI_PATROL = "patrol"
AI_CHASE = "chase"
AI_ATTACK = "attack"

# ── Weapons ───────────────────────────────────────────────────────────────────
WEAPONS = {
    "fists": {
        "name": "Fists",
        "damage": 5,
        "attack_range": 35,
        "cooldown": 20,
        "color": (200, 170, 120),
        "type": "melee",
        "proj_speed": 0,
        "proj_size": 0,
    },
    "dagger": {
        "name": "Dagger",
        "damage": 15,
        "attack_range": 42,
        "cooldown": 15,
        "color": CYAN,
        "type": "melee",
        "proj_speed": 0,
        "proj_size": 0,
    },
    "sword": {
        "name": "Sword",
        "damage": 28,
        "attack_range": 58,
        "cooldown": 30,
        "color": LIGHT_GRAY,
        "type": "melee",
        "proj_speed": 0,
        "proj_size": 0,
    },
    "bow": {
        "name": "Bow",
        "damage": 22,
        "attack_range": 500,
        "cooldown": 45,
        "color": BROWN,
        "type": "ranged",
        "proj_speed": 11,
        "proj_size": 6,
    },
    "fireball_staff": {
        "name": "Fireball Staff",
        "damage": 45,
        "attack_range": 420,
        "cooldown": 65,
        "color": ORANGE,
        "type": "magic",
        "proj_speed": 8,
        "proj_size": 10,
    },
}

# ── Scoring ───────────────────────────────────────────────────────────────────
SCORE_KILL_ENEMY = 100
SCORE_COMPLETE_LEVEL = 500

# ── Persistence ───────────────────────────────────────────────────────────────
SAVE_DIR = "saves"
SAVE_FILE = "saves/game_save.json"

# ── Game states ───────────────────────────────────────────────────────────────
STATE_MAIN_MENU = "main_menu"
STATE_PLAYING = "playing"
STATE_PAUSED = "paused"
STATE_GAME_OVER = "game_over"
STATE_LEVEL_COMPLETE = "level_complete"
