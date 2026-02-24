# project3.py
#
# ICS 33 Winter 2026
# Project 3: Why Not Smile?
#
# The main module that executes your Grin interpreter.
#
# WHAT YOU NEED TO DO: You'll need to implement the outermost shell of your
# program here, but consider how you can keep this part as simple as possible,
# offloading as much of the complexity as you can into additional modules in
# the 'grin' package, isolated in a way that allows you to unit test them.

import grin
from grin.statement import make_statement

def main() -> None:
    state = grin.InterpreterState()
    state.read_lines()
    statements = [make_statement(tokens) for tokens in state.lines()]
    while not state.is_finished():
        line = state.current_line()
        statements[line].execute(state)
        state.go_to_next_line()


if __name__ == '__main__':
    main()
