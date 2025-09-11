import random
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, kw_only=True)
class Sentences:
    polish: list[str]
    english: list[str]


def load_sentences() -> Sentences:
    assets_dir = Path(__file__).parent / "assets"

    with open(assets_dir / "pl.txt", "r", encoding="utf-8") as file:
        polish_sentences = file.read().splitlines()
    random.shuffle(polish_sentences)

    with open(assets_dir / "en.txt", "r", encoding="utf-8") as file:
        english_sentences = file.read().splitlines()
    random.shuffle(english_sentences)

    return Sentences(
        polish=polish_sentences,
        english=english_sentences,
    )
