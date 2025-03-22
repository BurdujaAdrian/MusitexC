#from lexer import Tokenizer
#from parser import Parser
import sys
#from new_parser import *
from ai_ast import *

def main():
    # Sample input if no file is provided
    sample_input = \
"""
#comment
title:"testing parse"
--- 
tempo: 480
piano : do re mi
"""

    # Get source code from file or use sample
    if len(sys.argv) > 1:
        try:
            with open(sys.argv[1], 'r') as file:
                source_code = file.read()
        except FileNotFoundError:
            print(f"Error: File {sys.argv[1]} not found.")
            return
    else:
        source_code = sample_input

    # Tokenize the source code
    tokenizer = Tokenizer(source_code)
    tokens = tokenizer.tokenize()

    # Print the tokens
    # print("=== Tokens ===")
    # for token in tokens:
    #    print(token)
       # # Parse the tokens
    # parser = Parser(tokens)

    x = parse_music(tokens)
 #   print (parse_music(tokens))
    #ast = parser.parse()
#    print(x)

    # Print the AST
    # print("=== AST ===")
    print(traverse_ast(x))

if __name__ == "__main__":
    main()


