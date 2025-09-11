Event managers
==============

A class responsible for grouping of events, and for ending the screens displayed by the application.

An event manager is started by an :doc:`eventful screen <eventful_screen>` when the screen is displayed, and is stopped when the screen exits. Callbacks can be registered to be called when an event happens, which is used by :doc:`experiment runner <experiment_runner>` to go to the next screen.

An instance of an event manager can also be cloned, which allows it to be used as a prototype by :doc:`screen sequencers <screen_sequencers>`.


Interface
----------

.. autoclass:: src.data_acquisition.event_manager.EventManager
   :members:
   :undoc-members:
   :show-inheritance:


How to subclass
---------------

.. note::
    
    If you want to create an event manager that is based on events, you should subclass :doc:`SimpleEventManager <event_managers/simple_event_managers>`. Subclass this class only if you want to implement some custom event logic or create a composite event manager.

Subclasses should implement the following methods:

- ``clone()`` - should return a new instance of the subclass, with the same parameters as the original.
- ``_start()``
- ``_stop()``

Available properties and methods:

- ``_trigger_callbacks(result: T)`` - should be used to trigger the screen-end callback, usually as a callback to subscribed events.
- ``_clone_registered_callbacks_from(event_manager: EventManager)`` - can be used to clone the registered callbacks from another event manager.


Catalog
-------

.. toctree::
   :maxdepth: 2
   :titlesonly:

   event_managers/composite_event_managers
   event_managers/simple_event_managers
