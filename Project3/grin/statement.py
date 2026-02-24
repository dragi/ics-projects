import sys
from grin.token import GrinToken, GrinTokenKind
from grin.location import GrinLocation

def resolve(token: GrinToken, state) -> int|float|str:
    if token.kind() == GrinTokenKind.LITERAL_INTEGER:
        return token.value()
    elif token.kind() == GrinTokenKind.LITERAL_FLOAT:
        return token.value()
    elif token.kind() == GrinTokenKind.LITERAL_STRING:
        return token.value()
    else:
        return state.get_variable(token.text())

class Statement:
    def __init__(self, tokens: list[GrinToken], location: GrinLocation):
        self._tokens = tokens
        self._location = location

    def location(self) -> GrinLocation:
        return self._location

    def execute(self, state) -> None:
        pass

class LetStatement(Statement):
    def __init__(self, tokens, location):
        super().__init__(tokens, location)
        self._variable_name = tokens[0].text()
        self._value = tokens[1]

    def execute(self, state) -> None:
        value = resolve(self._value, state)
        state.set_variable(self._variable_name, value)

class PrintStatement(Statement):
    def __init__(self, tokens, location):
        super().__init__(tokens, location)
        self._value = tokens[0]

    def execute(self, state, output_stream=sys.stdout) -> None:
        print(resolve(self._value, state), file=output_stream)

class InnumStatement(Statement):
    def __init__(self, tokens, location):
        super().__init__(tokens, location)
        self._variable_name = tokens[0].text()

    def execute(self, state, input_stream=sys.stdin) -> None:
        raw = input_stream.readline().strip()
        try:
            if '.' in raw:
                state.set_variable(self._variable_name, float(raw))
            else:
                state.set_variable(self._variable_name, int(raw))
        except ValueError:
            raise RuntimeError

class InstrStatement(Statement):
    def __init__(self, tokens, location):
        super().__init__(tokens, location)
        self._variable_name = tokens[0].text()

    def execute(self, state, input_stream=sys.stdin) -> None:
        state.set_variable(self._variable_name, input_stream.readline().rstrip('\n'))

class ReturnStatement(Statement):
    def execute(self, state) -> None:
        if not state.has_return():
            raise RuntimeError
        state.jump_to(state.pop_return())

class EndStatement(Statement):
    def execute(self, state) -> None:
        state.end()

def make_statement(tokens: list) -> Statement:
    index = 0

    if (len(tokens) >= 2
            and tokens[index].kind() == GrinTokenKind.IDENTIFIER
            and tokens[index + 1].kind() == GrinTokenKind.COLON):
        index += 2

    keyword_token = tokens[index]
    rest = tokens[index + 1:]

    if keyword_token.kind() == GrinTokenKind.LET:
        return LetStatement(rest, keyword_token.location())
    elif keyword_token.kind() == GrinTokenKind.PRINT:
        return PrintStatement(rest, keyword_token.location())
    elif keyword_token.kind() == GrinTokenKind.INNUM:
        return InnumStatement(rest, keyword_token.location())
    elif keyword_token.kind() == GrinTokenKind.INSTR:
        return InstrStatement(rest, keyword_token.location())
    elif keyword_token.kind() == GrinTokenKind.END:
        return EndStatement(rest, keyword_token.location())

__all__ = [
    'Statement', 'LetStatement', 'PrintStatement', 'InnumStatement', 'InstrStatement',
        'ReturnStatement', 'EndStatement', 'resolve', 'make_statement'
]