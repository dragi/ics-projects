from randomizer import Randomizer, FakeRandomizer

class Grammar:
    def __init__(self, start_variable: VariableSymbol):
        self._start_variable = start_variable
        self.rules = dict()

    def generate(self, randomizer=None):
        if randomizer is None:
            randomizer = Randomizer()
        rule = self.rules[self._start_variable]
        yield from rule.generate(self.rules, randomizer)

class VariableSymbol:
    def __init__(self, variable_id):
        self._variable_id = variable_id

    def __eq__(self, other):
        if not isinstance(other, VariableSymbol):
            return NotImplemented
        return self._variable_id == other._variable_id

    def __hash__(self):
        return hash(self._variable_id)

    def __str__(self):
        return self._variable_id

    def __repr__(self):
        return self._variable_id

    def generate(self, rules, randomizer):
        yield from rules[self].generate(rules, randomizer)

class Rule:
    def __init__(self):
        self._options = []

    def add_option(self, weight, option):
        for i in range(weight):
            self._options.append(option)

    def generate(self, rules, randomizer):
        num_options = len(self._options) - 1
        random_num = randomizer.randint(0, num_options)
        random_option = self._options[random_num]
        yield from random_option.generate(rules, randomizer)

class Option:
    def __init__(self, symbols):
        self._symbols = symbols

    def generate(self, rules, randomizer):
        for symbol in self._symbols:
            yield from symbol.generate(rules, randomizer)

class TerminalSymbol:
    def __init__(self, text):
        self._text = text

    def __str__(self):
        return self._text

    def __repr__(self):
        return self._text

    def generate(self, rules, randomizer):
        yield self._text