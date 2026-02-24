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
    def __init__(self, tokens: list[GrinToken], location: GrinLocation, label: str = None):
        self._tokens = tokens
        self._location = location
        self._label = label

    def location(self) -> GrinLocation:
        return self._location

    def label(self) -> str:
        return self._label

    def execute(self, state) -> None:
        pass

class LetStatement(Statement):
    def __init__(self, tokens, location, label=None):
        super().__init__(tokens, location, label)
        self._variable_name = tokens[0].text()
        self._value = tokens[1]

    def execute(self, state) -> None:
        value = resolve(self._value, state)
        state.set_variable(self._variable_name, value.value())

class PrintStatement(Statement):
    def __init__(self, tokens, location, label=None):
        super().__init__(tokens, location, label)
        self._value = tokens[0]

    def execute(self, state) -> None:
        print(resolve(self._value, state).value())

class InnumStatement(Statement):
    def __init__(self, tokens, location, label=None):
        super().__init__(tokens, location, label)
        self._variable_name = tokens[0].text()

    def execute(self, state) -> None:
        raw = input().strip()
        try:
            if '.' in raw:
                val = float(raw)
                if val.is_integer():
                    state.set_variable(self._variable_name, int(val))
                else:
                    state.set_variable(self._variable_name, val)
            else:
                state.set_variable(self._variable_name, int(raw))
        except ValueError:
            raise RuntimeError(f'INNUM expected a number, got "{raw}"')

class InstrStatement(Statement):
    def __init__(self, tokens, location, label=None):
        super().__init__(tokens, location, label)
        self._variable_name = tokens[0].text()

    def execute(self, state) -> None:
        state.set_variable(self._variable_name, input().rstrip('\n'))

class EndStatement(Statement):
    def __init__(self, tokens, location, label=None):
        super().__init__(tokens, location, label)

    def execute(self, state) -> None:
        state.end()

class ArithmeticStatement(Statement):
    def __init__(self, tokens, location, label=None):
        super().__init__(tokens, location, label)
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
    def __init__(self, tokens, location, label=None):
        super().__init__(tokens, location, label)

    def _apply(self, left, right):
        return left.add(right, self._location)

class SubStatement(ArithmeticStatement):
    def __init__(self, tokens, location, label=None):
        super().__init__(tokens, location, label)

    def _apply(self, left, right):
        return left.subtract(right, self._location)

class MultStatement(ArithmeticStatement):
    def __init__(self, tokens, location, label=None):
        super().__init__(tokens, location, label)

    def _apply(self, left, right):
        return left.multiply(right, self._location)

class DivStatement(ArithmeticStatement):
    def __init__(self, tokens, location, label=None):
        super().__init__(tokens, location, label)

    def _apply(self, left, right):
        return left.divide(right, self._location)

class GotoStatement(Statement):
    def __init__(self, tokens, location, label=None):
        super().__init__(tokens, location, label)
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
            state.go_to_next_line()
            return
        target = self._resolve_target(state)
        state.jump_to_line(target)

class GosubStatement(GotoStatement):
    def __init__(self, tokens, location, label=None):
        super().__init__(tokens, location, label)

    def execute(self, state) -> None:
        if not self._condition_is_true(state):
            state.go_to_next_line()
            return
        target = self._resolve_target(state)
        state.push_return(state.current_line() + 1)
        state.jump_to_line(target)

class ReturnStatement(Statement):
    def __init__(self, tokens, location, label=None):
        super().__init__(tokens, location, label)

    def execute(self, state) -> None:
        if not state.has_return():
            raise RuntimeError('RETURN with no matching GOSUB')
        state.jump_to_line(state.pop_return())

def _offset_to_line(offset: int, state, location) -> int:
    if offset == 0:
        raise RuntimeError('GOTO 0 is not permitted')

    current_line_num = state.current_line() + 1
    target_line_num = current_line_num + offset

    if target_line_num < 1 or target_line_num > state.length():
        raise RuntimeError(f'Jump target {target_line_num} is out of range (1-{state.length()})')

    return target_line_num - 1

