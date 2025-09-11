Simple event managers
=====================

Event managers based on events.

Abstract base class:

.. autoclass:: src.data_acquisition.event_manager.SimpleEventManager
   :show-inheritance:


How to subclass
---------------

Subclasses should implement the following methods:

- ``_setup()`` - should set up the event manager, for example subscribe to any events. This method is called when the event manager is started.
- ``_clone() -> SimpleEventManager[T]`` - should return a new instance of the subclass, with the same parameters as the original.

Available properties and methods:

- ``_trigger_callback(result: T)`` - should be used to trigger the screen-end callback, usually as a callback to subscribed events.


Catalog
-------

.. toctree::
   :maxdepth: 2

   Key-press-based <simple_event_managers/key_based>
   Time-based <simple_event_managers/time_based>
