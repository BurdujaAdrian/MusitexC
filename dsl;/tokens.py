from enum import Enum

class TokenType(Enum):
    # Delimiters
    OPEN_BRACE = "{"
    CLOSE_BRACE = "}"
    OPEN_PAREN = "("
    CLOSE_PAREN = ")"
    OPEN_BRACKET = "["
    CLOSE_BRACKET = "]"
    COLON = ":"
    DOUBLE_QUOTE = "\""
    COMMA = ","
    PIPE = "|"
    SLASH = "/"
    EQUAL = "="
    NL = "\n"
    SINGLE_QUOTE = "'"
    DOT = "."
    DASH = "-"
    PLUS = "+"
    GREATER_THAN = ">"
    LESS_THAN = "<"
    ASTERISK = "*"
    SEMICOLON = ";"

    # Literals
    ALPHANUM = "alphanum"
    NUM = "num"
    STRING = "string"

    # Keywords
    KW_WITH = "with"
    KW_TITLE = "title"
    KW_CR = "copy_right"
    KW_KEY = "key"
    KW_TEMPO = "tempo"
    KW_B = "b"
    KW_S = "s"
    KW_R = "r"
    KW_OCTAVE = "octave"
    KW_MEASURE = "measure"

    EOF = "eof"

class Token:
    def __init__(self, string: str, line: int, n: int, type_: TokenType):
        self.str = string
        self.line = line
        self.n = n  # Column number
        self.type = type_

    def __repr__(self):
        return f"<{self.type.value}: \"{self.str}\">"