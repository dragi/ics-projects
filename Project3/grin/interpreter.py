from grin.parsing import parse

def read_lines():
    lines = []
    line = input().strip()

    while len(line) > 0 and line != '.':
        lines.append(line)
        line = input().strip()

__all__ = [
    read_lines.__name__
]