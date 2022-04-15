class StatefulCounter:
    def __init__(self, init_value: int = 0):
        self._value = init_value

    def increment(self, amnt: int = 1) -> None:
        self._value += amnt

    @property
    def value(self) -> int:
        return self._value
