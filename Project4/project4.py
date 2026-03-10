# project4.py
#
# ICS 33 Winter 2026
# Project 4: Still Looking for Something

from input import read_input, build_grammar

def main() -> None:
    grammar, lines, num_sentences = read_input()
    build_grammar(grammar, lines, num_sentences)

if __name__ == '__main__':
    main()