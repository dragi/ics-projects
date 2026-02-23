from grin.parsing import parse

class InterpreterState:
    def __init__(self):
        self._variables = {}
        self._current_line = 0
        self._parsed_lines = None

    def read_lines(self) -> None:
        lines = []
        line = input().strip()

        while len(line) > 0 and line != '.':
            lines.append(line)
            line = input().strip()

        self._parsed_lines = parse(lines)

    def current_line(self) -> int:
        return self._current_line

    def get_variable(self, name: str) -> int|float|str:
        return self._variables[name]

    def set_variable(self, name: str, value: int|float|str) -> None:
        self._variables[name] = value

__all__ = [InterpreterState.__name__]