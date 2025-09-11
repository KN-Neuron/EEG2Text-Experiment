Experiment runner
=================

A class responsible for running the whole application. It takes a :doc:`GUI <gui>` object, a :doc:`screen sequencer <screen_sequencers>` object and a callback to be called after the experiment ends (to stop the GUI, for example) as parameters, and has one public method ``run()`` that starts the application. It should not be subclassed.


Interface
---------

.. autoclass:: src.data_acquisition.experiment_runner.ExperimentRunner
   :members:
   :undoc-members:
   :show-inheritance:
