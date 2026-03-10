class InputReader:
    """Reads lines from stdin using the built-in input function."""
    def read_line(self) -> str:
        """Return one stripped line of user input from stdin."""
        return input().strip()

class FakeInputReader:
    """Returns test double that contains a predetermined sequence of strings."""
    def __init__(self, values: list[str]) -> None:
        """Store the given values to be returned in order."""
        self._values = iter(values)

    def read_line(self) -> str:
        """Return the next value from the sequence."""
        return next(self._values)