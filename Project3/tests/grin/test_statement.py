import unittest
import io
from grin.interpreter_state import InterpreterState
from grin.statement import (LetStatement, PrintStatement, InnumStatement,
    InstrStatement, EndStatement, make_statement, resolve)
from grin.token import GrinToken, GrinTokenKind
from grin.location import GrinLocation

def make_token(kind, text, value=None):
    return GrinToken(kind=kind, text=text, location=GrinLocation(1, 1), value=value)

LOCATION = GrinLocation(1, 1)

class TestResolve(unittest.TestCase):
    def test_integer_literal(self):
        state = InterpreterState()
        token = make_token(GrinTokenKind.LITERAL_INTEGER, '7', 7)
        self.assertEqual(resolve(token, state), 7)

    def test_string_literal(self):
        state = InterpreterState()
        token = make_token(GrinTokenKind.LITERAL_STRING, '"hi"', 'hi')
        self.assertEqual(resolve(token, state), 'hi')

    def test_variable_that_was_set(self):
        state = InterpreterState()
        state.set_variable('X', 99)
        token = make_token(GrinTokenKind.IDENTIFIER, 'X', 'X')
        self.assertEqual(resolve(token, state), 99)

    def test_variable_never_set_gives_zero(self):
        state = InterpreterState()
        token = make_token(GrinTokenKind.IDENTIFIER, 'Z', 'Z')
        self.assertEqual(resolve(token, state), 0)

class TestLetStatement(unittest.TestCase):
    def test_sets_integer(self):
        state = InterpreterState()
        var = make_token(GrinTokenKind.IDENTIFIER, 'A', 'A')
        val = make_token(GrinTokenKind.LITERAL_INTEGER, '5', 5)
        LetStatement([var, val], LOCATION).execute(state)
        self.assertEqual(state.get_variable('A'), 5)

    def test_sets_string(self):
        state = InterpreterState()
        var = make_token(GrinTokenKind.IDENTIFIER, 'S', 'S')
        val = make_token(GrinTokenKind.LITERAL_STRING, '"Boo"', 'Boo')
        LetStatement([var, val], LOCATION).execute(state)
        self.assertEqual(state.get_variable('S'), 'Boo')

    def test_copies_from_other_variable(self):
        state = InterpreterState()
        state.set_variable('B', 42)
        var = make_token(GrinTokenKind.IDENTIFIER, 'A', 'A')
        src = make_token(GrinTokenKind.IDENTIFIER, 'B', 'B')
        LetStatement([var, src], LOCATION).execute(state)
        self.assertEqual(state.get_variable('A'), 42)

    def test_overwrites_existing_value(self):
        state = InterpreterState()
        state.set_variable('A', 1)
        var = make_token(GrinTokenKind.IDENTIFIER, 'A', 'A')
        val = make_token(GrinTokenKind.LITERAL_INTEGER, '99', 99)
        LetStatement([var, val], LOCATION).execute(state)
        self.assertEqual(state.get_variable('A'), 99)

class TestPrintStatement(unittest.TestCase):
    def test_prints_integer(self):
        state = InterpreterState()
        val = make_token(GrinTokenKind.LITERAL_INTEGER, '3', 3)
        out = io.StringIO()
        PrintStatement([val], LOCATION).execute(state, output_stream=out)
        self.assertEqual(out.getvalue(), '3\n')

    def test_prints_string(self):
        state = InterpreterState()
        val = make_token(GrinTokenKind.LITERAL_STRING, '"hello"', 'hello')
        out = io.StringIO()
        PrintStatement([val], LOCATION).execute(state, output_stream=out)
        self.assertEqual(out.getvalue(), 'hello\n')

    def test_prints_unset_variable_as_zero(self):
        state = InterpreterState()
        val = make_token(GrinTokenKind.IDENTIFIER, 'Z', 'Z')
        out = io.StringIO()
        PrintStatement([val], LOCATION).execute(state, output_stream=out)
        self.assertEqual(out.getvalue(), '0\n')

    def test_prints_variable_value(self):
        state = InterpreterState()
        state.set_variable('X', 7)
        val = make_token(GrinTokenKind.IDENTIFIER, 'X', 'X')
        out = io.StringIO()
        PrintStatement([val], LOCATION).execute(state, output_stream=out)
        self.assertEqual(out.getvalue(), '7\n')

