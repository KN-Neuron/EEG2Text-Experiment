# src/reading_time_analyzer.py

import re
import statistics
from collections import defaultdict
from datetime import datetime
from logging import Logger
from pathlib import Path

DEFAULT_WPM = 225


class ReadingTimeAnalyzer:
    def __init__(self, log_directory: Path, logger: Logger):
        self._logger = logger
        self._log_directory = log_directory
        # A dictionary to store: {"sentence text": [duration1_sec, duration2_sec, ...]}
        self.reading_times: dict[str, list[float]] = defaultdict(list)
        self._parse_all_logs()

    def _parse_all_logs(self):
        """Parses all .log files in the specified directory to populate reading times."""
        self._logger.info(f"Starting to parse log files in: {self._log_directory}")
        if not self._log_directory.exists() or not self._log_directory.is_dir():
            self._logger.warning(
                f"Log directory not found: {self._log_directory}. Cannot calculate reading times."
            )
            return

        for log_file in self._log_directory.glob("*.log"):
            self._parse_file(log_file)

        self._logger.info(
            f"Finished parsing logs. Found reading times for {len(self.reading_times)} unique sentences."
        )

    def _parse_file(self, file_path: Path):
        """
        Parses a single log file to find sentence start/end annotations and calculate duration.
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            sentence_start_info = {}

            # Regex to find sentence log entries and start/end annotations
            sentence_log_pattern = re.compile(
                r"Showing screen with (normal) sentence: (.*)"
            )
            annotation_pattern = re.compile(
                r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) - .* - (SENTENCE_START_normal|SENTENCE_END)"
            )

            for line in lines:
                # Look for when a sentence is shown
                sentence_match = sentence_log_pattern.search(line)
                if sentence_match:
                    category = sentence_match.group(1)
                    text = sentence_match.group(2).strip()
                    if category == "normal":
                        # Store the text, waiting for its START annotation
                        sentence_start_info["last_text"] = text
                    continue

                annotation_match = annotation_pattern.search(line)
                if annotation_match:
                    timestamp_str = annotation_match.group(1)
                    event = annotation_match.group(2)
                    timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")

                    if event == "SENTENCE_START_normal" and "last_text" in sentence_start_info:
                        sentence_start_info["time"] = timestamp
                        sentence_start_info["text"] = sentence_start_info.pop("last_text")

                    elif event == "SENTENCE_END" and "time" in sentence_start_info:
                        duration = (timestamp - sentence_start_info["time"]).total_seconds()
                        sentence_text = sentence_start_info["text"]
                        
                        if 0.5 < duration < 30.0:
                             self.reading_times[sentence_text].append(duration)
                        
                        # Reset for the next sentence
                        sentence_start_info.clear()

        except Exception as e:
            self._logger.error(f"Failed to parse log file {file_path}: {e}")

    def get_avg_reading_time(self, sentence_text: str) -> float | None:
        """
        Returns the average reading time for a given sentence in seconds.
        Returns None if the sentence has no recorded reading times.
        """
        if sentence_text in self.reading_times and self.reading_times[sentence_text]:
            times = self.reading_times[sentence_text]
            return statistics.mean(times)
        return None

    def estimate_reading_time_from_wpm(self, sentence_text: str) -> float:
        """
        Fallback method to estimate reading time based on word count.
        """
        word_count = len(sentence_text.split())
        if word_count == 0:
            return 1.0  
        return (word_count / DEFAULT_WPM) * 60
