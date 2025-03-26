from ai_ast import *

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current_token = tokens[0] if tokens else None

    def advance(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
            return self.tokens[self.pos - 1]
        return self.tokens[-1]  # Return EOF token

    def peek(self, offset=1):
        pos = self.pos + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return self.tokens[-1]  # Return EOF token

    def match(self, token_type):
        if self.current_token.type == token_type:
            return self.advance()
        elif self.current_token.type != token_type:
            return False
        else:
            raise SyntaxError(
                f"Expected {token_type}, got {self.current_token.type} at line {self.current_token.line}, column {self.current_token.column}"
            )

    def skip_newlines(self):
        """Skip any newline tokens"""
        while self.current_token.type == TokenType.NL:
            self.advance()

    def parse(self):
        # Create program node (root of AST)
        #update metadata if you want to add for example
        metadata = Metadata()
        macros = []
        variables = []
        tracks = []

        # Skip initial newlines
        self.skip_newlines()

        # Continue parsing until we reach EOF
        while self.current_token.type != TokenType.EOF:
            # Handle metadata
            if self.current_token.type == TokenType.KW_TITLE:
                self.parse_title(metadata)
            elif self.current_token.type == TokenType.KW_TEMPO:
                self.parse_tempo(metadata)
            elif self.current_token.type == TokenType.KW_KEY:
                self.parse_key(metadata)
            elif self.current_token.type == TokenType.SEMICOLON:
                self.advance()
            # Handle macro definition
            elif (self.current_token.type ==
                  TokenType.ALPHANUM and self.peek().type == TokenType.OPEN_PAREN or self.peek().type == TokenType.EQUAL):
                macro = self.parse_macro_definition()
                macros.append(macro)

            # Handle variable assignment
            elif self.current_token.type == TokenType.ALPHANUM and self.peek().type == TokenType.EQUAL:
                variable = self.parse_variable_assignment()
                variables.append(variable)
            # Handle track definition
            elif self.current_token.type == TokenType.ALPHANUM and self.peek().type == TokenType.COLON:
                track_name = self.current_token.value
                self.advance()  # Skip track name
                self.match(TokenType.COLON)
                track = Track(track_name, self.parse_track_elements())
                tracks.append(track)
            # Handle separators
            elif self.current_token.type == TokenType.DASH:
                self.parse_separator()
            # Skip newlines between statements
            elif self.current_token.type == TokenType.NL:
                self.advance()
            # Handle unexpected tokens
            else:
                raise SyntaxError(
                    f"Unexpected token {self.current_token.type} at line {self.current_token.line}, column {self.current_token.column}")

        return Program(metadata, macros, variables, tracks)

    def parse_title(self, metadata):
        """Parse the title property"""
        self.match(TokenType.KW_TITLE)
        self.match(TokenType.COLON)
        title_token = self.match(TokenType.STRING)
        metadata.title = title_token.value.strip('"')
        # Skip newline after title if present
        if self.current_token.type == TokenType.NL:
            self.advance()

    def parse_tempo(self, metadata):
        """Parse the tempo property"""
        self.match(TokenType.KW_TEMPO)
        self.match(TokenType.COLON)
        tempo_token = self.match(TokenType.NUM)
        metadata.tempo = int(tempo_token.value)
        # Skip newline after tempo if present
        if self.current_token.type == TokenType.NL:
            self.advance()

    def parse_key(self, metadata):
        """Parse the key property"""
        self.match(TokenType.KW_KEY)
        self.match(TokenType.COLON)
        key_token = self.match(TokenType.ALPHANUM)
        metadata.key = key_token.value
        # Skip newline after key if present
        if self.current_token.type == TokenType.NL:
            self.advance()

    def parse_macro_definition(self):
        """Parse macro definition like 'my_macro = do re mi' or 'my_macro2 with(first,last) = first re mi last'"""
        macro_name = self.match(TokenType.ALPHANUM).value
        parameters = []

        # Parse parameters
        if (self.match(TokenType.OPEN_PAREN)):

        # If there are parameters (not empty parentheses)
            if self.current_token.type != TokenType.CLOSE_PAREN:
                # Parse first parameter
                if self.current_token.type == TokenType.ALPHANUM:
                    parameters.append(self.current_token.value)
                    self.advance()

                    # Parse additional parameters separated by commas
                    while self.current_token.type == TokenType.COMMA:
                        self.advance()  # Skip comma
                        if self.current_token.type == TokenType.ALPHANUM:
                            parameters.append(self.current_token.value)
                            self.advance()
                        else:
                            raise SyntaxError(
                                f"Expected parameter name, got {self.current_token.type} at line {self.current_token.line}, column {self.current_token.column}")

            self.match(TokenType.CLOSE_PAREN)
            self.match(TokenType.EQUAL)
            body = self.parse_macro_body()
        else:
        # Parse equals sign and body
            self.match(TokenType.EQUAL)
            body = self.parse_macro_body()

        # Expect a newline or EOF after macro definition
        if self.current_token.type == TokenType.NL:
            self.advance()

        return Macro(macro_name, parameters, body)

    def parse_macro_body(self):
        """Parse the body of a macro definition"""
        body = []

        # Parse notes, variables, etc. until end of line
        while self.current_token.type not in [TokenType.NL, TokenType.SEMICOLON,  TokenType.EOF]:
            if self.current_token.type == TokenType.ALPHANUM:
                element_value = self.current_token.value
                self.advance()

                # Check if it's a macro call
                # if self.current_token.type == TokenType.SEMICOLON:
                #     self.advance()
                #     return body
                if self.current_token.type == TokenType.OPEN_PAREN:
                    # Parse macro call
                    body.append(self.parse_macro_call_with_name(element_value))
                # Otherwise it's a note or variable reference
                else:
                    body.append(Note(element_value))
            else:
                self.advance()  # Skip other tokens

        return body

    def parse_variable_assignment(self):
        var_name = self.match(TokenType.ALPHANUM).value
        self.match(TokenType.EQUAL)

        # Parse the value (currently only supporting several  notes)
        if self.current_token.type == TokenType.ALPHANUM:
            value = Note(self.current_token.value)
            self.advance()

        else:
            raise SyntaxError(
                f"Expected note value, got {self.current_token.type} at line {self.current_token.line}, column {self.current_token.column}")

        # Expect a newline or EOF after variable assignment
        if self.current_token.type == TokenType.NL:
            self.advance()

        return Variable(var_name, value)

    def parse_track_elements(self):
        """Parse the elements of a track"""
        elements = []

        # Parse notes, commands, and macros until end of track
        while self.current_token.type not in [TokenType.EOF]:
            if self.current_token.type == TokenType.NL:
                # End of track on newline
                self.advance()
                break
            elif self.current_token.type == TokenType.ALPHANUM:
                element_value = self.current_token.value
                self.advance()

                # Check if it's a macro call
                if self.current_token.type == TokenType.OPEN_PAREN:
                    # Parse macro call
                    elements.append(self.parse_macro_call_with_name(element_value))
                # Check if it's the end of a macro call (with a dot)
                elif self.current_token.type == TokenType.DOT:
                    elements.append(MacroCall(element_value))
                    self.advance()
                # Otherwise it's a note or variable reference
                else:
                    elements.append(Note(element_value))
            else:
                self.advance()  # Skip other tokens

        return elements

    def parse_macro_call_with_name(self, macro_name):
        """Parse a macro call with arguments"""
        arguments = []

        # Parse opening parenthesis
        self.match(TokenType.OPEN_PAREN)

        # Parse arguments if any
        if self.current_token.type != TokenType.CLOSE_PAREN:
            # Parse first argument
            if self.current_token.type == TokenType.ALPHANUM:
                arguments.append(self.current_token.value)
                self.advance()

                # Parse additional arguments
                while self.current_token.type == TokenType.COMMA:
                    self.advance()  # Skip comma
                    if self.current_token.type == TokenType.ALPHANUM:
                        arguments.append(self.current_token.value)
                        self.advance()
                    else:
                        raise SyntaxError(
                            f"Expected argument, got {self.current_token.type} at line {self.current_token.line}, column {self.current_token.column}")

        # Parse closing parenthesis
        self.match(TokenType.CLOSE_PAREN)

        # Check for dot (optional)
        if self.current_token.type == TokenType.DOT:
            self.advance()

        return MacroCall(macro_name, arguments)

    def parse_separator(self):
        while self.current_token.type == TokenType.DASH:
            self.advance()
        if self.current_token.type == TokenType.NL:
            self.advance()
        return Separator()


def parse_music(tokens):
    parser = Parser(tokens)
    return parser.parse()