from grammar import Grammar, VariableSymbol
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

    def test_multiple_options(self):
        grammar = Grammar(VariableSymbol('HowIsBoo'))
        lines = [
            '{', 'HowIsBoo', '1 Boo is [Adjective] today', '}',
            '{', 'Adjective', '3 happy', '3 perfect', '1 relaxing', '1 fulfilled', '2 excited', '}'
        ]
        num_sentences = 20

        f = io.StringIO()
        with redirect_stdout(f):
            build_grammar(grammar, lines, num_sentences)

        valid = {'Boo is happy today', 'Boo is perfect today', 'Boo is relaxing today',
                 'Boo is fulfilled today', 'Boo is excited today'}
        for line in f.getvalue().strip().split('\n'):
            self.assertIn(line, valid)

    def test_comments_are_ignored(self):
        grammar = Grammar(VariableSymbol('HowIsBoo'))
        lines = [
            'comment',
            '{', 'HowIsBoo', '1 Boo is relaxing today', '}',
            'comment'
        ]
        num_sentences = 1

        f = io.StringIO()
        with redirect_stdout(f):
            build_grammar(grammar, lines, num_sentences)

        self.assertEqual(f.getvalue(), 'Boo is relaxing today\n')

    def test_num_lines(self):
        grammar = Grammar(VariableSymbol('HowIsBoo'))
        lines = ['{', 'HowIsBoo', '1 Boo is excited today', '}']
        num_sentences = 7

        f = io.StringIO()
        with redirect_stdout(f):
            build_grammar(grammar, lines, num_sentences)

        self.assertEqual(len(f.getvalue().strip().split('\n')), 7)

    def test_zero_sentences(self):
        grammar = Grammar(VariableSymbol('HowIsBoo'))
        lines = ['{', 'HowIsBoo', '1 Boo is happy today', '}']

        f = io.StringIO()
        with redirect_stdout(f):
            build_grammar(grammar, lines, 0)

        self.assertEqual(f.getvalue(), '')

    def test_multiple_variables_in_option(self):
        grammar = Grammar(VariableSymbol('HowIsBoo'))
        lines = [
            '{', 'HowIsBoo', '1 [Subject] [Verb] [Adjective]', '}',
            '{', 'Subject', '1 Boo', '}',
            '{', 'Verb', '1 is', '}',
            '{', 'Adjective', '1 happy', '}',
        ]

        f = io.StringIO()
        with redirect_stdout(f):
            build_grammar(grammar, lines, 1)

        self.assertEqual(f.getvalue(), 'Boo is happy\n')

    def test_same_variable_in_option(self):
        grammar = Grammar(VariableSymbol('HowIsBoo'))
        lines = [
            '{', 'HowIsBoo', '1 Boo is [Adjective] and [Adjective] today', '}',
            '{', 'Adjective', '1 happy', '}',
        ]

        f = io.StringIO()
        with redirect_stdout(f):
            build_grammar(grammar, lines, 1)

        self.assertEqual(f.getvalue(), 'Boo is happy and happy today\n')

    def test_empty_lines_ignored(self):
        grammar = Grammar(VariableSymbol('HowIsBoo'))
        lines = [
            '',
            '{', 'HowIsBoo', '1 Boo is happy', '}',
            '',
            '{', 'Adjective', '1 happy', '}',
            ''
        ]
        num_sentences = 1

        f = io.StringIO()
        with redirect_stdout(f):
            build_grammar(grammar, lines, num_sentences)

        self.assertEqual(f.getvalue(), 'Boo is happy\n')

    def test_duplicate_variable_overwrites(self):
        grammar = Grammar(VariableSymbol('HowIsBoo'))
        lines = [
            '{', 'HowIsBoo', '1 sad', '}',
            '{', 'HowIsBoo', '1 happy', '}',
        ]
        num_sentences = 1

        f = io.StringIO()
        with redirect_stdout(f):
            build_grammar(grammar, lines, num_sentences)

        self.assertEqual(f.getvalue(), 'happy\n')

    def test_zero_weight_option(self):
        grammar = Grammar(VariableSymbol('HowIsBoo'))
        lines = [
            '{', 'HowIsBoo', '0 sad', '10 happy', '}',
        ]
        num_sentences = 20

        f = io.StringIO()
        with redirect_stdout(f):
            build_grammar(grammar, lines, num_sentences)

        results = f.getvalue().strip().split('\n')
        self.assertNotIn('sad', results)
        self.assertTrue(all(r == 'happy' for r in results))

    def test_deeply_nested_variables(self):
        grammar = Grammar(VariableSymbol('A'))
        lines = [
            '{', 'A', '1 [B]', '}',
            '{', 'B', '1 [C]', '}',
            '{', 'C', '1 [D]', '}',
            '{', 'D', '1 test', '}',
        ]
        num_sentences = 1

        f = io.StringIO()
        with redirect_stdout(f):
            build_grammar(grammar, lines, num_sentences)

        self.assertEqual(f.getvalue(), 'test\n')

if __name__ == '__main__':
    unittest.main()