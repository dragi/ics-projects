from pathlib import Path
from grammar import Grammar, VariableSymbol, Rule, Option, TerminalSymbol
from input_reader import InputReader

def read_input(reader = None) -> tuple[Grammar, list[str], int]:
    """Read input and file to produce a Grammar, its lines, and sentence count."""
    if reader is None:
        reader = InputReader()

    file_path = Path(reader.read_line())
    num_sentences = int(reader.read_line())
    starting_variable = VariableSymbol(reader.read_line())
    grammar = Grammar(starting_variable)

    with open(file_path, 'r') as f:
        lines = f.readlines()

    return grammar, lines, num_sentences

def build_grammar(grammar: Grammar, lines: list[str], num_sentences: int) -> None:
    """Parse rules from lines and print generated sentences."""
    for i in range(len(lines)):
        if len(lines[i].strip()) == 0:
            continue

        if lines[i].strip()[0] == '{':
            add_rule(lines, i+1, grammar)

    print_grammar(grammar, num_sentences)

def add_rule(lines: list[str], line_number: int, grammar: Grammar) -> None:
    """Parse one rule block and register it in the grammar."""
    variable_id = lines[line_number].strip()
    variable = VariableSymbol(variable_id)
    rule = Rule()

    i = line_number + 1
    while lines[i].strip() != '}':
        symbols = lines[i].split()
        weight = int(symbols[0])
        symbols.pop(0)

        for j in range(len(symbols)):
            if symbols[j][0] == '[':
                symbols[j] = VariableSymbol(symbols[j].strip('[]'))
            else:
                symbols[j] = TerminalSymbol(symbols[j])

        option = Option(symbols)
        rule.add_option(weight, option)

        i += 1

    grammar.insert_rule(variable, rule)

def print_grammar(grammar: Grammar, num_times: int) -> None:
    """Print num_times randomly generated sentences."""
    for i in range(num_times):
        sentence = list(grammar.generate())
        print(' '.join(sentence))