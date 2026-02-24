from grin.location import GrinLocation
from grin.token import GrinToken, GrinTokenKind

__all__ = ['Value', 'IntValue', 'FloatValue', 'StringValue', 'resolve']

class Value:
    def value(self) -> int | float | str:
        raise Exception('value() must be implemented by subclass')

    def add(self, other: 'Value', location: GrinLocation = None) -> 'Value':
        raise Exception('add() must be implemented by subclass')

    def subtract(self, other: 'Value', location: GrinLocation = None) -> 'Value':
        raise Exception('subtract() must be implemented by subclass')

    def multiply(self, other: 'Value', location: GrinLocation = None) -> 'Value':
        raise Exception('multiply() must be implemented by subclass')

    def divide(self, other: 'Value', location: GrinLocation = None) -> 'Value':
        raise Exception('divide() must be implemented by subclass')

    def _type_error(self, op: str, other: 'Value', location: GrinLocation) -> None:
        raise RuntimeError(
            f'Type mismatch: cannot apply "{op}" to '
            f'{type(self.value()).__name__} and {type(other.value()).__name__}')

class IntValue(Value):
    def __init__(self, value: int):
        self._value = value

    def value(self) -> int:
        return self._value

    def add(self, other: 'Value', location: GrinLocation = None) -> 'Value':
        if isinstance(other, IntValue):
            return IntValue(self._value + other.value())
        elif isinstance(other, FloatValue):
            return FloatValue(self._value + other.value())
        self._type_error('+', other, location)

    def subtract(self, other: 'Value', location: GrinLocation = None) -> 'Value':
        if isinstance(other, IntValue):
            return IntValue(self._value - other.value())
        elif isinstance(other, FloatValue):
            return FloatValue(self._value - other.value())
        self._type_error('-', other, location)

    def multiply(self, other: 'Value', location: GrinLocation = None) -> 'Value':
        if isinstance(other, IntValue):
            return IntValue(self._value * other.value())
        elif isinstance(other, FloatValue):
            return FloatValue(self._value * other.value())
        elif isinstance(other, StringValue):
            if self._value < 0:
                raise RuntimeError('Cannot multiply a string by a negative integer')
            return StringValue(other.value() * self._value)
        self._type_error('*', other, location)

    def divide(self, other: 'Value', location: GrinLocation = None) -> 'Value':
        if other.value() == 0:
            raise RuntimeError('Division by zero')
        if isinstance(other, IntValue):
            return IntValue(int(self._value / other.value()))
        elif isinstance(other, FloatValue):
            return FloatValue(self._value / other.value())
        self._type_error('/', other, location)

    def __repr__(self):
        return f'IntValue({self._value})'

class FloatValue(Value):
    def __init__(self, value: float):
        self._value = value

    def value(self) -> float:
        return self._value

    def add(self, other: 'Value', location: GrinLocation = None) -> 'Value':
        if isinstance(other, (IntValue, FloatValue)):
            return FloatValue(self._value + other.value())
        self._type_error('+', other, location)

    def subtract(self, other: 'Value', location: GrinLocation = None) -> 'Value':
        if isinstance(other, (IntValue, FloatValue)):
            return FloatValue(self._value - other.value())
        self._type_error('-', other, location)

    def multiply(self, other: 'Value', location: GrinLocation = None) -> 'Value':
        if isinstance(other, (IntValue, FloatValue)):
            return FloatValue(self._value * other.value())
        self._type_error('*', other, location)

    def divide(self, other: 'Value', location: GrinLocation = None) -> 'Value':
        if other.value() == 0:
            raise RuntimeError('Division by zero')
        if isinstance(other, (IntValue, FloatValue)):
            return FloatValue(self._value / other.value())
        self._type_error('/', other, location)

    def __repr__(self):
        return f'FloatValue({self._value})'

class StringValue(Value):
    def __init__(self, value: str):
        self._value = value

    def value(self) -> str:
        return self._value

    def add(self, other: 'Value', location: GrinLocation = None) -> 'Value':
        if isinstance(other, StringValue):
            return StringValue(self._value + other.value())
        self._type_error('+', other, location)

    def subtract(self, other: 'Value', location: GrinLocation = None) -> 'Value':
        self._type_error('-', other, location)

    def multiply(self, other: 'Value', location: GrinLocation = None) -> 'Value':
        if isinstance(other, IntValue):
            if other.value() < 0:
                raise RuntimeError('Cannot multiply a string by a negative integer')
            return StringValue(self._value * other.value())
        self._type_error('*', other, location)

    def divide(self, other: 'Value', location: GrinLocation = None) -> 'Value':
        self._type_error('/', other, location)

    def __repr__(self):
        return f'StringValue({self._value!r})'

def resolve(token: GrinToken, state) -> 'Value':
    kind = token.kind()

    if kind == GrinTokenKind.LITERAL_INTEGER:
        return IntValue(token.value())
    elif kind == GrinTokenKind.LITERAL_FLOAT:
        return FloatValue(token.value())
    elif kind == GrinTokenKind.LITERAL_STRING:
        return StringValue(token.value())
    elif kind == GrinTokenKind.IDENTIFIER:
        raw = state.get_variable(token.text())
        if isinstance(raw, int):
            return IntValue(raw)
        elif isinstance(raw, float):
            return FloatValue(raw)
        elif isinstance(raw, str):
            return StringValue(raw)

    raise RuntimeError(f'Cannot resolve token as a value: {token.text()}')