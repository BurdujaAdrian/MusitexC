
from lexer import Tokenizer
from new_parser import parse_music
from interpreter import interpret_music, MusicNote
import sys

def main(source_code=None):
    if not source_code:
        source_code = """
        title:"My Music Composition"
        tempo:120

        # Define variables
        melancholy = mi
        resolve = sol

        # Define macros
        bitter_chorus() = la si la sol fa mi re
        soft_verse(melancholy, resolve) = melancholy re fa sol resolve

        # Track with notes and macro calls
        piano: do mi bitter_chorus. melancholy si soft_verse(mi,sol).
        violin: sol5 fa5 mi5 re5 do5

        ---
        """


    print("Processing music code...")
    print("-" * 50)
    print(source_code)
    print("-" * 50)

    # Tokenize the source code
    tokenizer = Tokenizer(source_code)
    tokens = tokenizer.tokenize()
    
    print("\nTokens:")
    for token in tokens[:20]:  # Show just first 20 tokens to avoid clutter
        print(f"  {token}")
    if len(tokens) > 20:
        print(f"  ... and {len(tokens) - 20} more tokens")

    # Parse the tokens to create an AST
    ast = parse_music(tokens)
    
    # Display simplified AST structure for debugging
    print("\nAST Structure:")
    print("  Metadata:", ast.metadata.title, ast.metadata.tempo, ast.metadata.key)
    print(f"  Macros: {len(ast.macros)}")
    for macro in ast.macros:
        print(f"    {macro.name} with {len(macro.parameters)} parameters")
    
    print(f"  Variables: {len(ast.variables)}")
    for var in ast.variables:
        print(f"    {var.name} = {var.value}")
    
    print(f"  Tracks: {len(ast.tracks)}")
    for track in ast.tracks:
        print(f"    {track.name} with {len(track.elements)} elements")

    # Interpret the AST
    print("\nInterpreting music:")
    output = interpret_music(ast)
    print(output)
    
    # Print the interpretation results
    print("\nInterpretation Results:")
    for line in output:
        print(line)

    return output

if __name__ == "__main__":
    # If a file was specified, read from it
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as file:
            source_code = file.read()
        main(source_code)
    else:
        # Otherwise use the default example
        main()
