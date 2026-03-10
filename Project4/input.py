from pathlib import Path
from grammar import Grammar, VariableSymbol, Rule, Option, TerminalSymbol

def read_input() -> None:
    file_path = Path(input().strip())
    num_sentences = int(input().strip())
    starting_variable = VariableSymbol(input().strip())
    grammar = Grammar(starting_variable)

    lines = []
    with open(file_path, 'r') as f:
        lines = f.readlines()

    for i in range(len(lines)):
        if len(lines[i].strip()) == 0:
            continue

        if lines[i].strip()[0] == '{':
            add_rule(lines, i+1, grammar)

    grammar.print_grammar()
    generate_grammar(grammar, num_sentences)

def add_rule(lines: list[str], line_number: int, grammar: Grammar) -> None:
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

        symbols = tuple(symbols)
        option = Option(symbols)
        rule.add_option(weight, option)

        i += 1

    grammar.rules[variable] = rule

def generate_grammar(grammar, num_times):
    for i in range(num_times):
        sentence = list(grammar.generate())
        for symbol in sentence:
            print(symbol, end=' ')
        print()