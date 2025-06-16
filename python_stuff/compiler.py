from new_parser import Parser
from lexer import Tokenizer
from simplify import * 
from ast_ import traverse_ast
from midigen import *
import sys
import os

def main(input = None):
    # Define the path to the public directory
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.'))
    public_dir = os.path.join(base_dir, 'public')
    os.makedirs(public_dir, exist_ok=True)
    print(public_dir)


    if input is not None and len(sys.argv) < 2:
        file_name = "tex.mtex"
        source = input
        print("No input file provided")
    else:
        file_name = sys.argv[1]
        with open(file_name) as f:
            source = f.read()

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
|
| Tip: write the name of an instruments, ":" then the notes you want to play in the same line
|
| Example: 
|
| piano: do re mi fa sol la si do

""")
        return

    resolve_repeats(ast)
    print(traverse_ast(ast,0))
    flatten_expr_group(ast)
    print(traverse_ast(ast,0))
    resolve_macros(ast)
    print(traverse_ast(ast,0))
    output = ""
    try:
        output = sys.argv[2]
    except:
        output = file_name.split(".")[1][1:] + ".mid"
        # files are in the form ./twinkle.midi , after splitting /twinkle, skip / with [1:]
    midi_path = os.path.join(public_dir, output)
    gen_midi(ast, midi_path)

    # error checking
    if len(ast.err_list) > 0:
        print("Compilation errors:")
        for err in ast.err_list:
            print(err)
        return

    pass

if __name__ == "__main__":
    main()
