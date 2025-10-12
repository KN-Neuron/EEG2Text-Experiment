# main.py
"""
EEG2Text Experiment with BrainAccess
Optimized design based on EEG best practices
"""

import logging
import tkinter as tk
from datetime import datetime
from pathlib import Path

from experiment import EEG2TextExperiment


def setup_logging(participant_id: str) -> logging.Logger:
    """Setup logging configuration"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logger = logging.getLogger("EEG2Text")
    logger.setLevel(logging.INFO)
    
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
    
    # Console handler
    console = logging.StreamHandler()
    console.setFormatter(formatter)
    logger.addHandler(console)
    
    return logger

def main():
    """Main entry point"""
    # Get participant info
    root = tk.Tk()
    root.withdraw()
    
    from tkinter import simpledialog
    participant_id = simpledialog.askstring("Participant ID", "Enter Participant ID:")
    
    if not participant_id:
        print("No participant ID provided. Exiting.")
        return
    
    logger = setup_logging(participant_id)
    logger.info(f"Starting experiment for participant: {participant_id}")
    
    # Initialize and run experiment
    try:
        experiment = EEG2TextExperiment(
            participant_id=participant_id,
            logger=logger,
            debug_mode=False  # Set to True for testing
        )
        experiment.run()
    except Exception as e:
        logger.error(f"Experiment error: {e}", exc_info=True)
        raise
    finally:
        root.destroy()

if __name__ == "__main__":
    main()

