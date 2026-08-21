import random
from typing import Iterator

class Randomizer:
    """Wraps the standard library random.randint for use in generation."""
    def randint(self, a: int, b: int) -> int:
        """Return a random integer between a and b inclusive."""
        return random.randint(a, b)

class FakeRandomizer:
    """Test double that returns a predetermined sequence of integers."""
    def __init__(self, values: list[int]) -> None:
        """Store the given values as an iterator."""
        self._values: Iterator[int] = iter(values)

    def randint(self, a: int, b: int) -> int:
        """Return the next value from the sequence, ignoring a and b."""
        return next(self._values)