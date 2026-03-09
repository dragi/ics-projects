class Grammar:
    def __init__(self, start_variable: VariableSymbol):
        self._start_variable = start_variable
        self._rules = dict()

class VariableSymbol:
    def __init__(self, variable_id):
        self._variable_id = variable_id

class Rule:
    pass

class Option:
    def __init__(self, weight):
        self._weight = weight

class TerminalSymbol:
    pass