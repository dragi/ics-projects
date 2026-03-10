from grammar import Grammar, VariableSymbol, Rule, Option, TerminalSymbol
from input import build_grammar
import unittest
import io
from contextlib import redirect_stdout

class TestGrammar(unittest.TestCase):
    def test_one_terminal_in_one_option(self):
        grammar = Grammar(VariableSymbol('HowIsBoo'))
        lines = ['{', 'HowIsBoo', '1 Good', '}']
        num_sentences = 1

        f = io.StringIO()
        with redirect_stdout(f):
            build_grammar(grammar, lines, num_sentences)

        self.assertEqual(f.getvalue(), 'Good\n')

    def test_multiple_terminals_in_one_option(self):
        grammar = Grammar(VariableSymbol('HowIsBoo'))
        lines = ['{', 'HowIsBoo', '1 Boo is happy', '}']
        num_sentences = 1

        f = io.StringIO()
        with redirect_stdout(f):
            build_grammar(grammar, lines, num_sentences)

        self.assertEqual(f.getvalue(), 'Boo is happy\n')

    def test_multiple_sentences(self):
        grammar = Grammar(VariableSymbol('HowIsBoo'))
        lines = ['{', 'HowIsBoo', '1 Boo is happy today', '}']
        num_sentences = 3

        f = io.StringIO()
        with redirect_stdout(f):
            build_grammar(grammar, lines, num_sentences)

        self.assertEqual(f.getvalue(), 'Boo is happy today\nBoo is happy today\nBoo is happy today\n')

    def test_two_variables(self):
        grammar = Grammar(VariableSymbol('HowIsBoo'))
        lines = [
            '{', 'HowIsBoo', '1 Boo is [Adjective] today', '}',
            '{', 'Adjective', '1 happy', '}'
        ]
        num_sentences = 1

        f = io.StringIO()
        with redirect_stdout(f):
            build_grammar(grammar, lines, num_sentences)

        self.assertEqual(f.getvalue(), 'Boo is happy today\n')

    def test_three_variables(self):
        grammar = Grammar(VariableSymbol('HowIsBoo'))
        lines = [
            '{', 'HowIsBoo', '1 Boo is [Mood] today', '}',
            '{', 'Mood', '1 [Adjective]', '}',
            '{', 'Adjective', '1 fulfilled', '}'
        ]
        num_sentences = 1

        f = io.StringIO()
        with redirect_stdout(f):
            build_grammar(grammar, lines, num_sentences)

        self.assertEqual(f.getvalue(), 'Boo is fulfilled today\n')

if __name__ == '__main__':
    unittest.main()