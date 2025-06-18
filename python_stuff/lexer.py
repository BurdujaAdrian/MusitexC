class TokenType:
    OPEN_BRACE = "OPEN_BRACE"
    CLOSE_BRACE = "CLOSE_BRACE"
    OPEN_PAREN = "OPEN_PAREN"
    CLOSE_PAREN = "CLOSE_PAREN"
    OPEN_BRACKET = "OPEN_BRACKET"
    CLOSE_BRACKET = "CLOSE_BRACKET"
    COLON = "COLON"
    DOUBLE_QUOTE = "DOUBLE_QUOTE"
    COMMA = "COMMA"
    PIPE = "PIPE"
    SLASH = "SLASH"
    BANG = "BANG"
    EQUAL = "EQUAL"
    NL = "NL"
    SINGLE_QUOTE = "SINGLE_QUOTE"
    DOT = "DOT"
    DASH = "DASH"
    PLUS = "PLUS"
    GREATER_THAN = "GREATER_THAN"
    LESS_THAN = "LESS_THAN"
    CARROT = "CARROT"
    ASTERISK = "ASTERISK"
    SEMICOLON = "SEMICOLON"
    SPACE = "SPACE"

    # Literals
    ALPHANUM = "ALPHANUM"
    NUM = "NUM"
    STRING = "STRING"

    # Keywords
    KW_MACRO = 'KW_MACRO'
    KW_TRACK = 'TRACK'
    KW_TITLE = "KW_TITLE"
    KW_CR = "KW_CR"
    KW_R = "KW_R"
    V = "V" # volume

    EOF = "EOF"

    # notes
    do = "do"
    re = "re"
    mi = "mi"
    fa = "fa"
    sol = "sol"
    la = "la"
    si = "si"



class Token:
    def __init__(self, value, line, column, token_type):
        self.value = value
        self.line = line
        self.column = column
        self.type = token_type

    def __repr__(self):
        return f"<Token {self.type} '{self.value}' at {self.line}:{self.column}>"


