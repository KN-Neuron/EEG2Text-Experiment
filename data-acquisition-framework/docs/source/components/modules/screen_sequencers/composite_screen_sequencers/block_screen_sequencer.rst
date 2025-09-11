Block screen sequencer
======================

Sequencer that combines mutiple sub-sequencers into blocks. Each sub-sequencer is its own block. The block sequencer can also be passed 2 callbacks: one to be called when a block starts, and one to be called when a block ends, which can be useful for starting and stopping data acquisition. Both callbacks are passed the block number (1-indexed) as an argument.

.. autoclass:: src.data_acquisition.sequencers.BlockScreenSequencer
   :special-members: __init__
   :show-inheritance:

.. warning::
   
   Block end callback is only called when getting the first screen of the next block (or, for the last block, when trying to get the next screen when there is none left).


Usage example
-------------

.. code-block:: python

    sequencer = BlockScreenSequencer(
        sequencers=[
            TextScreenSequencer(
                gui=gui, event_manager=event_manager, texts=["a", "b", "c"]
            ),
            TextScreenSequencer(
                gui=gui, event_manager=event_manager, texts=["1", "2", "3"]
            ),
        ],
        block_start_callback=lambda _: eeg_headset.start(),
        block_end_callback=lambda block_number: eeg_headset.stop_and_save_at_path(Path(f"test_{block_number}.fif")),
    )

This sequencers will first return all the screens from the first sequencer (with texts "a", "b", "c"), and then all the screens from the second sequencer ("1", "2", "3"). EEG acquisition will be started when getting the screen with text "a". It will be stopped and saved at file `test_1.fif` when getting the screen with text "1"; at the same time, new acquisition will be started. It will be stopped and saved at file `test_2.fif` when trying to get a screen after "3".
