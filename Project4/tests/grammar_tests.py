from grammar import Grammar, VariableSymbol, Rule, Option, TerminalSymbol
from input import build_grammar
import unittest
import io
from contextlib import redirect_stdout

class TestGrammar(unittest.TestCase):
    def test_single_terminal(self):
        grammar = Grammar(VariableSymbol('HowIsBoo'))
        lines = ['{', 'HowIsBoo', '1 Good', '}']
        num_sentences = 1

        f = io.StringIO()
        with redirect_stdout(f):
            build_grammar(grammar, lines, num_sentences)

        self.assertEqual(f.getvalue(), 'Good\n')

if __name__ == '__main__':
    unittest.main()