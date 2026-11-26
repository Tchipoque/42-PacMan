import json
import sys
from pathlib import Path
from typing import Any


DEFAULT_CONFIG: dict[str, Any] = {
    "maze_size": [15, 15],
    "perfect": False,
    "entry_cell": [0, 0],
    "exit_cell": [14, 14],
    "seed": 42,
    "level_time": 120,
    "max_levels": 10
}


def remove_json_comments(content: str) -> str:
    """remove lines that begins with # from JSON content"""

    lines = content.splitlines()
    clean_lines = [
        line for line in lines
        if not line.lstrip().startswith("#")
    ]
    return "\n".join(clean_lines)


def load_config(config_path: str) -> dict[str, Any]:
    """load game config and apply default value"""

    path = Path(config_path)

    if not path.is_file():
        raise FileNotFoundError(
            f"Configuration file not found: {config_path}"
        )

    with path.open("r", encoding="utf-8") as config_file:
        content = config_file.read()

    config = json.loads(remove_json_comments(content))

    if not isinstance(config, dict):
        raise ValueError("The configuration must be a JSON object")

    settings = DEFAULT_CONFIG.copy()

    for key in DEFAULT_CONFIG:
        if key not in config:
            print(f"Missing '{key}'. Using default: {DEFAULT_CONFIG}")
        else:
            settings[key] = config[key]
        if (
            not isinstance(settings["max_levels"], int)
            or isinstance(settings["max_levels"], bool)
            or settings["max_levels"] < 1
        ):
            print("'max_levels' must be a positive integer. Using default: 10")
            settings["max_levels"] = DEFAULT_CONFIG["max_levels"]

    if (
        not isinstance(settings["maze_size"], list)
        or len(settings["maze_size"]) != 2
        or settings["maze_size"] != [15, 15]
    ):
        print("'maze_size' must be [15, 15]. Using default: [15, 15]")
        settings["maze_size"] = [15, 15]

    if settings["perfect"] is not False:
        print("'perfect' must be false. Using default: False")
        settings["perfect"] = False

    if (
        not isinstance(settings["level_time"], int)
        or isinstance(settings["level_time"], bool)
        or settings["level_time"] <= 0
    ):
        print("'level_time' must be a possitive integer. Using default: 120")
        settings["level_time"] = DEFAULT_CONFIG["level_time"]

    if (
        not isinstance(settings["seed"], int)
        or isinstance(settings["seed"], bool)
    ):
        print("'seed' must be an integer. Using default: 42")
        settings["seed"] = DEFAULT_CONFIG["seed"]

    for key in ("entry_cell", "exit_cell"):
        cell = settings[key]

        if (
            not isinstance(cell, list)
            or len(cell) != 2
            or any(
                not isinstance(value, int) or isinstance(value, bool)
                for value in cell
            )
            or not all(0 <= value < 15 for value in cell)
        ):
            print(
                f"'{key}' is invalid. " f"Using default: {DEFAULT_CONFIG[key]}"
            )
            settings[key] = DEFAULT_CONFIG[key].copy()

    return settings


def main() -> None:
    """start game using config file"""
    if len(sys.argv) != 2:
        print("Usage: python3 pac-man.py config.json")
        sys.exit(1)

    try:
        config = load_config(sys.argv[1])
    except (OSError, json.JSONDecodeError, ValueError) as error:
        print(f"Configuration error: {error}")
        sys.exit(1)

    try:  # connect settings to gamecontroler
        from src.run import GameController

        print("Configuration loaded successfully")
        print(f"Maze size: {config['maze_size']}")

        game = GameController(config)
        game.loadTitleScreen()

        while True:
            game.update()

    except Exception as error:
        print(f"Game error: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
