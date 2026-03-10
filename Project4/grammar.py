import random

class Grammar:
    def __init__(self, start_variable: VariableSymbol):
        self._start_variable = start_variable
        self.rules = dict()

    def print_rules(self):
        for variable, rule in self.rules.items():
            print('Rule:', variable, end='')
            for option in rule.options():
                print('Option: ', end='')
                for symbol in option.symbols():
                    print(symbol, end=', ')
                print()
            print()

    def generate(self):
        rule = self.rules[self._start_variable]
        yield from rule.generate(self.rules)

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

    def variable_id(self):
        print(self._variable_id)

    def generate(self, rules):
        yield from rules[self].generate(rules)

class Rule:
    def __init__(self):
        self._options = []

    def add_option(self, weight, option):
        for i in range(weight):
            self._options.append(option)

    def options(self):
        return self._options

    def generate(self, rules):
        num_options = len(self._options) - 1
        random_num = random.randint(0, num_options)
        random_option = self._options[random_num]
        yield from random_option.generate(rules)

class Option:
    def __init__(self, symbols):
        self._symbols = symbols

    def symbols(self):
        return self._symbols

    def generate(self, rules):
        for symbol in self._symbols:
            if isinstance(symbol, VariableSymbol):
                yield from symbol.generate(rules)
            else:
                yield from symbol.generate()

class TerminalSymbol:
    def __init__(self, text):
        self._text = text

    def __str__(self):
        return self._text

    def __repr__(self):
        return self._text

    def generate(self):
        yield self._text