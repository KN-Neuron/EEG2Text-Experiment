EEG headset
===========

A class representing a headset device used for EEG data acquisition.


Interface
----------

.. autoclass:: src.data_acquisition.eeg_headset.EEGHeadset
   :special-members: __init__
   :members:
   :undoc-members:
   :show-inheritance:


How to subclass
---------------

Subclasses should implement the following methods:

- ``_start()``
- ``_stop_and_save_at_path(save_path: Path)``
- ``_annotate(annotation: str)``
- optionally ``_disconnect()`` - if the headset requires a specific disconnection procedure. Empty by default.

Catalog
-------

.. toctree::
   :maxdepth: 1
   :titlesonly:

   eeg_headset/brainaccess
   eeg_headset/mock_eeg_headset
