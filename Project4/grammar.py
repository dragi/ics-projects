from randomizer import Randomizer

class Grammar:
    """Holds rules and generates strings from a start variable."""
    def __init__(self, start_variable: VariableSymbol) -> None:
        self._start_variable = start_variable
        self._rules = dict()

    def insert_rule(self, variable: VariableSymbol, rule: Rule) -> None:
        """Register a rule for the given variable symbol."""
        self._rules[variable] = rule

    def generate(self, randomizer: Randomizer = None):
        """Yield a randomly generated string starting from start variable."""
        if randomizer is None:
            randomizer = Randomizer()
        rule = self._rules[self._start_variable]
        yield from rule.generate(self._rules, randomizer)

class VariableSymbol:
    """Represents a named non-terminal symbol in a grammar."""
    def __init__(self, variable_id: str) -> None:
        """Store the string identifier for this variable symbol."""
        self._variable_id = variable_id

    def __eq__(self, other: object) -> bool:
        """Return True if both symbols share the same identifier."""
        if not isinstance(other, VariableSymbol):
            return NotImplemented
        return self._variable_id == other._variable_id

    def __hash__(self) -> int:
        """Return a hash based on the variable identifier."""
        return hash(self._variable_id)

    def __str__(self) -> str:
        """Return the variable identifier as a string."""
        return self._variable_id

    def __repr__(self) -> str:
        """Return the variable identifier as its representation."""
        return self._variable_id

    def generate(self, rules: dict, randomizer: Randomizer):
        """Expand this variable by delegating to its rule in the rules dictionary."""
        yield from rules[self].generate(rules, randomizer)

class Rule:
    """Represents a rule as a weighted list of options."""
    def __init__(self) -> None:
        """Initialize an empty list of options."""
        self._options = []

    def add_option(self, weight: int, option: Option) -> None:
        """Append an option to the list a number of times equal to its weight."""
        for i in range(weight):
            self._options.append(option)

    def generate(self, rules: dict, randomizer: Randomizer):
        """Randomly select one option and yield its generated output."""
        num_options = len(self._options) - 1
        random_num = randomizer.randint(0, num_options)
        random_option = self._options[random_num]
        yield from random_option.generate(rules, randomizer)

class Option:
    """Represents a single alternative as an ordered list of symbols."""
    def __init__(self, symbols: list) -> None:
        """Store the sequence of symbols that make up this option."""
        self._symbols = symbols

    def generate(self, rules: dict, randomizer: Randomizer):
        """Yield output from each symbol in sequence."""
        for symbol in self._symbols:
            yield from symbol.generate(rules, randomizer)

class TerminalSymbol:
    """Represents a literal string token that cannot be expanded further."""
    def __init__(self, text: str) -> None:
        """Store the terminal text value."""
        self._text = text

    def __str__(self) -> str:
        """Return the terminal text as a string."""
        return self._text

    def __repr__(self) -> str:
        """Return the terminal text as its representation."""
        return self._text

    def generate(self, rules: dict, randomizer: Randomizer):
        """Yield the terminal text as the final generated output."""
        yield self._text