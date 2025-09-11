Simple screen sequencers
========================

Screen sequencers that are not composite.

Abstract base class:

.. autoclass:: src.data_acquisition.sequencers.SimpleScreenSequencer
   :show-inheritance:


How to subclass
---------------

Subclasses should implement the following methods:

- ``_get_next() -> EventfulScreen[T]``

Available properties and methods:

- ``_previous_result: T``: the result of the previous screen.
- ``_screen_show_callback: Callable[[str], None]``: the callback to be called when a screen is shown.


Catalog
-------

.. toctree::
   :maxdepth: 2
   :titlesonly:

   By screen type <simple_screen_sequencers/by_screen_type>
