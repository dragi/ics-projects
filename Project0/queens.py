# queens.py
#
# ICS 33 Winter 2026
# Project 0: History of Modern
#
# A module containing tools that could assist in solving variants of the
# well-known "n-queens" problem.  Note that we're only implementing one part
# of the problem: immutably managing the "state" of the board (i.e., which
# queens are arranged in which cells).  The rest of the problem -- determining
# a valid solution for it -- is not our focus here.
#
# Your goal is to complete the QueensState class described below, though
# you'll need to build it incrementally, as well as test it incrementally by
# writing unit tests in test_queens.py.  Make sure you've read the project
# write-up before you proceed, as it will explain the requirements around
# following (and documenting) an incremental process of solving this problem.
#
# DO NOT MODIFY THE Position NAMEDTUPLE OR THE PROVIDED EXCEPTION CLASSES.

from collections import namedtuple
from typing import Self



Position = namedtuple('Position', ['row', 'column'])

# Ordinarily, we would write docstrings within classes or their methods.
# Since a namedtuple builds those classes and methods for us, we instead
# add the documentation by hand afterward.
Position.__doc__ = 'A position on a chessboard, specified by zero-based row and column numbers.'
Position.row.__doc__ = 'A zero-based row number'
Position.column.__doc__ = 'A zero-based column number'



class DuplicateQueenError(Exception):
    """An exception indicating an attempt to add a queen where one is already present."""

    def __init__(self, position: Position):
        """Initializes the exception, given a position where the duplicate queen exists."""
        self._position = position

    def __str__(self) -> str:
        return f'duplicate queen in row {self._position.row} column {self._position.column}'


class MissingQueenError(Exception):
    """An exception indicating an attempt to remove a queen where one is not present."""

    def __init__(self, position: Position):
        """Initializes the exception, given a position where a queen is missing."""
        self._position = position

    def __str__(self) -> str:
        return f'missing queen in row {self._position.row} column {self._position.column}'


class QueensState:
    """Immutably represents the state of a chessboard being used to assist in
    solving the n-queens problem."""

    def __init__(self, rows: int, columns: int, queens: tuple[Position, ...] = ()):
        """Initializes the chessboard to have the given numbers of rows and columns,
        with no queens occupying any of its cells unless specified."""
        self._rows = rows
        self._columns = columns
        self._queens = []

        for queen in queens:
            if self.has_queen(queen):
                raise DuplicateQueenError(queen)
            elif queen.row >= self._rows:
                raise IndexError(f'Specified row ({queen.row}) is out of range.')
            elif queen.column >= self._columns:
                raise IndexError(f'Specified column ({queen.column}) is out of range.')
            else:
                self._queens.append(queen)


    def queen_count(self) -> int:
        """Returns the number of queens on the chessboard."""
        return len(self._queens)


    def queens(self) -> list[Position]:
        """Returns a list of the positions in which queens appear on the chessboard,
        arranged in no particular order."""
        return list(self._queens)


    def has_queen(self, position: Position) -> bool:
        """Returns True if a queen occupies the given position on the chessboard, or
        False otherwise."""
        return position in self._queens


    def any_queens_unsafe(self) -> bool:
        """Returns True if any queens on the chessboard are unsafe (i.e., they can
        be captured by at least one other queen on the chessboard), or False otherwise."""
        same_row = self._check_across(self._rows, self._columns, True)
        same_col = self._check_across(self._columns, self._rows, False)
        same_diagonal = self._check_diagonals(self._rows, self._columns)
        return same_row or same_col or same_diagonal


    def with_queens_added(self, positions: list[Position]) -> Self:
        """Builds a new QueensState with queens added in the given positions,
        without modifying 'self' in any way.  Raises a DuplicateQueenError when
        there is already a queen in at least one of the given positions."""
        new_positions = list(positions)
        new_positions.extend(self._queens)
        new_positions = tuple(new_positions)
        return QueensState(self._rows, self._columns, new_positions)


    def with_queens_removed(self, positions: list[Position]) -> Self:
        """Builds a new QueensState with queens removed from the given positions,
        without modifying 'self' in any way.  Raises a MissingQueenError when there
        is no queen in at least one of the given positions."""
        new_positions = []
        for position in positions:
            if not self.has_queen(position):
                raise MissingQueenError(position)

        for queen in self._queens:
            if queen not in positions:
                new_positions.append(queen)

        return QueensState(self._rows, self._columns, tuple(new_positions))

    def _check_across(self, x: int, y: int, check_rows: bool) -> bool:
        """Helper method to check across either each row or column of the board
        for multiple queens. If multiple are found, return True, while if they are not,
        return False."""
        for i in range(x):
            count = 0
            for j in range(y):
                position = Position(j, i)
                if check_rows:
                    position = Position(i, j)
                if self.has_queen(position):
                    count += 1
            if count > 1:
                return True
        return False

    def _check_diagonals(self, rows: int, cols: int) -> bool:
        """Helper method to check across each diagonal of the board
        for multiple queens. If multiple are found, return True, while if they are not,
        return False."""
        for start_col in range(cols):
            count = 0
            row, col = 0, start_col
            while row < rows and col < cols:
                if self.has_queen(Position(row, col)):
                    count += 1
                row += 1
                col += 1
            if count > 1:
                return True

        for start_row in range(1, rows):
            count = 0
            row, col = start_row, 0
            while row < rows and col < cols:
                if self.has_queen(Position(row, col)):
                    count += 1
                row += 1
                col += 1
            if count > 1:
                return True

        for start_col in range(cols):
            count = 0
            row, col = 0, start_col
            while row < rows and col >= 0:
                if self.has_queen(Position(row, col)):
                    count += 1
                row += 1
                col -= 1
            if count > 1:
                return True

        return False