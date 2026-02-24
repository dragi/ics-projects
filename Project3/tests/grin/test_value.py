import unittest
from grin.value import IntValue, FloatValue, StringValue, resolve
from grin.interpreter_state import InterpreterState
from grin.token import GrinToken, GrinTokenKind
from grin.location import GrinLocation

class TestIntValue(unittest.TestCase):
    def test_add(self):
        self.assertEqual(IntValue(3).add(IntValue(4)).value(), 7)

    def test_add_string_raises(self):
        with self.assertRaises(RuntimeError):
            IntValue(3).add(StringValue('hi'))

    def test_multiply_string(self):
        self.assertEqual(IntValue(3).multiply(StringValue('ab')).value(), 'ababab')

    def test_multiply_negative_string_raises(self):
        with self.assertRaises(RuntimeError):
            IntValue(-2).multiply(StringValue('ab'))

    def test_divide_truncates(self):
        self.assertEqual(IntValue(7).divide(IntValue(2)).value(), 3)
        self.assertEqual(IntValue(-7).divide(IntValue(2)).value(), -3)

    def test_divide_by_zero_raises(self):
        with self.assertRaises(RuntimeError):
            IntValue(5).divide(IntValue(0))

class TestFloatValue(unittest.TestCase):
    def test_add(self):
        self.assertAlmostEqual(FloatValue(1.5).add(FloatValue(2.5)).value(), 4.0)

    def test_add_string_raises(self):
        with self.assertRaises(RuntimeError):
            FloatValue(1.5).add(StringValue('hi'))

    def test_divide_by_zero_raises(self):
        with self.assertRaises(RuntimeError):
            FloatValue(5.0).divide(FloatValue(0.0))

class TestStringValue(unittest.TestCase):
    def test_add(self):
        self.assertEqual(StringValue('Boo').add(StringValue('lean')).value(), 'Boolean')

    def test_add_int_raises(self):
        with self.assertRaises(RuntimeError):
            StringValue('hi').add(IntValue(1))

    def test_multiply(self):
        self.assertEqual(StringValue('ab').multiply(IntValue(3)).value(), 'ababab')

    def test_multiply_negative_raises(self):
        with self.assertRaises(RuntimeError):
            StringValue('ab').multiply(IntValue(-1))

class TestResolve(unittest.TestCase):
    def test_int_token(self):
        token = GrinToken(kind=GrinTokenKind.LITERAL_INTEGER, text='7',
                          location=GrinLocation(1, 1), value=7)
        self.assertEqual(resolve(token, InterpreterState()).value(), 7)

    def test_variable_lookup(self):
        state = InterpreterState()
        state.set_variable('X', 99)
        token = GrinToken(kind=GrinTokenKind.IDENTIFIER, text='X',
                          location=GrinLocation(1, 1), value='X')
        self.assertEqual(resolve(token, state).value(), 99)

    def test_unset_variable_is_zero(self):
        token = GrinToken(kind=GrinTokenKind.IDENTIFIER, text='Z',
                          location=GrinLocation(1, 1), value='Z')
        self.assertEqual(resolve(token, InterpreterState()).value(), 0)

if __name__ == '__main__':
    unittest.main()