def _label_to_line(label: str, state, location) -> int:
    line = state.label_line(label)
    if line is None:
        raise RuntimeError(f'Unknown label "{label}"')
    return line

def _compare(left, right, op_token) -> bool:
    l_val = left.value()
    r_val = right.value()

    if isinstance(l_val, (int, float)) and isinstance(r_val, (int, float)):
        l_num = float(l_val) if isinstance(l_val, int) else l_val
        r_num = float(r_val) if isinstance(r_val, int) else r_val

        op = op_token.kind()
        if op == GrinTokenKind.EQUAL:
            return l_num == r_num
        elif op == GrinTokenKind.NOT_EQUAL:
            return l_num != r_num
        elif op == GrinTokenKind.LESS_THAN:
            return l_num < r_num
        elif op == GrinTokenKind.LESS_THAN_OR_EQUAL:
            return l_num <= r_num
        elif op == GrinTokenKind.GREATER_THAN:
            return l_num > r_num
        elif op == GrinTokenKind.GREATER_THAN_OR_EQUAL:
            return l_num >= r_num

    elif isinstance(l_val, str) and isinstance(r_val, str):
        op = op_token.kind()
        if op == GrinTokenKind.EQUAL:
            return l_val == r_val
        elif op == GrinTokenKind.NOT_EQUAL:
            return l_val != r_val
        elif op == GrinTokenKind.LESS_THAN:
            return l_val < r_val
        elif op == GrinTokenKind.LESS_THAN_OR_EQUAL:
            return l_val <= r_val
        elif op == GrinTokenKind.GREATER_THAN:
            return l_val > r_val
        elif op == GrinTokenKind.GREATER_THAN_OR_EQUAL:
            return l_val >= r_val

    raise RuntimeError(
        f'Type mismatch in comparison: cannot compare {type(l_val).__name__} with {type(r_val).__name__}')

def make_statement(tokens: list) -> Statement:
    index = 0
    label = None

    if (len(tokens) >= 2
            and tokens[index].kind() == GrinTokenKind.IDENTIFIER
            and tokens[index + 1].kind() == GrinTokenKind.COLON):
        label = tokens[index].text()
        index += 2

    keyword_token = tokens[index]
    rest = tokens[index + 1:]

    if keyword_token.kind() == GrinTokenKind.LET:
        return LetStatement(rest, keyword_token.location(), label)
    elif keyword_token.kind() == GrinTokenKind.PRINT:
        return PrintStatement(rest, keyword_token.location(), label)
    elif keyword_token.kind() == GrinTokenKind.INNUM:
        return InnumStatement(rest, keyword_token.location(), label)
    elif keyword_token.kind() == GrinTokenKind.INSTR:
        return InstrStatement(rest, keyword_token.location(), label)
    elif keyword_token.kind() == GrinTokenKind.END:
        return EndStatement(rest, keyword_token.location(), label)
    elif keyword_token.kind() == GrinTokenKind.ADD:
        return AddStatement(rest, keyword_token.location(), label)
    elif keyword_token.kind() == GrinTokenKind.SUB:
        return SubStatement(rest, keyword_token.location(), label)
    elif keyword_token.kind() == GrinTokenKind.MULT:
        return MultStatement(rest, keyword_token.location(), label)
    elif keyword_token.kind() == GrinTokenKind.DIV:
        return DivStatement(rest, keyword_token.location(), label)
    elif keyword_token.kind() == GrinTokenKind.GOTO:
        return GotoStatement(rest, keyword_token.location(), label)
    elif keyword_token.kind() == GrinTokenKind.GOSUB:
        return GosubStatement(rest, keyword_token.location(), label)
    elif keyword_token.kind() == GrinTokenKind.RETURN:
        return ReturnStatement(rest, keyword_token.location(), label)

    raise RuntimeError(f'Unknown statement type: {keyword_token.kind()}')