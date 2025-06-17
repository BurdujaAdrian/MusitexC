from new_parser import Parser
from lexer import Tokenizer
from simplify import *
from ai_ast import traverse_ast
from midigen import *
import sys


def main():
    file_name = sys.argv[1]

    with open(file_name) as f:
        source = f.read()

    print(source)

    tokenizer = Tokenizer(source)
    tokens = tokenizer.tokenize()

    parser = Parser(tokens)
    ast = parser.parse()

    # sanity check
    count = 0
    for track in ast.tracks:
        for mov in track.movements:
            count += len(mov.expressions)

    if count == 0:
        print("""Compilation error: All tracks cannot be empty.

Tip: write the name of an instruments, ":" then the notes you want to play in the same line

Example:

piano: do re mi fa sol la si do

""")
        return

    resolve_repeats(ast)
    print(traverse_ast(ast, 0))
    flatten_expr_group(ast)
    print(traverse_ast(ast, 0))
    resolve_macros(ast)
    print(traverse_ast(ast, 0))
#
    output = ""
    try:
        output = sys.argv[2]
    except:
        output = file_name.split(".")[0][0:] + ".mid"
        print(output)
#         # files are in the form ./twinkle.midi , after splitting /twinkle, skip / with [1:]
    gen_midi(ast, output)
#
#     # error checking
    if len(ast.err_list) > 0:
        print("Compilation errors:")
        for err in ast.err_list:
            print(err)
        return

    pass
#
#
if __name__ == "__main__":
    main()
