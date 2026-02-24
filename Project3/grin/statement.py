import sys
from grin.token import GrinToken, GrinTokenKind
from grin.location import GrinLocation
from grin.value import IntValue, FloatValue, StringValue, resolve

__all__ = [
    'Statement', 'LetStatement', 'PrintStatement', 'InnumStatement', 'InstrStatement',
    'EndStatement', 'resolve', 'make_statement', 'ArithmeticStatement',
    'AddStatement', 'SubStatement', 'MultStatement', 'DivStatement',
    'GotoStatement', 'GosubStatement', 'ReturnStatement'
]

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
            raise RuntimeError('INNUM expected a number')

class InstrStatement(Statement):
    def __init__(self, tokens, location):
        super().__init__(tokens, location)
        self._variable_name = tokens[0].text()

    def execute(self, state, input_stream=sys.stdin) -> None:
        state.set_variable(self._variable_name, input_stream.readline().rstrip('\n'))


class EndStatement(Statement):
    def execute(self, state) -> None:
        state.end()

class ArithmeticStatement(Statement):
    def __init__(self, tokens, location):
        super().__init__(tokens, location)
        self._variable_name = tokens[0].text()
        self._value_token = tokens[1]

    def _apply(self, left, right):
        raise Exception('_apply must be implemented by subclass')

    def execute(self, state) -> None:
        current_raw = state.get_variable(self._variable_name)
        if isinstance(current_raw, int):
            current = IntValue(current_raw)
        elif isinstance(current_raw, float):
            current = FloatValue(current_raw)
        else:
            current = StringValue(current_raw)
        operand = resolve(self._value_token, state)
        result = self._apply(current, operand)
        state.set_variable(self._variable_name, result.value())

class AddStatement(ArithmeticStatement):
    def _apply(self, left, right):
        return left.add(right, self._location)

class SubStatement(ArithmeticStatement):
    def _apply(self, left, right):
        return left.subtract(right, self._location)

class MultStatement(ArithmeticStatement):
    def _apply(self, left, right):
        return left.multiply(right, self._location)

class DivStatement(ArithmeticStatement):
    def _apply(self, left, right):
        return left.divide(right, self._location)

class GotoStatement(Statement):
    def __init__(self, tokens, location):
        super().__init__(tokens, location)
        self._target_token = tokens[0]

        if len(tokens) > 1 and tokens[1].kind() == GrinTokenKind.IF:
            self._cond_val1 = tokens[2]
            self._cond_op = tokens[3]
            self._cond_val2 = tokens[4]
        else:
            self._cond_val1 = None
            self._cond_op = None
            self._cond_val2 = None

    def _condition_is_true(self, state) -> bool:
        if self._cond_op is None:
            return True
        left = resolve(self._cond_val1, state)
        right = resolve(self._cond_val2, state)
        return _compare(left, right, self._cond_op)

    def _resolve_target(self, state) -> int:
        token = self._target_token

        if token.kind() == GrinTokenKind.LITERAL_INTEGER:
            return _offset_to_line(token.value(), state, self._location)

        elif token.kind() == GrinTokenKind.LITERAL_STRING:
            return _label_to_line(token.value(), state, self._location)

        elif token.kind() == GrinTokenKind.IDENTIFIER:
            raw = state.get_variable(token.text())
            if isinstance(raw, int):
                return _offset_to_line(raw, state, self._location)
            elif isinstance(raw, str):
                return _label_to_line(raw, state, self._location)
            else:
                raise RuntimeError('Jump target variable must hold an integer or string')

        raise RuntimeError('Invalid jump target')

    def execute(self, state) -> None:
        if not self._condition_is_true(state):
            return
        target = self._resolve_target(state)
        state.jump_to_line(target)

class GosubStatement(GotoStatement):
    def execute(self, state) -> None:
        if not self._condition_is_true(state):
            return
        target = self._resolve_target(state)
        state.push_return(state.current_line() + 1)
        state.jump_to_line(target)

class ReturnStatement(Statement):
    def execute(self, state) -> None:
        if not state.has_return():
            raise RuntimeError('RETURN with no matching GOSUB')
        state.jump_to_line(state.pop_return())

def _offset_to_line(offset: int, state, location) -> int:
    if offset == 0:
        raise RuntimeError('GOTO 0 is not permitted')
    target = state.current_line() + offset
    if target < 0 or target > state.length():
        raise RuntimeError(f'Jump target is out of range')
    return target

def _label_to_line(label: str, state, location) -> int:
    line = state.label_line(label)
    if line is None:
        raise RuntimeError(f'Unknown label "{label}"')
    return line

def _compare(left, right, op_token) -> bool:
    l = left.value()
    r = right.value()

    l_num = isinstance(l, (int, float))
    r_num = isinstance(r, (int, float))
    if not ((l_num and r_num) or (isinstance(l, str) and isinstance(r, str))):
        raise RuntimeError(f'Type mismatch in comparison')

    op = op_token.kind()
    if op == GrinTokenKind.EQUAL:
        return l == r
    elif op == GrinTokenKind.NOT_EQUAL:
        return l != r
    elif op == GrinTokenKind.LESS_THAN:
        return l < r
    elif op == GrinTokenKind.LESS_THAN_OR_EQUAL:
        return l <= r
    elif op == GrinTokenKind.GREATER_THAN:
        return l > r
    elif op == GrinTokenKind.GREATER_THAN_OR_EQUAL:
        return l >= r

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
    elif keyword_token.kind() == GrinTokenKind.ADD:
        return AddStatement(rest, keyword_token.location())
    elif keyword_token.kind() == GrinTokenKind.SUB:
        return SubStatement(rest, keyword_token.location())
    elif keyword_token.kind() == GrinTokenKind.MULT:
        return MultStatement(rest, keyword_token.location())
    elif keyword_token.kind() == GrinTokenKind.DIV:
        return DivStatement(rest, keyword_token.location())
    elif keyword_token.kind() == GrinTokenKind.GOTO:
        return GotoStatement(rest, keyword_token.location())
    elif keyword_token.kind() == GrinTokenKind.GOSUB:
        return GosubStatement(rest, keyword_token.location())
    elif keyword_token.kind() == GrinTokenKind.RETURN:
        return ReturnStatement(rest, keyword_token.location())