Changelog
=========

The latest version is available at the `main` branch of the `GitLab repository <https://gitlab.com/kn-neuron/neuroguard/data-acquisition-framework>`_.

Previous versions are available in the `tags section <https://gitlab.com/kn-neuron/neuroguard/data-acquisition-framework/tags>`_ of the repository.

v0.5.0
------
- hanged name from `BrainAccessV1Headset` to `BrainAccessV2EEGHeadset` to reflect the BrainAccess SDK version.
- Added a workaround for a BrainAccess SDK v3.5.0 bug that didn't allow to connect to the headset a second time.
- Added `disconnect` method to `EEGHeadset` interface.

v0.4.0
------
- Implemented logging.
- Small documentation fixes.

v0.3.0
------
- Implemented pre-experiment survey.
- Added `reset` method to FixationCrossScreenSequencer.
- Added method call order checks to event managers and events.
- Added more info about installing Brainaccess SDK to the documentation.
- Other small fixes.

v0.2.0
------
- Added `Escape` to available keys.
- Redid event subscription mechanism in GUI to use event IDs.

v0.1.0
------
- Initial version.
