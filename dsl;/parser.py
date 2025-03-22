from lexer import Token, TokenType
from my_ast import *




class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current_token = None
        self.parse_stack = []
        self.ast = AST()

        # Initialize with first token
        if tokens:
            self.current_token = tokens[0]

    def parse(self):
        self.parse_stack.append(ParseState.NONE)

        while self.parse_stack:
            state = self.parse_stack.pop()

            if state == ParseState.NONE:
                self.parse_none()
            elif state == ParseState.HEADER:
                self.parse_header()
            elif state == ParseState.H_TITLE:
                self.parse_title()
            elif state == ParseState.H_CR:
                self.parse_copyright()
            elif state == ParseState.STATEMENT:
                self.parse_statement()
            elif state == ParseState.S_MACRO_DEF:
                self.parse_macro_def()
            elif state == ParseState.S_SET_DEF:
                self.parse_set_def()
            elif state == ParseState.S_MOVEMENT:
                self.parse_movement()
            elif state == ParseState.S_TAGGED_M:
                self.parse_tagged_movement()
            elif state == ParseState.EXPR:
                self.parse_expr()
            elif state == ParseState.E_NOTE:
                self.parse_note()
            elif state == ParseState.E_MACRO_APL:
                self.parse_macro_apl()
            elif state == ParseState.E_MACRO_INL:
                self.parse_macro_inl()
            elif state == ParseState.C_EXPR_GROUP:
                self.parse_expr_group()
            elif state == ParseState.E_SETTING:
                self.parse_setting()
            elif state == ParseState.C_ARGS:
                self.parse_args()
            elif state == ParseState.ERR:
                self.parse_error()
            elif state == ParseState.NL:
                self.parse_nl()
            elif state == ParseState.EOF:
                break

        return self.ast

    def parse_nl(self):
        self.match(TokenType.NL)
        if self.current_token.type == TokenType.NL:
            self.parse_stack.append(ParseState.NL)
        # elif self.current_token.type ==
        #
        # elif

    def advance(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
            return self.tokens[self.pos - 1]
        return self.tokens[-1]  # Return EOF token

    def peek(self, offset=0):
        pos = self.pos + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return self.tokens[-1]  # Return EOF token

    def match(self, token_type):
        if self.current_token.type == token_type:
            return self.advance()
        raise SyntaxError(
            f"Expected {token_type}, got {self.current_token.type} at line {self.current_token.line}, column {self.current_token.column}")

    def parse_none(self):
        if self.current_token.type in (TokenType.KW_TITLE, TokenType.KW_CR):
            if not self.ast.no_header:
                self.parse_stack.append(ParseState.HEADER)
        elif self.current_token.type == TokenType.EOF:
            self.parse_stack.append(ParseState.EOF)
        elif self.current_token.type == TokenType.NL:
            self.parse_stack.append(ParseState.NL)
        else:
            self.parse_stack.append(ParseState.STATEMENT)

    def parse_header(self):
        # Keep parsing header until ---
        if self.current_token.type == TokenType.KW_TITLE:
            self.parse_stack.append(ParseState.HEADER)
            self.parse_stack.append(ParseState.H_TITLE)
        elif self.current_token.type == TokenType.KW_CR:
            self.parse_stack.append(ParseState.HEADER)
            self.parse_stack.append(ParseState.H_CR)
        elif self.current_token.type == TokenType.DASH:
            # Check for header end marker
            if (self.peek(1).type == TokenType.DASH and
                    self.peek(2).type == TokenType.DASH):
                self.advance()  # Skip first dash
                self.advance()  # Skip second dash
                self.advance()  # Skip third dash
                self.ast.no_header = True
                self.parse_stack.append(ParseState.STATEMENT)
            else:
                self.parse_error()
        else:
            self.parse_stack.append(ParseState.STATEMENT)

    def parse_title(self):
        self.match(TokenType.KW_TITLE)
        self.match(TokenType.COLON)
        title_token = self.match(TokenType.STRING)
        # Remove quotes from the title
        self.ast.title = title_token.value[1:-1]

    def parse_copyright(self):
        self.match(TokenType.KW_CR)
        self.match(TokenType.COLON)
        cr_token = self.match(TokenType.STRING)
        # Remove quotes from the copyright
        self.ast.copyright = cr_token.value[1:-1]

    def parse_statement(self):
        if self.current_token.type == TokenType.ALPHANUM:
            # Check next token to determine statement type
            identifier = self.current_token.value
            next_token = self.peek(1)

            if next_token.type == TokenType.EQUAL:
                # Macro definition
                self.parse_stack.append(ParseState.S_MACRO_DEF)
            elif next_token.type == TokenType.COLON:
                # Instrument or tagged movement
                next_next_token = self.peek(2)
                if next_next_token.type == TokenType.ALPHANUM:
                    self.parse_stack.append(ParseState.S_TAGGED_M)
                else:
                    self.parse_stack.append(ParseState.S_MOVEMENT)
            else:
                # Could be a global setting
                self.parse_stack.append(ParseState.S_GL_SETTING)
        elif self.current_token.type == TokenType.EOF:
            self.parse_stack.append(ParseState.EOF)
        else:
            # Skip over unknown tokens for error recovery
            self.advance()

    def parse_macro_def(self):
        identifier = self.match(TokenType.ALPHANUM).value

        # Check for with keyword and arguments
        args = None
        if self.current_token.type == TokenType.KW_WITH:
            self.advance()
            self.parse_stack.append(ParseState.C_ARGS)
            args = self.parse_args_list()

        # Expect equals sign
        self.match(TokenType.EQUAL)

        # Parse the macro body
        body = []
        while self.current_token.type != TokenType.NL and self.current_token.type != TokenType.EOF:
            expr = self.parse_expression()
            if expr:
                body.append(expr)
            else:
                break

        # Create macro definition
        macro_def = MacroDef(identifier, body, args)
        self.ast.statements.append(macro_def)

        # Add to definitions map
        self.ast.definitions[identifier] = Identifier(macro_def, IdentType.MACRO)

        # Skip newline
        if self.current_token.type == TokenType.NL:
            self.advance()

    def parse_args_list(self):
        args = []

        # Check if there are arguments in parentheses
        if self.current_token.type == TokenType.OPEN_PAREN:
            self.advance()

            # Parse comma separated arguments
            if self.current_token.type == TokenType.ALPHANUM:
                args.append(self.current_token.value)
                self.advance()

                while self.current_token.type == TokenType.COMMA:
                    self.advance()
                    if self.current_token.type == TokenType.ALPHANUM:
                        args.append(self.current_token.value)
                        self.advance()
                    else:
                        self.parse_error()
                        break

            # Expect closing parenthesis
            if self.current_token.type == TokenType.CLOSE_PAREN:
                self.advance()
            else:
                self.parse_error()

        return args if args else None

    def parse_expression(self):
        # Determine the type of expression
        if self.current_token.type == TokenType.ALPHANUM:
            # Could be a note or a macro application
            if self.peek(1).type == TokenType.OPEN_PAREN:
                return self.parse_macro_application()
            else:
                return self.parse_note_expression()
        elif self.current_token.type in (TokenType.KW_B, TokenType.KW_R, TokenType.KW_S, TokenType.KW_OCTAVE):
            return self.parse_setting_expression()
        elif self.current_token.type == TokenType.PIPE:
            # Skip the pipe and continue
            self.advance()
            return None
        else:
            # Skip unknown tokens
            self.advance()
            return None

    def parse_note_expression(self):
        note_name = self.match(TokenType.ALPHANUM).value

        # Check for octave and duration modifiers
        octave = 4  # Default octave
        duration = 1  # Default duration
        mode = NoteMode.NEUTRAL

        # More parsing logic for note modifiers would go here

        return Note(note_name, octave, duration, mode)

    def parse_macro_application(self):
        name = self.match(TokenType.ALPHANUM).value

        args = None
        # Check if there are arguments
        if self.current_token.type == TokenType.OPEN_PAREN:
            self.advance()
            args = []

            # Parse comma separated arguments
            while self.current_token.type != TokenType.CLOSE_PAREN and self.current_token.type != TokenType.EOF:
                if self.current_token.type in (TokenType.ALPHANUM, TokenType.STRING, TokenType.NUM):
                    args.append(self.current_token.value)
                    self.advance()

                    if self.current_token.type == TokenType.COMMA:
                        self.advance()
                    elif self.current_token.type != TokenType.CLOSE_PAREN:
                        self.parse_error()
                        break
                else:
                    self.parse_error()
                    break

            # Expect closing parenthesis
            if self.current_token.type == TokenType.CLOSE_PAREN:
                self.advance()
            else:
                self.parse_error()

        return Macro(name, args)

    def parse_setting_expression(self):
        # For simplicity, just handle octave settings
        if self.current_token.type == TokenType.KW_OCTAVE:
            self.advance()

            direction = Octave.Direction.ASCENDING  # Default
            # Check for direction
            if self.current_token.type in (TokenType.GREATER_THAN, TokenType.LESS_THAN):
                direction = (Octave.Direction.ASCENDING
                             if self.current_token.type == TokenType.GREATER_THAN
                             else Octave.Direction.DESCENDING)
                self.advance()

            # Expect a value
            if self.current_token.type == TokenType.NUM:
                value = int(self.current_token.value)
                self.advance()
                return Octave(direction, value)
            else:
                self.parse_error()

        # Skip other settings for now
        self.advance()
        return None

    def parse_movement(self):
        instrument = self.match(TokenType.ALPHANUM).value
        self.match(TokenType.COLON)

        # Parse expressions until newline or EOF
        expressions = []
        while self.current_token.type != TokenType.NL and self.current_token.type != TokenType.EOF:
            expr = self.parse_expression()
            if expr:
                expressions.append(expr)

        # Create movement
        movement = Movement(instrument)
        self.ast.statements.append(movement)

        # Skip newline
        if self.current_token.type == TokenType.NL:
            self.advance()

    def parse_tagged_movement(self):
        instrument = self.match(TokenType.ALPHANUM).value
        self.match(TokenType.COLON)
        tag = self.match(TokenType.ALPHANUM).value

        # Create tagged movement
        tagged_movement = TaggedMovement(instrument, tag)
        self.ast.statements.append(tagged_movement)

        # Skip newline
        if self.current_token.type == TokenType.NL:
            self.advance()

    def parse_set_def(self):
        # Not implemented in this simplified version
        self.advance()

    def parse_expr(self):
        # Not used directly, expressions are parsed in context
        pass

    def parse_note(self):
        # Not used directly, notes are parsed in context
        pass

    def parse_macro_apl(self):
        # Not used directly, macro applications are parsed in context
        pass

    def parse_macro_inl(self):
        # Not used directly
        pass

    def parse_expr_group(self):
        # Not used directly
        pass

    def parse_setting(self):
        # Not used directly, settings are parsed in context
        pass

    def parse_args(self):
        # Not used directly, args are parsed in context
        pass

    def parse_error(self):
        print(
            f"Syntax error at line {self.current_token.line}, column {self.current_token.column}: Unexpected token {self.current_token.type}")
        # Skip to next statement for error recovery
        while (self.current_token.type != TokenType.NL and
               self.current_token.type != TokenType.EOF):
            self.advance()

        # Skip the newline
        if self.current_token.type == TokenType.NL:
            self.advance()