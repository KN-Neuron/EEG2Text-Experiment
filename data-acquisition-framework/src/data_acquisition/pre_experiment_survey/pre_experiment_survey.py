import json
from pathlib import Path
from typing import Any, Callable, Optional, cast

import yaml

from .errors import PreExperimentSurveyError
from .survey_gui import SurveyGui


class PreExperimentSurvey:
    def __init__(
        self,
        *,
        config_file_path: Path,
        responses_file_path_factory: Optional[
            Callable[[dict[str, str | bool]], Path]
        ] = None,
    ):
        """
        :param config_file_path: Path to the YAML configuration file defining the survey fields.
        :param responses_file_path_factory: Optional function to return a path to save the survey responses as a JSON file. The function is passed the responses from the survey as a dictionary. If not provided, the responses will not be saved to a file.
        """

        self._config_file_path = config_file_path
        self._responses_file_path_factory = responses_file_path_factory

        self.field_widgets = {}
        self.field_vars = {}

    def start_and_get_responses(self) -> dict[str, str | bool]:
        field_config = self._read_config()

        survey_gui = SurveyGui(field_config=field_config)
        survey_gui.run()

        responses = survey_gui.get_responses()
        if self._responses_file_path_factory is not None:
            responses_file_path = self._responses_file_path_factory(responses)

            with open(responses_file_path, "w", encoding="utf-8") as f:
                json.dump(responses, f, indent=4, ensure_ascii=False)

        return responses

    def _read_config(self) -> list[Any]:
        if not self._config_file_path.exists():
            raise PreExperimentSurveyError(
                f"Configuration file at {self._config_file_path} does not exist."
            )

        with open(self._config_file_path, "r", encoding="utf-8") as f:
            field_config = yaml.safe_load(f)

        if not isinstance(field_config, list):
            raise PreExperimentSurveyError(
                f"Configuration file must contain a list of field configurations."
            )

        return cast(list[Any], field_config)
