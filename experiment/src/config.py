from dataclasses import dataclass

from data_acquisition.gui.event_types import Key

from .constants import (AUDIO_INSTRUCTION_TEXT, BLOCK_COUNT,
                        CONTINUE_SCREEN_ADVANCE_KEY, CONTINUE_SCREEN_TEXT,
                        FIXATION_CROSS_TIMEOUT_RANGE_MILLIS,
                        NORMAL_READING_INSTRUCTION_TEXT,
                        PAUSE_SCREEN_END_ANNOTATION,
                        PAUSE_SCREEN_START_ANNOTATION, PAUSE_SCREEN_TEXT,
                        PAUSE_UNPAUSE_KEY, QUESTION_SCREEN_END_ANNOTATION,
                        QUESTION_SCREEN_START_ANNOTATION,
                        RELAX_SCREEN_END_ANNOTATION,
                        RELAX_SCREEN_START_ANNOTATION,
                        RELAX_SCREEN_TIMEOUT_MILLIS,
                        SENTENCE_SCREEN_ADVANCE_KEY,
                        SENTENCE_SCREEN_END_ANNOTATION,
                        SENTENCE_SCREEN_START_ANNOTATION,
                        SENTENCE_SCREEN_TIMEOUT_MILLIS,
                        SENTENCES_IN_BLOCK_COUNT,
                        SENTIMENT_READING_INSTRUCTION_TEXT,
                        THINKING_SCREEN_END_ANNOTATION,
                        THINKING_SCREEN_START_ANNOTATION,
                        THINKING_SCREEN_TIMEOUT_MILLIS)

fixation_cross_timeout_range_start_millis, fixation_cross_timeout_range_end_millis = (
    FIXATION_CROSS_TIMEOUT_RANGE_MILLIS
)


@dataclass
class Config:
    block_count: int = BLOCK_COUNT
    sentence_count: int = SENTENCES_IN_BLOCK_COUNT

    do_show_continue_screen: bool = True
    continue_screen_text: str = CONTINUE_SCREEN_TEXT
    continue_screen_advance_key: Key = CONTINUE_SCREEN_ADVANCE_KEY

    normal_reading_instruction_text: str = NORMAL_READING_INSTRUCTION_TEXT
    sentiment_reading_instruction_text: str = SENTIMENT_READING_INSTRUCTION_TEXT
    audio_instruction_text: str = AUDIO_INSTRUCTION_TEXT

    sentence_screen_advance_key: Key = SENTENCE_SCREEN_ADVANCE_KEY
    sentence_screen_timeout_millis: int = SENTENCE_SCREEN_TIMEOUT_MILLIS
    sentence_screen_start_annotation = SENTENCE_SCREEN_START_ANNOTATION
    sentence_screen_end_annotation = SENTENCE_SCREEN_END_ANNOTATION

    thinking_screen_timeout_millis: int = THINKING_SCREEN_TIMEOUT_MILLIS
    thinking_screen_start_annotation = THINKING_SCREEN_START_ANNOTATION
    thinking_screen_end_annotation = THINKING_SCREEN_END_ANNOTATION

    question_screen_start_annotation = QUESTION_SCREEN_START_ANNOTATION
    question_screen_end_annotation = QUESTION_SCREEN_END_ANNOTATION

    fixation_cross_timeout_range_start_millis: int = (
        fixation_cross_timeout_range_start_millis
    )
    fixation_cross_timeout_range_end_millis: int = (
        fixation_cross_timeout_range_end_millis
    )

    pause_unpause_key: Key = PAUSE_UNPAUSE_KEY
    pause_screen_text: str = PAUSE_SCREEN_TEXT
    pause_screen_start_annotation: str = PAUSE_SCREEN_START_ANNOTATION
    pause_screen_end_annotation: str = PAUSE_SCREEN_END_ANNOTATION

    relax_screen_timeout_millis: int = RELAX_SCREEN_TIMEOUT_MILLIS
    relax_screen_start_annotation: str = RELAX_SCREEN_START_ANNOTATION
    relax_screen_end_annotation: str = RELAX_SCREEN_END_ANNOTATION

    normal_question_ratio: float = 2.0 / 10.0
    sentiment_question_ratio: float = 2.0 / 10.0
    audio_question_ratio: float = 2.0 / 10.0
