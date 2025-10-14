# main.py

import tkinter as tk
from pathlib import Path
import logging
from datetime import datetime
import sys

def setup_logging(participant_id: str) -> logging.Logger:
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    logger = logging.getLogger("EEG2Text")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    handler = logging.FileHandler(
        log_dir / f"{participant_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log",
        encoding="utf-8"
    )
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    console = logging.StreamHandler()
    console.setFormatter(formatter)
    logger.addHandler(console)
    return logger

def main():
    debug_mode = '--debug' in sys.argv or '-d' in sys.argv
    use_mock_eeg = '--mock-eeg' in sys.argv
    root = tk.Tk()
    root.withdraw()
    from tkinter import simpledialog
    participant_id = simpledialog.askstring("Participant ID", "Enter Participant ID:")
    if not participant_id:
        print("No participant ID provided. Exiting.")
        return
    logger = setup_logging(participant_id)
    if debug_mode:
        logger.info("="*50)
        logger.info("DEBUG MODE ENABLED")
        logger.info("="*50)
    if use_mock_eeg:
        logger.info("Using MOCK EEG headset")
    logger.info(f"Starting experiment for participant: {participant_id}")
    from experiment import EEG2TextExperiment
    try:
        experiment = EEG2TextExperiment(
            participant_id=participant_id,
            logger=logger,
            debug_mode=debug_mode,
            use_mock_eeg=use_mock_eeg
        )
        experiment.run()
        logger.info("Experiment completed successfully!")
    except KeyboardInterrupt:
        logger.warning("Experiment interrupted by user")
    except Exception as e:
        logger.error(f"Experiment error: {e}", exc_info=True)
        # In a real scenario, you might want to gracefully handle cleanup here
        # but for now, we re-raise to see the full traceback.
        raise
    finally:
        # This block may not be reached if the experiment is force-quit,
        # but it's good practice for graceful exits.
        if 'experiment' in locals() and experiment:
            experiment.cleanup()
        root.destroy()

if __name__ == "__main__":
    main()