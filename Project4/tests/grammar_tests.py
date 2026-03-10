from grammar import Grammar, VariableSymbol, FakeRandomizer
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

class TestFakeRandomizer(unittest.TestCase):
    def test_picks_first_option(self):
        grammar = Grammar(VariableSymbol('HowIsBoo'))
        lines = [
            '{', 'HowIsBoo', '1 Boo is [Adjective] today', '}',
            '{', 'Adjective', '3 happy', '3 perfect', '1 relaxing', '}',
        ]
        build_grammar(grammar, lines, 0)

        result = list(grammar.generate(FakeRandomizer([0, 0])))
        self.assertEqual(result, ['Boo', 'is', 'happy', 'today'])

    def test_picks_last_option(self):
        grammar = Grammar(VariableSymbol('HowIsBoo'))
        lines = [
            '{', 'HowIsBoo', '1 Boo is [Adjective] today', '}',
            '{', 'Adjective', '3 happy', '3 perfect', '1 relaxing', '}',
        ]
        build_grammar(grammar, lines, 0)

        result = list(grammar.generate(FakeRandomizer([0, 6])))
        self.assertEqual(result, ['Boo', 'is', 'relaxing', 'today'])

    def test_picks_middle_option(self):
        grammar = Grammar(VariableSymbol('HowIsBoo'))
        lines = [
            '{', 'HowIsBoo', '1 Boo is [Adjective] today', '}',
            '{', 'Adjective', '3 happy', '3 perfect', '1 relaxing', '}',
        ]
        build_grammar(grammar, lines, 0)

        result = list(grammar.generate(FakeRandomizer([0, 4])))
        self.assertEqual(result, ['Boo', 'is', 'perfect', 'today'])

    def test_nested_variables_controlled(self):
        grammar = Grammar(VariableSymbol('HowIsBoo'))
        lines = [
            '{', 'HowIsBoo', '1 Boo is [Mood] today', '}',
            '{', 'Mood', '1 very [Adjective]', '1 somewhat [Adjective]', '}',
            '{', 'Adjective', '1 happy', '1 fulfilled', '}',
        ]
        build_grammar(grammar, lines, 0)

        result = list(grammar.generate(FakeRandomizer([0, 1, 1])))
        self.assertEqual(result, ['Boo', 'is', 'somewhat', 'fulfilled', 'today'])

if __name__ == '__main__':
    unittest.main()