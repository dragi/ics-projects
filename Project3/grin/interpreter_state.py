from grin.token import GrinTokenKind
from grin.parsing import parse

class InterpreterState:
    def __init__(self):
        self._variables = {}
        self._call_stack = []
        self._labels = {}
        self._current_line = 0
        self._lines = None
        self._finished = False

    def read_lines(self) -> None:
        lines = []
        line = input().strip()

        while len(line) > 0 and line != '.':
            lines.append(line)
            line = input().strip()

        self._lines = list(parse(lines))
        self._labels = self._map_labels()

    def current_line(self) -> int:
        return self._current_line

    def lines(self) -> list[str]:
        return self._lines

    def length(self) -> int:
        return len(self._lines)

    def go_to_next_line(self) -> None:
        self._current_line += 1

    def jump_to_line(self, line: int) -> None:
        self._current_line = line - 1

    def is_finished(self) -> bool:
        return self._finished or self._current_line >= len(self._lines)

    def end(self) -> None:
        self._finished = True

    def get_variable(self, name: str) -> int|float|str:
        return self._variables.get(name, 0)

    def set_variable(self, name: str, value: int|float|str) -> None:
        self._variables[name] = value

    def label_line(self, name: str) -> int | None:
        return self._labels.get(name, None)

    def _map_labels(self) -> dict[str, int]:
        labels = {}
        for index, tokens in enumerate(self._lines):
            if (len(tokens) >= 2 and tokens[0].kind() == GrinTokenKind.IDENTIFIER
                    and tokens[1].kind() == GrinTokenKind.COLON):
                labels[tokens[0].text()] = index
        return labels

    def push_return(self, line: int) -> None:
        self._call_stack.append(line)

    def pop_return(self) -> int:
        if not self._call_stack:
            raise IndexError('Call stack is empty')
        return self._call_stack.pop()

    def has_return(self) -> bool:
        return len(self._call_stack) > 0

__all__ = ['InterpreterState']