Composite event manager
=======================

General-purpose composite event manager that combines multiple event managers into one, and triggers the callback whenever any of its sub-managers triggers.

.. autoclass:: src.data_acquisition.event_manager.CompositeEventManager
   :show-inheritance:

Usage example
-------------

.. code-block:: python

   event_manager = CompositeEventManager(
       event_managers=[
           FixedTimeoutEventManager(gui=gui, timeout_millis=1000),
           KeyPressEventManager(gui=gui, key=Key.LEFT_SHIFT),
       ]
   )

This event manager will trigger when either the left Shift key is pressed or when 1 second passes.
