import json
from pathlib import Path
from typing import Any

HIGHSCORE_FILE = Path("highscore.json")


def load_highscores() -> list[dict[str, Any]]:
    """load saved highscores from json file"""

    if not HIGHSCORE_FILE.exists():
        return []

    try:
        with HIGHSCORE_FILE.open("r", encoding="utf-8") as file:
            scores = json.load(file)

        if not isinstance(scores, list):
            print("Invalid highscores file. Starting with an empty list")
            return []

        return scores

    except (OSError, json.JSONDecodeError):
        print("Could not load highscores. Starting with empty list")
        return []


def save_highscores(scores: list[dict[str, Any]]) -> None:
    """save highscores to the json file"""

    try:
        with HIGHSCORE_FILE.open("w", encoding="utf-8") as file:
            json.dump(scores, file, indent=4)
    except OSError:
        print("Could not save highscores")


def sort_highscores(
    scores: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """sort highscores and keep only the top 10"""

    valid_scores = [
        score for score in scores
        if (
            isinstance(score, dict)
            and isinstance(score.get("name"), str)
            and isinstance(score.get("score"), int)
            and not isinstance(score.get("score"), bool)
            and score["score"] >= 0
        )
    ]

    valid_scores.sort(
        key=lambda score: score["score"],
        reverse=True
    )
    return valid_scores[:10]


def add_highscore(name: str, score: int) -> list[dict[str, Any]]:
    """add a new score and update the top 10 highscores"""

    name = name.strip()

    if (
        not name
        or len(name) > 10
        or not all(char.isalnum() or char == " " for char in name)
    ):
        print("Invalid player name")
        return load_highscores()

    if (
        not isinstance(score, int)
        or isinstance(score, bool)
        or score < 0
    ):
        print("Invalid score")
        return load_highscores()

    scores = load_highscores()

    scores.append({
        "name": name,
        "score": score
    })

    scores = sort_highscores(scores)
    save_highscores(scores)

    return scores
