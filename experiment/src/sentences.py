import json
import random
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, kw_only=True)
class Sentence:
    text: str
    question: str = None
    options: list[str] = None
    correct_answer_index: int = None
    audio_path: str = None
    category: str = "normal"


@dataclass(frozen=True, kw_only=True)
class SentenceSet:
    normal: list[Sentence]
    sentiment: list[Sentence]
    audio: list[Sentence]
    test_normal: list[Sentence]
    test_sentiment: list[Sentence]
    test_audio: list[Sentence]


def load_sentences() -> SentenceSet:
    assets_dir = Path(__file__).parent / "assets"

    with open(assets_dir / "normal_sentences.json", "r", encoding="utf-8") as file:
        normal_sentences_data = json.load(file)

    with open(assets_dir / "sentiment_sentences.json", "r", encoding="utf-8") as file:
        sentiment_sentences_data = json.load(file)


    normal_sentences = [
        Sentence(
            text=item["text"],
            question=item.get("question"),
            options=item.get("options"),
            correct_answer_index=item.get("correct_answer_index"),
            category="normal",
        )
        for item in normal_sentences_data
    ]

    sentiment_sentences = [
        Sentence(
            text=item["text"],
            question=item.get("question"),
            options=item.get("options"),
            correct_answer_index=item.get("correct_answer_index"),
            category="sentiment",
        )
        for item in sentiment_sentences_data
    ]

    audio_sentences = [
        Sentence(
            text=item["text"],
            audio_path=item.get("audio_path"),
            question=item.get("question"),
            options=item.get("options"),
            correct_answer_index=item.get("correct_answer_index"),
            category="audio",
        )
        for item in normal_sentences_data
    ]

    test_normal = normal_sentences[:10]
    test_sentiment = sentiment_sentences[:10]
    test_audio = audio_sentences[:10]

    normal_sentences = normal_sentences[10:]
    sentiment_sentences = sentiment_sentences[10:]
    audio_sentences = audio_sentences[10:]

    random.shuffle(normal_sentences)
    random.shuffle(sentiment_sentences)
    random.shuffle(audio_sentences)

    return SentenceSet(
        normal=normal_sentences,
        sentiment=sentiment_sentences,
        audio=audio_sentences,
        test_normal=test_normal,
        test_sentiment=test_sentiment,
        test_audio=test_audio,
    )
