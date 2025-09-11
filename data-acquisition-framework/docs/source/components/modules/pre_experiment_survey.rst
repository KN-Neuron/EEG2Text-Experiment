Pre-experiment survey
=====================

A class responsible for running a pre-experiment survey, useful for entering the participant's ID and collecting additional information, such as age or handedness, before the experiment starts.

It reads a configuration YAML file in the following format:

.. code-block:: yaml

   - label: "Shown label 1"
   key: "unique key 1"
   type: "text"
   required: true

   - label: "Shown label 2"
   key: "unique key 2"
   type: "text"

   - label: "Show label 3"
   key: "unique key 3"
   type: "checkbox"

   - label: "Show label 4"
   key: "unique key 4"
   type: "dropdown"
   options:
      - "Option 1"
      - "Option 2"
      - "Option 3"

All fields must have:

- `label`: Text shown to the user.
- `key`: A unique key used to retrieve the value from the returned responses.
- `type`: The type of the field, which determines how it is displayed.

Allowed field types are (with additional configuration options that they can have):

- `text`
   - `required`: If set to True, the field must be filled in before proceeding. Defaults to False.
- `checkbox`
- `dropdown`
   - `options`: A list of options to choose from.

Interface
---------

.. autoclass:: src.data_acquisition.pre_experiment_survey.PreExperimentSurvey
   :members:
   :special-members: __init__
   :undoc-members:
   :show-inheritance:
