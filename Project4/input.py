from grammar import Grammar, VariableSymbol, Rule, Option, TerminalSymbol

def read_input():
    user_input = input()
    user_input.splitlines()
    file_path = user_input[0]
    num_sentences = user_input[1]
    starting_variable_id = user_input[2]

    starting_variable = VariableSymbol(starting_variable_id)
    grammar = Grammar(starting_variable)