class TestInnumStatement(unittest.TestCase):
    def test_reads_integer(self):
        state = InterpreterState()
        var = make_token(GrinTokenKind.IDENTIFIER, 'X', 'X')
        InnumStatement([var], LOCATION).execute(state, input_stream=io.StringIO('42\n'))
        self.assertEqual(state.get_variable('X'), 42)

    def test_reads_float(self):
        state = InterpreterState()
        var = make_token(GrinTokenKind.IDENTIFIER, 'X', 'X')
        InnumStatement([var], LOCATION).execute(state, input_stream=io.StringIO('3.14\n'))
        self.assertAlmostEqual(state.get_variable('X'), 3.14)

    def test_bad_input_raises(self):
        state = InterpreterState()
        var = make_token(GrinTokenKind.IDENTIFIER, 'X', 'X')
        with self.assertRaises(Exception):
            InnumStatement([var], LOCATION).execute(state, input_stream=io.StringIO('abc\n'))

class TestInstrStatement(unittest.TestCase):
    def test_reads_string(self):
        state = InterpreterState()
        var = make_token(GrinTokenKind.IDENTIFIER, 'S', 'S')
        InstrStatement([var], LOCATION).execute(state, input_stream=io.StringIO('hello\n'))
        self.assertEqual(state.get_variable('S'), 'hello')

    def test_reads_empty_line(self):
        state = InterpreterState()
        var = make_token(GrinTokenKind.IDENTIFIER, 'S', 'S')
        InstrStatement([var], LOCATION).execute(state, input_stream=io.StringIO('\n'))
        self.assertEqual(state.get_variable('S'), '')

class TestEndStatement(unittest.TestCase):
    def test_marks_program_finished(self):
        state = InterpreterState()
        state._lines = [None, None, None]
        EndStatement([], LOCATION).execute(state)
        self.assertTrue(state.is_finished())

class TestMakeStatement(unittest.TestCase):
    def test_let(self):
        var = make_token(GrinTokenKind.IDENTIFIER, 'A', 'A')
        val = make_token(GrinTokenKind.LITERAL_INTEGER, '1', 1)
        kw = make_token(GrinTokenKind.LET, 'LET')
        self.assertIsInstance(make_statement([kw, var, val]), LetStatement)

    def test_print(self):
        kw = make_token(GrinTokenKind.PRINT, 'PRINT')
        val = make_token(GrinTokenKind.LITERAL_INTEGER, '1', 1)
        self.assertIsInstance(make_statement([kw, val]), PrintStatement)

    def test_innum(self):
        kw = make_token(GrinTokenKind.INNUM, 'INNUM')
        var = make_token(GrinTokenKind.IDENTIFIER, 'X', 'X')
        self.assertIsInstance(make_statement([kw, var]), InnumStatement)

    def test_instr(self):
        kw = make_token(GrinTokenKind.INSTR, 'INSTR')
        var = make_token(GrinTokenKind.IDENTIFIER, 'X', 'X')
        self.assertIsInstance(make_statement([kw, var]), InstrStatement)

    def test_end(self):
        kw = make_token(GrinTokenKind.END, 'END')
        self.assertIsInstance(make_statement([kw]), EndStatement)

    def test_label_is_skipped(self):
        label = make_token(GrinTokenKind.IDENTIFIER, 'LOOP', 'LOOP')
        colon = make_token(GrinTokenKind.COLON, ':')
        kw = make_token(GrinTokenKind.PRINT, 'PRINT')
        val = make_token(GrinTokenKind.LITERAL_INTEGER, '1', 1)
        self.assertIsInstance(make_statement([label, colon, kw, val]), PrintStatement)

if __name__ == '__main__':
    unittest.main()