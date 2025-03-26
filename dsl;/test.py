# Example usage with sample input
from lexer import *
from new_parser import *
from ai_ast import *
def main():
    source = """
    title:"My Music Composition"
    tempo:120
    


    foo () = do re mi ; bar  = fa sol la

    # Track with notes and macro calls
    """

    tokenizer = Tokenizer(source)
    tokens = tokenizer.tokenize()

    ast = parse_music(tokens)

    # print(tokens)

    print(traverse_ast(ast))

    return ast


if __name__ == "__main__":
    main()
