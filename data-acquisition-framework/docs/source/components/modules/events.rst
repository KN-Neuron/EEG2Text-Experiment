Events
======

A class representing events in the application. It can be an event provided by the GUI, or by some external source.


Interface
----------

.. autoclass:: src.data_acquisition.events.Event
   :members:
   :undoc-members:
   :show-inheritance:


How to subclass
---------------

Subclasses should implement the following methods:

- ``clone() -> Event``
- ``_start_listening()``
- ``_stop_listening()``

Available properties and methods:

- ``_trigger_callback()`` - should be used to trigger registered callbacks when the event occurs.


Catalog
-------

.. toctree::
   :maxdepth: 2
   :titlesonly:

   events/gui_events
