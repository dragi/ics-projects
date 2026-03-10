import random

class Grammar:
    def __init__(self, start_variable: VariableSymbol):
        self._start_variable = start_variable
        self.rules = dict()

    def print_grammar(self):
        for variable, rule in self.rules.items():
            print('Rule:', variable, end='')
            for option in rule.options():
                print('Option: ', end='')
                for symbol in option.symbols():
                    print(symbol, end=', ')
                print()
            print()

    def generate(self):
        print(self.rules.keys(), end = ', ')
        rule = self.rules[self._start_variable]
        yield rule.generate(self.rules)

class VariableSymbol:
    def __init__(self, variable_id):
        self._variable_id = variable_id

    def variable_id(self):
        print(self._variable_id)

    def __str__(self):
        return self._variable_id

    def generate(self, rules):
        yield rules[self].generate(rules)

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
        yield random_option.generate(rules)

class Option:
    def __init__(self, symbols):
        self._symbols = symbols

    def symbols(self):
        return self._symbols

    def generate(self, rules):
        output = []
        for symbol in self._symbols:
            if isinstance(symbol, VariableSymbol):
                variable_symbol = symbol.generate(rules)
                output.extend(variable_symbol)
            else:
                terminal_symbol = symbol.generate()
                output.append(terminal_symbol)
        yield output

class TerminalSymbol:
    def __init__(self, text):
        self._text = text

    def __str__(self):
        return self._text

    def generate(self):
        yield self._text