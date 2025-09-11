Screens
=======

A class responsible for displaying a single screen. It needs to be passed a GUI object and has one public method: ``show()``.


Interface
---------
.. autoclass:: src.data_acquisition.screens.Screen
   :members:
   :undoc-members:
   :show-inheritance:


How to subclass
---------------

Subclasses should implement the following methods:

- ``show()``

Available properties and methods:

- ``_gui: Gui``


Catalog
-------

.. toctree::
   :maxdepth: 1
   :titlesonly:

   screens/blank_screen
   screens/fixation_cross_screen
   screens/text_screen
