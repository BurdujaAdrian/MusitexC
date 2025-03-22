# Example usage with sample input
from lexer import *
from new_parser import *
from ai_ast import *
def main():
    source = """
    title:"My Music Composition"
    tempo:120

    # Define variables
    first = la
    last = si

    # Define macros
    my_macro() = do re mi fa sol la si
    my_macro2(first,last) = first re mi fa last

    # Track with notes and macro calls
    piano: do mi my_macro. la si my_macro2(do,si).

    ---
    """

    tokenizer = Tokenizer(source)
    tokens = tokenizer.tokenize()

    ast = parse_music(tokens)

    print(traverse_ast(ast))

    return ast


if __name__ == "__main__":
    main()
