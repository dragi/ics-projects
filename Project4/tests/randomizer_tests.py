from grammar import Grammar, VariableSymbol
from randomizer import FakeRandomizer
from input import build_grammar
import unittest

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

    def test_variable_called_twice(self):
        grammar = Grammar(VariableSymbol('HowIsBoo'))
        lines = [
            '{', 'HowIsBoo', '1 Boo is [Adjective] and [Adjective] today', '}',
            '{', 'Adjective', '1 happy', '1 perfect', '}',
        ]
        build_grammar(grammar, lines, 0)

        result = list(grammar.generate(FakeRandomizer([0, 0, 1])))
        self.assertEqual(result, ['Boo', 'is', 'happy', 'and', 'perfect', 'today'])