# main.py - Entry point for EEG2Text single-word paradigm
#
# Usage:
#   python main.py                          # Domyślne: approach 2, beep paradigm
#   python main.py --approach1              # Approach 1: czytanie w myślach + spacja
#   python main.py --approach2              # Approach 2: beep paradigm (default)
#   python main.py --mock-eeg              # Mock EEG (bez headsetu)
#   python main.py --debug                 # Debug mode (windowed)
#   python main.py --words 50              # 50 unikalnych słów
#   python main.py --repeats 10            # 10 powtórzeń każdego słowa
#   python main.py --beeps 5              # 5 beepów na trial
#   python main.py --beep-interval 2.0    # 2s między beepami
#   python main.py --word-display 1.5     # 1.5s wyświetlanie słowa
#   python main.py --sentences 20         # 20 zdań testowych
#   python main.py --sentence-mode rsvp   # RSVP lub full
#   python main.py --break-every 50       # Przerwa co 50 trialli
#   python main.py --participant P001     # ID uczestnika (pomija prompt)

import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path

from experiment_config import ExperimentConfig


def setup_logging(participant_id: str) -> logging.Logger:
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    logger = logging.getLogger("EEG2Text")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    handler = logging.FileHandler(
        log_dir / f"{participant_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log",
        encoding="utf-8",
    )
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    console = logging.StreamHandler()
    console.setFormatter(formatter)
    logger.addHandler(console)

    return logger


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="EEG2Text Single-Word Paradigm Experiment"
    )

    # Tryb
    parser.add_argument(
        "-d", "--debug", action="store_true", help="Debug mode (windowed)"
    )
    parser.add_argument("--mock-eeg", action="store_true", help="Use mock EEG headset")
    parser.add_argument(
        "--participant", type=str, default=None, help="Participant ID (skips prompt)"
    )

    # Podejście
    approach_group = parser.add_mutually_exclusive_group()
    approach_group.add_argument(
        "--approach1",
        action="store_true",
        help="Approach 1: słowo + czytanie w myślach + spacja",
    )
    approach_group.add_argument(
        "--approach2", action="store_true", help="Approach 2: słowo + beepy (domyślne)"
    )

    # Parametry słów
    parser.add_argument(
        "--words",
        type=int,
        default=None,
        help=f"Liczba unikalnych słów N (default: {ExperimentConfig.n_words})",
    )
    parser.add_argument(
        "--repeats",
        type=int,
        default=None,
        help=f"Powtórzenia K (default: {ExperimentConfig.k_repeats})",
    )

    # Parametry beepów (approach 2)
    parser.add_argument(
        "--beeps",
        type=int,
        default=None,
        help=f"Liczba beepów na trial (default: {ExperimentConfig.n_beeps})",
    )
    parser.add_argument(
        "--beep-interval",
        type=float,
        default=None,
        help=f"Odstęp między beepami w sekundach (default: {ExperimentConfig.beep_interval})",
    )
    parser.add_argument(
        "--beep-freq",
        type=int,
        default=None,
        help=f"Częstotliwość beep w Hz (default: {ExperimentConfig.beep_frequency})",
    )

    # Timingi
    parser.add_argument(
        "--word-display",
        type=float,
        default=None,
        help=f"Czas wyświetlania słowa w sekundach (default: {ExperimentConfig.word_display_time})",
    )
    parser.add_argument(
        "--pre-beep-delay",
        type=float,
        default=None,
        help=f"Pauza przed beepami (default: {ExperimentConfig.pre_beep_delay})",
    )

    # Zdania
    parser.add_argument(
        "--sentences",
        type=int,
        default=None,
        help=f"Liczba zdań testowych M (default: {ExperimentConfig.m_sentences})",
    )
    parser.add_argument(
        "--sentence-mode",
        choices=["rsvp", "full"],
        default=None,
        help=f"Tryb wyświetlania zdań (default: {ExperimentConfig.sentence_display_mode})",
    )
    parser.add_argument(
        "--rsvp-duration",
        type=float,
        default=None,
        help=f"Czas słowa w RSVP w sekundach (default: {ExperimentConfig.rsvp_word_duration})",
    )

    # Przerwy
    parser.add_argument(
        "--break-every",
        type=int,
        default=None,
        help=f"Przerwa co N trialli (default: {ExperimentConfig.break_every_n_trials})",
    )
    parser.add_argument(
        "--break-duration",
        type=int,
        default=None,
        help=f"Czas przerwy w ms (default: {ExperimentConfig.break_duration_ms})",
    )

    # Pliki
    parser.add_argument(
        "--words-file",
        type=str,
        default=None,
        help=f"Plik ze słowami/zdaniami (default: {ExperimentConfig.words_file})",
    )

    return parser.parse_args()


def build_config(args: argparse.Namespace) -> ExperimentConfig:
    """Buduje ExperimentConfig z argumentów CLI."""
    config = ExperimentConfig()

    if args.approach1:
        config.approach = 1
    else:
        config.approach = 2

    if args.words is not None:
        config.n_words = args.words
    if args.repeats is not None:
        config.k_repeats = args.repeats
    if args.beeps is not None:
        config.n_beeps = args.beeps
    if args.beep_interval is not None:
        config.beep_interval = args.beep_interval
    if args.beep_freq is not None:
        config.beep_frequency = args.beep_freq
    if args.word_display is not None:
        config.word_display_time = args.word_display
        config.word_display_time_approach1 = args.word_display
    if args.pre_beep_delay is not None:
        config.pre_beep_delay = args.pre_beep_delay
    if args.sentences is not None:
        config.m_sentences = args.sentences
    if args.sentence_mode is not None:
        config.sentence_display_mode = args.sentence_mode
    if args.rsvp_duration is not None:
        config.rsvp_word_duration = args.rsvp_duration
    if args.break_every is not None:
        config.break_every_n_trials = args.break_every
    if args.break_duration is not None:
        config.break_duration_ms = args.break_duration
    if args.words_file is not None:
        config.words_file = args.words_file
        config.sentences_file = args.words_file

    return config


def main():
    args = parse_args()
    config = build_config(args)

    # Participant ID
    participant_id = args.participant
    if not participant_id:
        participant_id = input("Enter Participant ID: ").strip()
    if not participant_id:
        print("No participant ID provided. Exiting.")
        return

    logger = setup_logging(participant_id)

    if args.debug:
        logger.info("=" * 50)
        logger.info("DEBUG MODE ENABLED")
        logger.info("=" * 50)

    if args.mock_eeg:
        logger.info("Using MOCK EEG headset")

    logger.info(f"Starting experiment for participant: {participant_id}")

    from experiment import EEG2TextExperiment

    experiment = None
    try:
        experiment = EEG2TextExperiment(
            participant_id=participant_id,
            logger=logger,
            config=config,
            debug_mode=args.debug,
            use_mock_eeg=args.mock_eeg,
        )
        experiment.run()
        logger.info("Experiment completed successfully!")
    except KeyboardInterrupt:
        logger.warning("Experiment interrupted by user")
    except Exception as e:
        logger.error(f"Experiment error: {e}", exc_info=True)
        raise
    finally:
        if experiment:
            experiment.cleanup()


if __name__ == "__main__":
    main()

