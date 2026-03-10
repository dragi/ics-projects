import random

class Randomizer:
    def randint(self, a, b):
        return random.randint(a, b)

class FakeRandomizer:
    def __init__(self, values):
        self._values = iter(values)

    def randint(self, a, b):
        return next(self._values)