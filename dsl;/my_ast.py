from enum import Enum, auto


class IdentType(Enum):
    MACRO = auto()
    TRACK = auto()
    SET = auto()
    DEF = auto()
    KEYWORD = auto()
    NOTE = auto()
    INSTRUMENT = auto()


class NoteMode(Enum):
    NEUTRAL = auto()
    HOLD = auto()
    RELEASE = auto()


class Identifier:
    def __init__(self, definition, ident_type):
        self.definition = definition
        self.type = ident_type


# Expression classes
class Note:
    def __init__(self, note, octave=4, duration=1, mode=NoteMode.NEUTRAL):
        self.note = note
        self.octave = octave
        self.duration = duration
        self.mode = mode

    def __repr__(self):
        return f"Note({self.note}, octave={self.octave}, duration={self.duration}, mode={self.mode})"


class Macro:
    def __init__(self, name, args=None):
        self.name = name
        self.args = args

    def __repr__(self):
        return f"Macro({self.name}, args={self.args})"


class ExprGroup:
    def __init__(self, expressions=None):
        self.expressions = expressions or []

    def __repr__(self):
        return f"ExprGroup({self.expressions})"


class Octave:
    class Direction(Enum):
        ASCENDING = auto()
        DESCENDING = auto()

    def __init__(self, direction, value):
        self.direction = direction
        self.value = value

    def __repr__(self):
        return f"Octave({self.direction}, {self.value})"


# Statement classes
class MacroDef:
    def __init__(self, identifier, body, args=None):
        self.identifier = identifier
        self.args = args
        self.body = body or []

    def __repr__(self):
        return f"MacroDef({self.identifier}, args={self.args}, body={self.body})"


class Track:
    def __init__(self, instrument, name, body):
        self.instrument = instrument
        self.name = name
        self.body = body

    def __repr__(self):
        return f"Track({self.instrument}, {self.name}, {self.body})"


class Movement:
    def __init__(self, instrument):
        self.instrument = instrument

    def __repr__(self):
        return f"Movement({self.instrument})"


class TaggedMovement:
    def __init__(self, instrument, tag):
        self.instrument = instrument
        self.tag = tag

    def __repr__(self):
        return f"TaggedMovement({self.instrument}, {self.tag})"


class SetDef:
    def __init__(self, identifier, items=None):
        self.identifier = identifier
        self.items = items or {}

    def __repr__(self):
        return f"SetDef({self.identifier}, {self.items})"


# Expression wrapper
class Expression:
    def __init__(self, expr, next_expr=None):
        self.expr = expr
        self.next = next_expr

    def __repr__(self):
        return f"Expression({self.expr}, next={self.next})"


# AST class
class AST:
    def __init__(self):
        self.title = ""
        self.copyright = ""
        self.statements = []
        self.definitions = {}
        self.no_header = False

    def __repr__(self):
        return f"AST(title={self.title}, copyright={self.copyright}, statements={len(self.statements)}, definitions={len(self.definitions.keys())}, no_header={self.no_header})"

    def print_ast(self):
        print("AST:")
        print(f"Title: {self.title}")
        print(f"Copyright: {self.copyright}")
        print(f"No Header: {self.no_header}")

        print("\nStatements:")
        for stmt in self.statements:
            print(f"  {stmt}")

        print("\nDefinitions:")
        for key, value in self.definitions.items():
            print(f"  {key}: {value.type} -> {value.definition}")