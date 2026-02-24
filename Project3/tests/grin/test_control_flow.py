import unittest
from grin.interpreter_state import InterpreterState
from grin.statement import (GotoStatement, GosubStatement, ReturnStatement, make_statement)
from grin.token import GrinToken, GrinTokenKind
from grin.location import GrinLocation

def make_token(kind, text, value=None):
    return GrinToken(kind=kind, text=text, location=GrinLocation(1, 1), value=value)

LOCATION = GrinLocation(1, 1)

def make_program(n):
    state = InterpreterState()
    state._lines = [None] * n
    return state

class TestGotoStatement(unittest.TestCase):
    def test_basic_forward_jump(self):
        state = make_program(5)
        # GOTO 2 from line 0 should land on line 2
        target = make_token(GrinTokenKind.LITERAL_INTEGER, '2', 2)
        GotoStatement([target], LOCATION).execute(state)
        state.go_to_next_line()
        self.assertEqual(state.current_line(), 2)

    def test_backward_jump(self):
        state = make_program(5)
        state._current_line = 3
        target = make_token(GrinTokenKind.LITERAL_INTEGER, '-2', -2)
        GotoStatement([target], LOCATION).execute(state)
        state.go_to_next_line()
        self.assertEqual(state.current_line(), 1)

    def test_jump_to_label(self):
        state = make_program(5)
        state._labels = {'loop': 3}
        target = make_token(GrinTokenKind.LITERAL_STRING, '"loop"', 'loop')
        GotoStatement([target], LOCATION).execute(state)
        state.go_to_next_line()
        self.assertEqual(state.current_line(), 3)

    def test_goto_zero_raises(self):
        state = make_program(5)
        target = make_token(GrinTokenKind.LITERAL_INTEGER, '0', 0)
        with self.assertRaises(RuntimeError):
            GotoStatement([target], LOCATION).execute(state)

    def test_out_of_range_raises(self):
        state = make_program(3)
        target = make_token(GrinTokenKind.LITERAL_INTEGER, '99', 99)
        with self.assertRaises(RuntimeError):
            GotoStatement([target], LOCATION).execute(state)

    def test_unknown_label_raises(self):
        state = make_program(3)
        state._labels = {}
        target = make_token(GrinTokenKind.LITERAL_STRING, '"nowhere"', 'nowhere')
        with self.assertRaises(RuntimeError):
            GotoStatement([target], LOCATION).execute(state)

    def test_conditional_jump_taken(self):
        state = make_program(5)
        state.set_variable('A', 3)
        target = make_token(GrinTokenKind.LITERAL_INTEGER, '2', 2)
        IF = make_token(GrinTokenKind.IF, 'IF')
        val1 = make_token(GrinTokenKind.IDENTIFIER, 'A', 'A')
        op = make_token(GrinTokenKind.LESS_THAN, '<')
        val2 = make_token(GrinTokenKind.LITERAL_INTEGER, '4', 4)
        GotoStatement([target, IF, val1, op, val2], LOCATION).execute(state)
        state.go_to_next_line()
        self.assertEqual(state.current_line(), 2)

    def test_conditional_jump_not_taken(self):
        state = make_program(5)
        state.set_variable('A', 5)
        target = make_token(GrinTokenKind.LITERAL_INTEGER, '2', 2)
        IF = make_token(GrinTokenKind.IF, 'IF')
        val1 = make_token(GrinTokenKind.IDENTIFIER, 'A', 'A')
        op = make_token(GrinTokenKind.LESS_THAN, '<')
        val2 = make_token(GrinTokenKind.LITERAL_INTEGER, '4', 4)
        GotoStatement([target, IF, val1, op, val2], LOCATION).execute(state)
        state.go_to_next_line()
        self.assertEqual(state.current_line(), 1)

class TestGosubAndReturn(unittest.TestCase):
    def test_gosub_pushes_return_address(self):
        state = make_program(5)
        target = make_token(GrinTokenKind.LITERAL_INTEGER, '2', 2)
        GosubStatement([target], LOCATION).execute(state)
        self.assertTrue(state.has_return())

    def test_gosub_return_address_is_next_line(self):
        state = make_program(5)
        state._current_line = 1
        target = make_token(GrinTokenKind.LITERAL_INTEGER, '2', 2)
        GosubStatement([target], LOCATION).execute(state)
        self.assertEqual(state.pop_return(), 2)

    def test_return_jumps_back(self):
        state = make_program(5)
        state.push_return(3)
        ReturnStatement([], LOCATION).execute(state)
        state.go_to_next_line()
        self.assertEqual(state.current_line(), 3)

    def test_return_no_gosub_raises(self):
        state = make_program(5)
        with self.assertRaises(RuntimeError):
            ReturnStatement([], LOCATION).execute(state)

    def test_nested_gosub(self):
        state = make_program(10)
        state._current_line = 0
        target1 = make_token(GrinTokenKind.LITERAL_INTEGER, '3', 3)
        GosubStatement([target1], LOCATION).execute(state)
        state.go_to_next_line()

        target2 = make_token(GrinTokenKind.LITERAL_INTEGER, '2', 2)
        GosubStatement([target2], LOCATION).execute(state)

        ReturnStatement([], LOCATION).execute(state)
        state.go_to_next_line()
        inner_return = state.current_line()

        ReturnStatement([], LOCATION).execute(state)
        state.go_to_next_line()
        outer_return = state.current_line()

        self.assertNotEqual(inner_return, outer_return)
        self.assertFalse(state.has_return())

class TestMakeStatementJumps(unittest.TestCase):
    def test_makes_goto(self):
        kw = make_token(GrinTokenKind.GOTO, 'GOTO')
        target = make_token(GrinTokenKind.LITERAL_INTEGER, '1', 1)
        self.assertIsInstance(make_statement([kw, target]), GotoStatement)

    def test_makes_gosub(self):
        kw = make_token(GrinTokenKind.GOSUB, 'GOSUB')
        target = make_token(GrinTokenKind.LITERAL_INTEGER, '1', 1)
        self.assertIsInstance(make_statement([kw, target]), GosubStatement)

    def test_makes_return(self):
        kw = make_token(GrinTokenKind.RETURN, 'RETURN')
        self.assertIsInstance(make_statement([kw]), ReturnStatement)

if __name__ == '__main__':
    unittest.main()