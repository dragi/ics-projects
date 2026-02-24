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


    class TestMixedTypeOperations(unittest.TestCase):
        def test_int_add_float(self):
            result = IntValue(3).add(FloatValue(2.5))
            self.assertIsInstance(result, FloatValue)
            self.assertAlmostEqual(result.value(), 5.5)

        def test_float_add_int(self):
            result = FloatValue(3.5).add(IntValue(2))
            self.assertIsInstance(result, FloatValue)
            self.assertAlmostEqual(result.value(), 5.5)

        def test_int_multiply_float(self):
            result = IntValue(3).multiply(FloatValue(2.5))
            self.assertIsInstance(result, FloatValue)
            self.assertAlmostEqual(result.value(), 7.5)

        def test_float_multiply_int(self):
            result = FloatValue(3.5).multiply(IntValue(2))
            self.assertIsInstance(result, FloatValue)
            self.assertAlmostEqual(result.value(), 7.0)

        def test_int_divide_float(self):
            result = IntValue(7).divide(FloatValue(2.0))
            self.assertIsInstance(result, FloatValue)
            self.assertAlmostEqual(result.value(), 3.5)

        def test_float_divide_int(self):
            result = FloatValue(7.5).divide(IntValue(2))
            self.assertIsInstance(result, FloatValue)
            self.assertAlmostEqual(result.value(), 3.75)


    class TestValueEdgeCases(unittest.TestCase):
        def test_int_divide_by_float_zero(self):
            with self.assertRaises(RuntimeError):
                IntValue(5).divide(FloatValue(0.0))

        def test_float_divide_by_int_zero(self):
            with self.assertRaises(RuntimeError):
                FloatValue(5.0).divide(IntValue(0))

        def test_int_multiply_string_zero(self):
            result = IntValue(0).multiply(StringValue('abc'))
            self.assertEqual(result.value(), '')

        def test_string_multiply_zero(self):
            result = StringValue('abc').multiply(IntValue(0))
            self.assertEqual(result.value(), '')

        def test_float_value_representation(self):
            f = FloatValue(3.14)
            self.assertAlmostEqual(f.value(), 3.14)

if __name__ == '__main__':
    unittest.main()