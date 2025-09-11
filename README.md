# Experiment

BrainAccess SDK needs to be installed manually and is not included in Poetry dependencies.

For runtime config, modify constants in _main.py_:

- `DO_USE_DEBUG_MODE` - if True, makes the experiment quicker and uses windowed Pygame
- `DO_USE_MOCK_HEADSET` - if True, doesn't connect to actual BrainAccess headset
- `BRAINACCESS_CAP_NAME` - the name of the BrainAccess cap, can be checked in BrainAccess Board

For advanced config, modify constants in _src/constants.py_.

1. Go to /experiment
2. Create venv
3. After creating and activating venv do:

```
pip install poetry
poetry lock
poetry install
poetry run python main.py
```
