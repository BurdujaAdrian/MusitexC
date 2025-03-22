from lexer import Lexer  # Your lexer class

def print_tokens(input_str):
    lexer = Lexer(input_str)
    tokens = lexer.tokenize()
    type(tokens)
    for token in tokens:
        print(f"{token.type}: '{token.str}'")

# Test string
test_string = """
title: "My Song"
tempo = 120
piano: do re mi
"""

# Run it
print_tokens(test_string)