class Tokenizer:
    def __init__(self, source):
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 0
        self.tokens = []

    def tokenize(self):

        while self.pos < len(self.source) -1:
            self.tokenize_next()

        # Add extra newline token for parsing reasons
        self.tokens.append(Token("ln",self.line,self.column,TokenType.NL))
        # Add EOF token
        self.tokens.append(Token("eof", self.line, self.column, TokenType.EOF))
        return self.tokens

    # It peeks char
    def peek(self, offset=0):
        pos = self.pos + offset
        if pos >= len(self.source):
            return None
        return self.source[pos]

    #Increases position after taking the token
    def advance(self):
        char = self.source[self.pos]
        self.pos += 1
        self.column += 1

        if char == '\n':
            self.line += 1
            self.column = 0

        return char

    def tokenize_next(self):
        char = self.peek()

        # Skip whitespace except newlines
        if char in ' \t':
            self.tokens.append(Token(char, self.line, self.column, TokenType.SPACE))
            while char in ' \t':
                self.advance()
                char = self.peek()
            return

        # Handle newlines
        if char == '\n':
            self.tokens.append(Token(char, self.line, self.column, TokenType.NL))
            self.advance()
            return

        # Handle comments
        if char == '#':
            self.tokenize_comment()
            return

        # Handle identifiers and keywords
        if char.isalpha() or char == '_':
            self.tokenize_identifier()
            return

        # Handle numbers
        if char.isdigit():
            self.tokenize_number()
            return

        # Handle strings
        if char == '"':

            self.tokenize_string()
            return

        # Handle delimiters
        if self.is_delimiter(char):
            self.tokenize_delimiter()
            return

        # If we get here, we have an unrecognized character
        raise SyntaxError(f"Unrecognized character '{char}' at line {self.line}, column {self.column}")

    # Comments are not added to token stream
    def tokenize_comment(self):
        self.advance()

        while True:
            if self.peek() in '\r\n':
                return
            self.advance()



    def tokenize_identifier(self):

        start_pos = self.pos
        start_line = self.line
        start_column = self.column

        # Read all alphanumeric characters
        while self.peek() is not None and (self.peek().isalnum() or self.peek() == '_'):
            self.advance()

        # Extract the identifier
        identifier = self.source[start_pos:self.pos]

        # Check if it's a keyword
        token_type = self.get_keyword_type(identifier)
        if token_type:
            self.tokens.append(Token(identifier, start_line, start_column, token_type))
        else:
            self.tokens.append(Token(identifier, start_line, start_column, TokenType.ALPHANUM))

    def tokenize_number(self):
        start_pos = self.pos
        start_line = self.line
        start_column = self.column

        # Read all digits
        while self.peek() is not None and self.peek().isdigit():
            self.advance()

        # Check for 'ms' suffix
        if self.peek() == 'm' and self.peek(1) == 's':
            self.advance()  # Skip 'm'
            self.advance()  # Skip 's'

        # Extract the number
        number = self.source[start_pos:self.pos]
        self.tokens.append(Token(number, start_line, start_column, TokenType.NUM))

    def tokenize_string(self):

        start_pos = self.pos
        start_line = self.line
        start_column = self.column

        self.advance()  # Skip opening quote

        # i don't understand this
        escaped = False
        while self.peek() is not None:
            if self.peek() == '\\':
                escaped = True
                self.advance()
                continue

            if self.peek() == '"' and not escaped:
                self.advance()  # Skip closing quote
                break

            escaped = False
            self.advance()

        # Extract the string including quotes
        string = self.source[start_pos:self.pos]
        self.tokens.append(Token(string, start_line, start_column, TokenType.STRING))

    def tokenize_delimiter(self):
        char = self.peek()
        token_type = None

        if char == '{':
            token_type = TokenType.OPEN_BRACE
        elif char == '}':
            token_type = TokenType.CLOSE_BRACE
        elif char == '(':
            token_type = TokenType.OPEN_PAREN
        elif char == ')':
            token_type = TokenType.CLOSE_PAREN
        elif char == '[':
            token_type = TokenType.OPEN_BRACKET
        elif char == ']':
            token_type = TokenType.CLOSE_BRACKET
        elif char == ':':
            token_type = TokenType.COLON
        elif char == '"':
            token_type = TokenType.DOUBLE_QUOTE
        elif char == ',':
            token_type = TokenType.COMMA
        elif char == '|':
            token_type = TokenType.PIPE
        elif char == '/':
            token_type = TokenType.SLASH
        elif char == '!':
            token_type = TokenType.BANG
        elif char == '=':
            token_type = TokenType.EQUAL
        elif char == "'":
            token_type = TokenType.SINGLE_QUOTE
        elif char == '.':
            token_type = TokenType.DOT
        elif char == '-':
            token_type = TokenType.DASH
        elif char == '>':
            token_type = TokenType.GREATER_THAN
        elif char == '<':
            token_type = TokenType.LESS_THAN
        elif char == '^':
            token_type = TokenType.CARROT
        elif char == '*':
            token_type = TokenType.ASTERISK
        elif char == ';':
            token_type = TokenType.SEMICOLON
        elif char == '+':
            token_type = TokenType.PLUS

        self.tokens.append(Token(char, self.line, self.column, token_type))
        self.advance()

    def is_delimiter(self, char):
        return char in "{}()[]:\",/='.-><*;+|!^"

    def get_keyword_type(self, word):
        keywords = {
            "title": TokenType.KW_TITLE,
            "copy_right": TokenType.KW_CR,
            "r": TokenType.KW_R,
            "track": TokenType.KW_TRACK,
            "do":TokenType.do ,
            "re":TokenType.re ,
            "mi":TokenType.mi ,
            "fa":TokenType.fa ,
            "sol":TokenType.sol ,
            "la":TokenType.la ,
            "si":TokenType.si ,
            "vol":TokenType.V,
            "v":TokenType.V,
            "volume":TokenType.V,
        }
        return keywords.get(word)