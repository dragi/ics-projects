# test_queens.py
#
# ICS 33 Winter 2026
# Project 0: History of Modern
#
# Unit tests for the QueensState class in "queens.py".
#
# Docstrings are not required in your unit tests, though each test does need to have
# a name that clearly indicates its purpose.  Notice, for example, that the provided
# test method is named "test_queen_count_is_zero_initially" instead of something generic
# like "test_queen_count", since it doesn't entirely test the "queen_count" method,
# but instead focuses on just one aspect of how it behaves.  You'll want to do likewise.


from queens import QueensState
from queens import DuplicateQueenError
from queens import Position
import unittest



class TestQueensState(unittest.TestCase):
    def test_queen_count_is_zero_initially(self):
        state = QueensState(8, 8)
        self.assertEqual(state.queen_count(), 0)

    def test_queen_count_increases_if_there_are_queens(self):
        state = QueensState(8, 8, (Position(1, 1), Position(3, 1)))
        self.assertEqual(state.queen_count(), 2)

    def test_has_queen_is_true_if_queen_occupies_given_position(self):
        state = QueensState(4, 4, (Position(2, 2), Position(1, 0)))
        self.assertEqual(state.has_queen(Position(1,0)), True)

    def test_has_queen_is_false_if_queen_doesnt_occupy_given_position(self):
        state = QueensState(6, 10, (Position(4, 3), Position(3, 1)))
        self.assertEqual(state.has_queen(Position(2,2)), False)

    def test_duplicate_positions_causes_error(self):
        with self.assertRaises(DuplicateQueenError):
            state = QueensState(5, 5, (Position(3, 3), Position(2, 1), Position(3, 3)))

    def test_out_of_bounds_positions_causes_error(self):
        with self.assertRaises(IndexError):
            state = QueensState(2, 2, (Position(1, 0), Position(2, 2)))

    def test_with_queens_added_works_with_valid_input(self):
        state = QueensState(4, 5, (Position(2, 0), Position(3, 0)))
        new_state = state.with_queens_added([Position(1,0), Position(1,1)])
        positions = [Position(2, 0), Position(3, 0), Position(1,0), Position(1,1)]
        self.assertEqual(sorted(new_state.queens()), sorted(positions))

    def test_with_queens_added_causes_error_with_invalid_input(self):
        with self.assertRaises(DuplicateQueenError):
            state = QueensState(4, 4, (Position(2, 1), Position(3, 2)))
            new_state = state.with_queens_added([Position(2,0), Position(3,2)])


if __name__ == '__main__':
    unittest.main()
