import logging
from pathlib import Path
from threading import Thread
from typing import cast

from data_acquisition.eeg_headset import MockEEGHeadset
from data_acquisition.experiment_runner import ExperimentRunner
from data_acquisition.gui import PygameGui
from data_acquisition.gui.display_mode import (FullscreenDisplayMode,
                                               WindowedDisplayMode)
from data_acquisition.pre_experiment_survey import PreExperimentSurvey

from .app_sequencer_builder import AppSequencerBuilder
from .config import Config
from .constants import (BLOCK_COUNT, DEBUG_BLOCK_COUNT,
                        DEBUG_RELAX_SCREEN_TIMEOUT_MILLIS,
                        DEBUG_SENTENCES_IN_BLOCK_COUNT,
                        LOGGING_DATETIME_FORMAT, LOGGING_LEVEL,
                        LOGGING_MESSAGE_FORMAT, RELAX_SCREEN_TIMEOUT_MILLIS,
                        SENTENCES_IN_BLOCK_COUNT, SURVEY_CONFIG_PATH,
                        SURVEY_PARTICIPANT_ID_KEY)
from .reading_time_analyzer import ReadingTimeAnalyzer


def run(
    *,
    brainaccess_cap_name: str,
    do_use_debug_mode: bool = False,
    do_use_mock_headset: bool = False,
) -> None:
    survey = PreExperimentSurvey(config_file_path=SURVEY_CONFIG_PATH)
    responses = survey.start_and_get_responses()
    participant_id = cast(str, responses.get(SURVEY_PARTICIPANT_ID_KEY))

    logger = logging.getLogger()
    logger.setLevel(LOGGING_LEVEL)
    log_dir = Path().cwd() / "logs"
    log_dir.mkdir(exist_ok=True)
    handler = logging.FileHandler(log_dir / f"{participant_id}.log", encoding="utf-8")
    handler.setLevel(LOGGING_LEVEL)
    formatter = logging.Formatter(
        LOGGING_MESSAGE_FORMAT, datefmt=LOGGING_DATETIME_FORMAT
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    if do_use_mock_headset:
        headset = MockEEGHeadset(logger=logger)
    else:
        from data_acquisition.eeg_headset.brainaccess import \
            BrainAccessV3Headset
        from data_acquisition.eeg_headset.brainaccess.devices import \
            BRAINACCESS_MAXI_32_CHANNEL

        headset = BrainAccessV3Headset(
            device_name=brainaccess_cap_name,
            device_channels=BRAINACCESS_MAXI_32_CHANNEL,
            logger=logger,
        )

    display_mode = (
        WindowedDisplayMode(width=800, height=600)
        if do_use_debug_mode
        else FullscreenDisplayMode()
    )
    gui = PygameGui(display_mode=display_mode, window_title="NeuroGuard", logger=logger)

    config = Config(
        block_count=(DEBUG_BLOCK_COUNT if do_use_debug_mode else BLOCK_COUNT),
        sentence_count=(
            DEBUG_SENTENCES_IN_BLOCK_COUNT
            if do_use_debug_mode
            else SENTENCES_IN_BLOCK_COUNT
        ),
        relax_screen_timeout_millis=(
            DEBUG_RELAX_SCREEN_TIMEOUT_MILLIS
            if do_use_debug_mode
            else RELAX_SCREEN_TIMEOUT_MILLIS
        ),
    )

    reading_analyzer = ReadingTimeAnalyzer(log_directory=log_dir, logger=logger)


    app_sequencer_builder = AppSequencerBuilder(
        gui=gui,
        config=config,
        headset=headset,
        participant_id=participant_id,
        logger=logger,
        reading_time_analyzer=reading_analyzer,
    )
    sequencer = app_sequencer_builder.set_up_app_sequencer()

    runner = ExperimentRunner(
        gui=gui, screen_sequencer=sequencer, end_callback=gui.stop, logger=logger
    )

    Thread(target=runner.run).start()
    gui.start()
