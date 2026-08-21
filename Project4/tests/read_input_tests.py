from grammar import Grammar, VariableSymbol
from input import read_input
from input_reader import FakeInputReader
import unittest
import os

TEMP_FILE = 'temp_grammar_file.txt'

class TestReadInput(unittest.TestCase):
    def setUp(self):
        with open(TEMP_FILE, 'w') as f:
            f.write('{\nS\n1 hello\n}\n')

    def tearDown(self):
        os.remove(TEMP_FILE)

    def test_returns_grammar_instance(self):
        reader = FakeInputReader([TEMP_FILE, '1', 'S'])
        result = read_input(reader)
        grammar = result[0]
        self.assertIsInstance(grammar, Grammar)

    def test_returns_correct_num_sentences(self):
        reader = FakeInputReader([TEMP_FILE, '5', 'S'])
        result = read_input(reader)
        num_sentences = result[2]
        self.assertEqual(num_sentences, 5)

    def test_returns_correct_start_variable(self):
        with open(TEMP_FILE, 'w') as f:
            f.write('{\nHowIsBoo\n1 hello\n}\n')
        reader = FakeInputReader([TEMP_FILE, '1', 'HowIsBoo'])
        result = read_input(reader)
        grammar = result[0]
        self.assertEqual(grammar._start_variable, VariableSymbol('HowIsBoo'))

    def test_returns_file_lines(self):
        reader = FakeInputReader([TEMP_FILE, '1', 'S'])
        result = read_input(reader)
        lines = result[1]
        stripped = [line.strip() for line in lines]
        self.assertEqual(stripped, ['{', 'S', '1 hello', '}'])

    def test_large_num_sentences(self):
        reader = FakeInputReader([TEMP_FILE, '1000', 'S'])
        result = read_input(reader)
        num_sentences = result[2]
        self.assertEqual(num_sentences, 1000)

    def test_multiline_grammar_file(self):
        with open(TEMP_FILE, 'w') as f:
            f.write('{\nS\n1 [A]\n}\n{\nA\n1 world\n}\n')
        reader = FakeInputReader([TEMP_FILE, '1', 'S'])
        result = read_input(reader)
        lines = result[1]
        stripped = [line.strip() for line in lines]
        self.assertIn('A', stripped)
        self.assertIn('1 world', stripped)

if __name__ == '__main__':
    unittest.main()