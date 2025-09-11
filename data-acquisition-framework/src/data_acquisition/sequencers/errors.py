class ScreenSequencerError(Exception):
    pass


class EmptyInitialScreenSequenceError(ScreenSequencerError):
    pass


class IncorrectMethodCallOrderError(ScreenSequencerError):
    pass


class ScreenSequencerStopIteration(ScreenSequencerError):
    pass
