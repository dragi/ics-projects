from grin.token import GrinToken
from grin.location import GrinLocation

class Statement:
    def __init__(self, tokens: list[GrinToken], location: GrinLocation):
        self._tokens = tokens
        self._location = location

    def execute(self, state) -> None:
        pass

    def location(self) -> GrinLocation:
        return self._location