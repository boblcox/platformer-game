"""Programmatically generate pixel-art style sprites for the strategy game."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw

SPRITE_SIZE = 64
PLAYER_1 = (50, 100, 200)
PLAYER_2 = (200, 50, 50)
OUTLINE = (20, 20, 20, 255)


def sprite_dir() -> Path:
    return Path(__file__).resolve().parent.parent / "assets" / "sprites"


def new_canvas() -> Image.Image:
    return Image.new("RGBA", (SPRITE_SIZE, SPRITE_SIZE), (0, 0, 0, 0))


def hex_points(inset: int = 4) -> list[tuple[int, int]]:
    left = inset
    right = SPRITE_SIZE - inset
    top = inset + 8
    bottom = SPRITE_SIZE - inset - 8
    mid_y = SPRITE_SIZE // 2
    quarter = SPRITE_SIZE // 4
    return [
        (left + quarter, top),
        (right - quarter, top),
        (right, mid_y),
        (right - quarter, bottom),
        (left + quarter, bottom),
        (left, mid_y),
    ]


def shade(color: tuple[int, int, int], delta: int) -> tuple[int, int, int, int]:
    return tuple(max(0, min(255, c + delta)) for c in color) + (255,)


def draw_hex_tile(base_color: tuple[int, int, int], accents: Iterable[tuple[tuple[int, int], tuple[int, int], tuple[int, int, int]]]) -> Image.Image:
    image = new_canvas()
    draw = ImageDraw.Draw(image)
    points = hex_points()
    draw.polygon(points, fill=shade(base_color, 10), outline=OUTLINE)
    inner = hex_points(10)
    draw.polygon(inner, fill=shade(base_color, -5), outline=shade(base_color, -30))
    for start, end, accent in accents:
        draw.line([start, end], fill=shade(accent, 0), width=3)
    return image


def add_grass_details(image: Image.Image) -> None:
    draw = ImageDraw.Draw(image)
    for x in range(14, 54, 9):
        draw.line([(x, 42), (x - 2, 34)], fill=(120, 210, 95, 255), width=2)
        draw.line([(x, 42), (x + 2, 34)], fill=(90, 170, 70, 255), width=2)


def add_forest_details(image: Image.Image) -> None:
    draw = ImageDraw.Draw(image)
    trees = [(18, 40), (32, 30), (46, 40)]
    for cx, cy in trees:
        draw.rectangle((cx - 2, cy, cx + 2, cy + 10), fill=(90, 60, 30, 255))
        draw.polygon([(cx, cy - 16), (cx - 11, cy + 2), (cx + 11, cy + 2)], fill=(30, 100, 35, 255), outline=(20, 60, 20, 255))
        draw.polygon([(cx, cy - 8), (cx - 9, cy + 8), (cx + 9, cy + 8)], fill=(45, 130, 45, 255), outline=(20, 60, 20, 255))


def add_mountain_details(image: Image.Image) -> None:
    draw = ImageDraw.Draw(image)
    draw.polygon([(12, 48), (26, 20), (40, 48)], fill=(120, 120, 130, 255), outline=(70, 70, 80, 255))
    draw.polygon([(26, 20), (31, 30), (21, 30)], fill=(240, 240, 245, 255))
    draw.polygon([(28, 50), (43, 24), (56, 50)], fill=(150, 145, 140, 255), outline=(80, 75, 70, 255))
    draw.polygon([(43, 24), (47, 32), (39, 32)], fill=(245, 245, 248, 255))


def add_water_details(image: Image.Image) -> None:
    draw = ImageDraw.Draw(image)
    for y in (24, 34, 44):
        draw.arc((10, y - 6, 28, y + 6), 0, 180, fill=(180, 220, 255, 255), width=3)
        draw.arc((26, y - 4, 44, y + 8), 0, 180, fill=(140, 200, 250, 255), width=3)
        draw.arc((40, y - 5, 56, y + 7), 0, 180, fill=(180, 220, 255, 255), width=3)


def add_desert_details(image: Image.Image) -> None:
    draw = ImageDraw.Draw(image)
    draw.arc((10, 28, 34, 46), 180, 360, fill=(225, 205, 120, 255), width=4)
    draw.arc((28, 24, 56, 46), 180, 360, fill=(210, 188, 100, 255), width=4)
    draw.rectangle((40, 20, 42, 38), fill=(40, 130, 70, 255))
    draw.arc((34, 16, 44, 28), 90, 220, fill=(40, 130, 70, 255), width=3)
    draw.arc((38, 14, 48, 26), -40, 90, fill=(40, 130, 70, 255), width=3)


def draw_unit_base(owner_color: tuple[int, int, int]) -> Image.Image:
    image = new_canvas()
    draw = ImageDraw.Draw(image)
    draw.ellipse((8, 44, 56, 60), fill=(0, 0, 0, 70))
    draw.rectangle((20, 18, 44, 48), fill=shade(owner_color, 15), outline=OUTLINE)
    draw.ellipse((18, 6, 46, 30), fill=shade(owner_color, 30), outline=OUTLINE)
    draw.rectangle((18, 28, 24, 50), fill=(90, 70, 55, 255), outline=OUTLINE)
    draw.rectangle((40, 28, 46, 50), fill=(90, 70, 55, 255), outline=OUTLINE)
    return image


def draw_warrior(owner_color: tuple[int, int, int]) -> Image.Image:
    image = draw_unit_base(owner_color)
    draw = ImageDraw.Draw(image)
    draw.polygon([(48, 18), (54, 14), (54, 44), (48, 40)], fill=(180, 180, 190, 255), outline=OUTLINE)
    draw.rectangle((10, 20, 22, 34), fill=(160, 120, 60, 255), outline=OUTLINE)
    draw.ellipse((6, 18, 26, 38), fill=(150, 110, 60, 255), outline=OUTLINE)
    return image


def draw_archer(owner_color: tuple[int, int, int]) -> Image.Image:
    image = draw_unit_base(owner_color)
    draw = ImageDraw.Draw(image)
    draw.arc((42, 14, 58, 46), 250, 110, fill=(120, 80, 40, 255), width=3)
    draw.line([(48, 18), (52, 42)], fill=(210, 210, 200, 255), width=2)
    draw.line([(14, 20), (44, 30)], fill=(160, 120, 60, 255), width=3)
    draw.polygon([(44, 30), (37, 28), (39, 34)], fill=(180, 180, 190, 255), outline=OUTLINE)
    return image


def draw_mage(owner_color: tuple[int, int, int]) -> Image.Image:
    image = new_canvas()
    draw = ImageDraw.Draw(image)
    draw.ellipse((8, 44, 56, 60), fill=(0, 0, 0, 70))
    draw.polygon([(32, 10), (16, 48), (48, 48)], fill=shade(owner_color, 15), outline=OUTLINE)
    draw.ellipse((22, 14, 42, 32), fill=(220, 205, 180, 255), outline=OUTLINE)
    draw.line([(48, 16), (54, 44)], fill=(140, 90, 50, 255), width=4)
    draw.ellipse((48, 8, 58, 18), fill=(120, 220, 255, 255), outline=(50, 170, 210, 255))
    return image


def draw_cavalry(owner_color: tuple[int, int, int]) -> Image.Image:
    image = new_canvas()
    draw = ImageDraw.Draw(image)
    draw.ellipse((6, 46, 58, 60), fill=(0, 0, 0, 70))
    draw.rectangle((14, 28, 48, 42), fill=(110, 75, 45, 255), outline=OUTLINE)
    draw.rectangle((44, 20, 54, 34), fill=(120, 80, 45, 255), outline=OUTLINE)
    draw.polygon([(54, 20), (60, 24), (54, 28)], fill=(120, 80, 45, 255), outline=OUTLINE)
    for x in (18, 30, 42, 50):
        draw.line([(x, 42), (x - 2, 58)], fill=(70, 50, 30, 255), width=3)
    draw.rectangle((18, 16, 32, 28), fill=shade(owner_color, 25), outline=OUTLINE)
    draw.ellipse((18, 8, 34, 22), fill=shade(owner_color, 40), outline=OUTLINE)
    draw.line([(10, 10), (10, 42)], fill=(160, 160, 170, 255), width=3)
    draw.polygon([(10, 10), (24, 14), (10, 18)], fill=shade(owner_color, 35), outline=OUTLINE)
    return image


def draw_catapult(owner_color: tuple[int, int, int]) -> Image.Image:
    image = new_canvas()
    draw = ImageDraw.Draw(image)
    draw.ellipse((6, 50, 58, 60), fill=(0, 0, 0, 70))
    draw.line([(18, 48), (46, 48)], fill=(110, 80, 45, 255), width=5)
    draw.line([(18, 48), (14, 26)], fill=(130, 90, 50, 255), width=4)
    draw.line([(46, 48), (34, 16)], fill=(130, 90, 50, 255), width=4)
    draw.line([(14, 26), (34, 16)], fill=(150, 110, 60, 255), width=3)
    draw.line([(34, 16), (46, 10)], fill=(170, 130, 75, 255), width=3)
    draw.ellipse((44, 6, 54, 16), fill=shade(owner_color, 25), outline=OUTLINE)
    for x in (18, 46):
        draw.ellipse((x - 6, 44, x + 6, 56), fill=(70, 70, 80, 255), outline=OUTLINE)
    return image


def draw_castle(owner_color: tuple[int, int, int]) -> Image.Image:
    image = new_canvas()
    draw = ImageDraw.Draw(image)
    draw.rectangle((12, 28, 52, 54), fill=shade(owner_color, 10), outline=OUTLINE)
    draw.rectangle((18, 14, 28, 32), fill=shade(owner_color, 20), outline=OUTLINE)
    draw.rectangle((36, 14, 46, 32), fill=shade(owner_color, 20), outline=OUTLINE)
    draw.rectangle((28, 8, 36, 32), fill=shade(owner_color, 30), outline=OUTLINE)
    for x in (18, 22, 26, 28, 32, 36, 38, 42, 46):
        draw.rectangle((x, 10 if x in (28, 32, 36) else 16, x + 2, 20 if x in (28, 32, 36) else 24), fill=shade(owner_color, 35), outline=OUTLINE)
    draw.rectangle((28, 38, 36, 54), fill=(90, 55, 40, 255), outline=OUTLINE)
    return image


def draw_village() -> Image.Image:
    image = new_canvas()
    draw = ImageDraw.Draw(image)
    draw.rectangle((16, 28, 48, 52), fill=(205, 180, 130, 255), outline=OUTLINE)
    draw.polygon([(14, 30), (32, 14), (50, 30)], fill=(150, 80, 55, 255), outline=OUTLINE)
    draw.rectangle((28, 40, 36, 52), fill=(90, 60, 35, 255), outline=OUTLINE)
    draw.rectangle((18, 34, 26, 40), fill=(120, 170, 220, 255), outline=OUTLINE)
    draw.rectangle((38, 34, 46, 40), fill=(120, 170, 220, 255), outline=OUTLINE)
    return image


def draw_barracks() -> Image.Image:
    image = new_canvas()
    draw = ImageDraw.Draw(image)
    draw.rectangle((12, 26, 52, 54), fill=(150, 135, 120, 255), outline=OUTLINE)
    draw.polygon([(12, 26), (24, 14), (40, 14), (52, 26)], fill=(100, 90, 80, 255), outline=OUTLINE)
    draw.line([(20, 30), (20, 50)], fill=(80, 80, 85, 255), width=3)
    draw.line([(28, 30), (28, 50)], fill=(80, 80, 85, 255), width=3)
    draw.line([(36, 30), (36, 50)], fill=(80, 80, 85, 255), width=3)
    draw.line([(44, 30), (44, 50)], fill=(80, 80, 85, 255), width=3)
    draw.line([(8, 18), (8, 48)], fill=(110, 110, 115, 255), width=3)
    draw.polygon([(8, 18), (22, 22), (8, 26)], fill=(170, 170, 180, 255), outline=OUTLINE)
    return image


def draw_tower() -> Image.Image:
    image = new_canvas()
    draw = ImageDraw.Draw(image)
    draw.rectangle((22, 14, 42, 54), fill=(140, 145, 155, 255), outline=OUTLINE)
    draw.rectangle((18, 8, 46, 18), fill=(160, 165, 175, 255), outline=OUTLINE)
    for x in range(18, 46, 7):
        draw.rectangle((x, 4, x + 4, 12), fill=(170, 175, 185, 255), outline=OUTLINE)
    draw.rectangle((28, 30, 36, 54), fill=(90, 60, 40, 255), outline=OUTLINE)
    draw.rectangle((26, 20, 38, 28), fill=(120, 180, 220, 255), outline=OUTLINE)
    return image


def draw_selected_overlay() -> Image.Image:
    image = new_canvas()
    draw = ImageDraw.Draw(image)
    draw.polygon(hex_points(3), outline=(255, 225, 40, 255), width=5)
    return image


def draw_range_overlay(color: tuple[int, int, int, int]) -> Image.Image:
    image = new_canvas()
    draw = ImageDraw.Draw(image)
    draw.polygon(hex_points(4), fill=color, outline=(255, 255, 255, 90))
    return image


def save(image: Image.Image, name: str) -> None:
    image.save(sprite_dir() / name, format="PNG")


def generate_all_sprites() -> None:
    out_dir = sprite_dir()
    out_dir.mkdir(parents=True, exist_ok=True)

    grass = draw_hex_tile((100, 180, 80), [])
    add_grass_details(grass)
    save(grass, "grass.png")

    forest = draw_hex_tile((40, 120, 40), [])
    add_forest_details(forest)
    save(forest, "forest.png")

    mountain = draw_hex_tile((140, 120, 100), [])
    add_mountain_details(mountain)
    save(mountain, "mountain.png")

    water = draw_hex_tile((60, 120, 200), [])
    add_water_details(water)
    save(water, "water.png")

    desert = draw_hex_tile((200, 180, 100), [])
    add_desert_details(desert)
    save(desert, "desert.png")

    unit_drawers = {
        "warrior": draw_warrior,
        "archer": draw_archer,
        "mage": draw_mage,
        "cavalry": draw_cavalry,
        "catapult": draw_catapult,
    }
    for prefix, color in (("p1", PLAYER_1), ("p2", PLAYER_2)):
        for unit_name, drawer in unit_drawers.items():
            save(drawer(color), f"{unit_name}_{prefix}.png")
        save(draw_castle(color), f"castle_{prefix}.png")

    save(draw_village(), "village.png")
    save(draw_barracks(), "barracks.png")
    save(draw_tower(), "tower.png")
    save(draw_selected_overlay(), "selected.png")
    save(draw_range_overlay((60, 120, 255, 90)), "move_range.png")
    save(draw_range_overlay((255, 80, 80, 90)), "attack_range.png")


if __name__ == "__main__":
    generate_all_sprites()
    print(f"Sprites generated in {sprite_dir()}")
