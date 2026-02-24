import unittest
from grin.interpreter_state import InterpreterState

class TestInterpreterStateVariables(unittest.TestCase):
    def test_uninitialized_variable_defaults_to_zero(self):
        state = InterpreterState()
        self.assertEqual(state.get_variable('X'), 0)

    def test_set_and_get_int_variable(self):
        state = InterpreterState()
        state.set_variable('A', 42)
        self.assertEqual(state.get_variable('A'), 42)

    def test_set_and_get_float_variable(self):
        state = InterpreterState()
        state.set_variable('F', 2.01)
        self.assertAlmostEqual(state.get_variable('F'), 2.01)

    def test_set_and_get_string_variable(self):
        state = InterpreterState()
        state.set_variable('S', 'hello')
        self.assertEqual(state.get_variable('S'), 'hello')

    def test_variable_can_be_overwritten(self):
        state = InterpreterState()
        state.set_variable('A', 1)
        state.set_variable('A', 2)
        self.assertEqual(state.get_variable('A'), 2)

    def test_multiple_different_variables(self):
        state = InterpreterState()
        state.set_variable('X', 1)
        state.set_variable('Y', 2)
        self.assertEqual(state.get_variable('X'), 1)
        self.assertEqual(state.get_variable('Y'), 2)


class TestInterpreterStateLines(unittest.TestCase):
    def test_starts_at_line_zero(self):
        state = InterpreterState()
        self.assertEqual(state.current_line(), 0)

    def test_advance_once(self):
        state = InterpreterState()
        state.go_to_next_line()
        self.assertEqual(state.current_line(), 1)

    def test_advance_several_times(self):
        state = InterpreterState()
        state.go_to_next_line()
        state.go_to_next_line()
        state.go_to_next_line()
        self.assertEqual(state.current_line(), 3)

    def test_jump_sets_correct_line(self):
        state = InterpreterState()
        state.jump_to_line(5)
        self.assertEqual(state.current_line(), 4)

    def test_empty_program_finished(self):
        state = InterpreterState()
        state._lines = []
        self.assertTrue(state.is_finished())

    def test_program_with_lines_not_finished_initially(self):
        state = InterpreterState()
        state._lines = [None, None]
        self.assertFalse(state.is_finished())

    def test_end_stops_execution(self):
        state = InterpreterState()
        state._lines = [None, None]
        state.end()
        self.assertTrue(state.is_finished())

    def test_advancing_past_last_line_is_finished(self):
        state = InterpreterState()
        state._lines = [None]
        state.go_to_next_line()
        self.assertTrue(state.is_finished())

class TestCallStack(unittest.TestCase):
    def test_stack_empty_at_start(self):
        state = InterpreterState()
        self.assertFalse(state.has_return())

    def test_push_makes_stack_nonempty(self):
        state = InterpreterState()
        state.push_return(3)
        self.assertTrue(state.has_return())

    def test_push_and_pop_gives_back_same_value(self):
        state = InterpreterState()
        state.push_return(10)
        self.assertEqual(state.pop_return(), 10)

    def test_lifo_ordering(self):
        state = InterpreterState()
        state.push_return(1)
        state.push_return(2)
        first_pop = state.pop_return()
        second_pop = state.pop_return()
        self.assertEqual(first_pop, 2)
        self.assertEqual(second_pop, 1)

    def test_pop_empty_raises_index_error(self):
        state = InterpreterState()
        with self.assertRaises(IndexError):
            state.pop_return()

    def test_empty_after_popping_last(self):
        state = InterpreterState()
        state.push_return(5)
        state.pop_return()
        self.assertFalse(state.has_return())


    class TestLabelMapping(unittest.TestCase):
        def setUp(self):
            from grin.token import GrinTokenKind
            self.token1 = GrinToken(kind = GrinTokenKind.IDENTIFIER, text = 'START',
                                    location = GrinLocation(1, 1), value = 'START')
            self.colon = GrinToken(kind = GrinTokenKind.COLON, text = ':',
                                   location = GrinLocation(1, 5), value = None)
            self.token2 = GrinToken(kind = GrinTokenKind.PRINT, text = 'PRINT',
                                    location = GrinLocation(1, 6), value = None)

        def test_map_labels_finds_label(self):
            state = InterpreterState()
            state._lines = [[self.token1, self.colon, self.token2]]
            labels = state._map_labels()
            self.assertIn('START', labels)
            self.assertEqual(labels['START'], 0)

        def test_map_labels_ignores_lines_without_labels(self):
            state = InterpreterState()
            state._lines = [[self.token2]]
            labels = state._map_labels()
            self.assertEqual(labels, {})

        def test_label_line_returns_correct_line(self):
            state = InterpreterState()
            state._labels = {'main': 2}
            self.assertEqual(state.label_line('main'), 2)

        def test_label_line_nonexistent_returns_none(self):
            state = InterpreterState()
            state._labels = {}
            self.assertIsNone(state.label_line('missing'))


    class TestJumpBoundaries(unittest.TestCase):
        def test_jump_to_first_line(self):
            state = InterpreterState()
            state._lines = [None] * 5
            state.jump_to_line(1)
            self.assertEqual(state.current_line(), 0)

        def test_jump_to_last_line(self):
            state = InterpreterState()
            state._lines = [None] * 5
            state.jump_to_line(5)
            self.assertEqual(state.current_line(), 4)

        def test_end_prevents_further_execution(self):
            state = InterpreterState()
            state._lines = [None] * 5
            state.end()
            state.go_to_next_line()
            self.assertTrue(state.is_finished())

if __name__ == '__main__':
    unittest.main()