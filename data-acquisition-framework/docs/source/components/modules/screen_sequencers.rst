Screen sequencers
=================

A class responsible for the logic of the :doc:`screen <screens>` sequence. Works similarly to an iterator, returning the next screen when requested. The logic of the screen sequencer may or may not depend on the result of the previous screen.

Below is an example of a sequencer that returns a sequence of screens with some data that the user has to respond to (for example with a key press). If the user responds correctly, ``True`` is passed as the result, and the next returned screen is another screen with data. If the user responds incorrectly, ``False`` is passed as the result, and the next returned screen is a screen with a message. Then ``None`` is passed as the result to the message screen, and the next returned screen is another screen with data.

.. image:: /_static/images/sequencers/example_sequencer_logic.png
   :alt: example sequencer logic
   :align: center

The methods must be called in the following order after initializing the sequencer:

1. 1 call of ``get_next()``
2. 1 call of ``pass_previous_result()``
3. go back to step 1 until the sequencer is finished

When the sequencer is finished, it raises ``StopIteration``.


Interface
---------

.. autoclass:: src.data_acquisition.sequencers.ScreenSequencer
   :members:
   :undoc-members:
   :show-inheritance:


How to subclass
---------------

Subclasses should implement the following methods:

- ``_get_next() -> EventfulScreen[T]``

Available properties and methods:

- ``_previous_result: T``: the result of the previous screen.


Catalog
-------

.. toctree::
   :maxdepth: 3
   :titlesonly:

   Composite screen sequencers <screen_sequencers/composite_screen_sequencers>
   Simple screen sequencers <screen_sequencers/simple_screen_sequencers>
