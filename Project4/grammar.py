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

class VariableSymbol:
    def __init__(self, variable_id):
        self._variable_id = variable_id

    def variable_id(self):
        print(self._variable_id)

    def __str__(self):
        return f'Variable Symbol: {self._variable_id}'

class Rule:
    def __init__(self):
        self._options = []

    def add_option(self, weight, option):
        for i in range(weight):
            self._options.append(option)

    def options(self):
        return self._options

class Option:
    def __init__(self, symbols):
        self._symbols = symbols

    def symbols(self):
        return self._symbols

class TerminalSymbol:
    def __init__(self, text):
        self._text = text

    def __str__(self):
        return f'Terminal Symbol: {self._text}'