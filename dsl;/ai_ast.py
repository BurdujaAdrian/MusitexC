# AST Node classes
from lexer import *
class ASTNode:
    def __init__(self):
        pass

    def __repr__(self):
        return self.__str__()


class Program(ASTNode):
    def __init__(self, metadata, macros, variables, tracks):
        super().__init__()
        self.metadata = metadata
        self.macros = macros
        self.variables = variables
        self.tracks = tracks

    def __str__(self):
        return f"Program(metadata={self.metadata}, macros={self.macros}, variables={self.variables}, tracks={self.tracks})"


class Metadata(ASTNode):
    def __init__(self):
        super().__init__()
        self.title = None
        self.tempo = None
        self.key = None

    def __str__(self):
        return f"Metadata(title={self.title}, tempo={self.tempo}, key={self.key})"


class Macro(ASTNode):
    def __init__(self, name, parameters, body):
        super().__init__()
        self.name = name
        self.parameters = parameters
        self.body = body

    def __str__(self):
        return f"Macro(name={self.name}, parameters={self.parameters}, body={self.body})"


class Variable(ASTNode):
    def __init__(self, name, value):
        super().__init__()
        self.name = name
        self.value = value

    def __str__(self):
        if isinstance(self.value, str):
            return f"Variable(name={self.name}, value={self.value})"
        else:
            return f"Variable(name={self.name}, value={self.value})"


class Track(ASTNode):
    def __init__(self, name, elements):
        super().__init__()
        self.name = name
        self.elements = elements

    def __str__(self):
        return f"Track(name={self.name}, elements={self.elements})"


class Note(ASTNode):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def __str__(self):
        return f"Note({self.value})"


class MacroCall(ASTNode):
    def __init__(self, name, arguments=None):
        super().__init__()
        self.name = name
        self.arguments = arguments or []  # List of argument values

    def __str__(self):
        return f"MacroCall(name={self.name}, arguments={self.arguments})"


class VariableReference(ASTNode):
    def __init__(self, name):
        super().__init__()
        self.name = name

    def __str__(self):
        return f"VariableReference({self.name})"


class Separator(ASTNode):
    def __init__(self):
        super().__init__()

    def __str__(self):
        return "Separator()"

def traverse_ast(node, indent=0):
    prefix = "  " * indent
    result = []

    if isinstance(node, Program):
        result.append(f"{prefix}Program:")
        result.append(traverse_ast(node.metadata, indent + 1))

        if node.macros:
            result.append(f"{prefix}Macros:")
            for macro in node.macros:
                result.append(traverse_ast(macro, indent + 1))

        if node.variables:
            result.append(f"{prefix}Variables:")
            for variable in node.variables:
                result.append(traverse_ast(variable, indent + 1))

        if node.tracks:
            result.append(f"{prefix}Tracks:")
            for track in node.tracks:
                result.append(traverse_ast(track, indent + 1))

    elif isinstance(node, Metadata):
        result.append(f"{prefix}Metadata:")
        if node.title:
            result.append(f"{prefix}  Title: {node.title}")
        if node.tempo:
            result.append(f"{prefix}  Tempo: {node.tempo}")
        if node.key:
            result.append(f"{prefix}  Key: {node.key}")

    elif isinstance(node, Macro):
        result.append(f"{prefix}Macro '{node.name}':")
        result.append(f"{prefix}  Parameters: {node.parameters}")
        result.append(f"{prefix}  Body:")
        for element in node.body:
            result.append(traverse_ast(element, indent + 2))

    elif isinstance(node, Variable):
        result.append(f"{prefix}Variable '{node.name}' = {traverse_ast(node.value, 0)}")

    elif isinstance(node, Track):
        result.append(f"{prefix}Track '{node.name}':")
        result.append(f"{prefix}  Elements:")
        for element in node.elements:
            result.append(traverse_ast(element, indent + 2))

    elif isinstance(node, Note):
        return f"{prefix}Note: {node.value}"

    elif isinstance(node, MacroCall):
        return f"{prefix}MacroCall: {node.name} {node.arguments}"

    elif isinstance(node, VariableReference):
        return f"{prefix}VariableReference: {node.name}"

    elif isinstance(node, Separator):
        result.append(f"{prefix}Separator")

    return "\n".join(result) if isinstance(result, list) else result

