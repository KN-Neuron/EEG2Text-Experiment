GUI
===

A class responsible for rendering the user interface.


Interface
----------

.. autoclass:: src.data_acquisition.gui.Gui
   :members:
   :undoc-members:
   :show-inheritance:


How to subclass
---------------

Subclasses should implement the following methods:

- ``draw_image(image_path: Path)``
- ``draw_rectangle(*, color: Color, top_left_point: Point, width: int, height: int)``
- ``draw_text(*, font_size: int, text: str, color: Color)``
- ``draw_uniform_background(color: Color)``
- ``get_window_size()  -> ElementSize``
- ``on_init(callback: Callable[[], None])``
- ``play_sound(sound_path: Path)``
- ``start()``
- ``stop()``
- ``subscribe_to_event_and_get_id(*, event: EventType, callback: Callable[[], None]) -> int``
- ``unsubscribe_from_event_by_id(event_id: int)``


Catalog
-------

.. toctree::
   :maxdepth: 1
   :titlesonly:

   gui/pygame_gui
