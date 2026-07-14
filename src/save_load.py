"""JSON-based save / load system."""

from __future__ import annotations

import json
import os
from typing import Optional

from src.settings import SAVE_DIR, SAVE_FILE


def save_game(data: dict) -> bool:
    """Write *data* to the save file. Returns True on success."""
    try:
        os.makedirs(SAVE_DIR, exist_ok=True)
        with open(SAVE_FILE, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)
        return True
    except OSError:
        return False


def load_game() -> Optional[dict]:
    """Read and return save data, or None if no valid save exists."""
    if not os.path.isfile(SAVE_FILE):
        return None
    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError):
        return None


def save_exists() -> bool:
    """Return True if a save file is present."""
    return os.path.isfile(SAVE_FILE)
