# AST Node classes
from lexer import *

class ASTNode:
    def __init__(self, source):
        self.source = source
        pass

    def __repr__(self):
        return self.__str__()

    def source(self):
        return self.source


class Program(ASTNode):
    def __init__(self, metadata, macros, tracks, source,idents,error_list):
        super().__init__(source)
        self.metadata = metadata
        self.macros = macros
        self.tracks = tracks
        self.ident_dic = idents
        self.err_list = error_list

    def __str__(self):
        return f"Program(metadata={self.metadata}, macros={self.macros},tracks={self.tracks})"


class Metadata(ASTNode):
    def __init__(self, title,source):
        super().__init__(source)
        self.title = title 

    def __str__(self):
        return f"Metadata(title={self.title})"

### Statements:

class Macro(ASTNode):
    def __init__(self, name, parameters, body):
        super().__init__(name)
        self.name = name
        self.parameters = parameters
        self.body = body

    def __str__(self):
        return f"Macro(name={self.name}, parameters={self.parameters}, body={self.body})"


class Track(ASTNode):
    def __init__(self, name, movements,source):
        super().__init__(source)
        self.name = name
        self.movements = movements

    def __str__(self):
        return f"Track(name={self.name}, movements={self.movements})"

class Movement(ASTNode):
    def __init__(self,instrument, tag, expressions):
        super().__init__(instrument)
        self.instrument = instrument
        self.tag = tag
        self.expressions = expressions

    def __str__(self):
        return f"Movement(tag={self.tag}, expressions={self.expressions})"


### Expressions



class Ident(ASTNode):
    def __init__(self,source):
        super().__init__(source)
        self.ident = source 

    def __str__(self):
        return f"Identifier={self.ident}"

class ReleaseNote(ASTNode):
    def __init__(self,source):
        super().__init__(source)
    
    def __str__(self):
        return f"release"

class HoldNote(ASTNode):
    def __init__(self,note,source):
        super().__init__(source)
        self.note = note
    
    def __str__(self):
        return f"hold({self.note})"

class Note(ASTNode):
    def __init__(self, value,semitone,octave,duration):
        super().__init__(value)
        self.value = value
        self.semitone = semitone
        self.octave = octave
        self.duration = duration


    def __str__(self):
        return f"Note({self.value},semitone={self.semitone}, octave={self.octave}, duration={self.duration})"

class Chord(ASTNode):
    def __init__(self,notes,source):
        super().__init__(source)
        self.notes = notes

    def __str__(self):
        return f"Chord{self.notes}"

class MacroCall(ASTNode):
    def __init__(self, name, arguments):
        super().__init__(name)
        self.name = name
        self.arguments = arguments
    def __str__(self):
        return f"MacroCall(name={self.name}, arguments={self.arguments or []})"

class Repetition(ASTNode):
    def __init__(self, times, source):
        super().__init__(source)
        self.times = times
        self.source = source
    
    def __str__(self):
        return f"Repeat*{self.times})"

class SetOctave(ASTNode):
    def __init__(self,dir, n,source):
        super().__init__(source)
        self.dir = dir
        self.n = n

    def __str__(self):
        return f"set(Shift {'<' if self.dir else '>'} by {self.n})"

class SetDuration(ASTNode):
    def __init__(self,dur,source):
        super().__init__(source)
        self.dur = dur

    def __str__(self):
        return f"set(Duration={self.dur})"

class Fraction:
    def __init__(self,x,over):
        self.x = x
        self.over = over

    def __str__(self):
        return f"{self.x}/{self.over}"

class SetTempo(ASTNode):
    def __init__(self,n,source):
        super().__init__(source)
        self.n = n

    def __str__(self):
        return f"set(Tempo={self.n})"

class SetTone(ASTNode):
    def __init__(self,n,note,source):
        super().__init__(source)
        self.n = n
        self.note = note
    
    def __str__(self):
        return f"set(Semitone for {self.note} = {self.n})"

class Bar(ASTNode):
    def __init__(self,source):
        super().__init__(source)
    
    def __str__(self):
        return f" bar "

class SetInterval(ASTNode):
    def __init__(self,time):
        super().__init__(time)
        self.time = time
    
    def __str__(self):
        return f"set(Interval={self.time})"

class SetMeasure(ASTNode):
    def __init__(self,x,over,source):
        super().__init__(source)
        self.x = x
        self.over = over
    
    def __str__(self):
        return f"set(Measure={self.x}/{self.over})"


class SetVolume(ASTNode):
    def __init__(self,vol,source):
        super().__init__(source)
        self.vol = vol
    
    def __str__(self):
        return f"set(Volume={self.vol})"

class temp(ASTNode):
    def __init__(self,source):
        super().__init__(source)
    
    def __str__(self):
        return f"temp"

## Collections/groups
class ExprGroup(ASTNode):
    def __init__(self,exprs,source):
        super().__init__(source)
        self.exprs = exprs
    
    def __str__(self):
        return f"exprGroup{{ {self.exprs} }}"

### errors

class errExpr(ASTNode):
    def __init__(self,source):
        super().__init__(source)

    def __str__(self):
        return f"error({self.source})"




def traverse_ast(node, indent):
    prefix = "  " * indent
    result = []

    if isinstance(node, Program):
        result.append(f"{prefix}Program:")
        if node.metadata:
            for meta in node.metadata:
                result.append(traverse_ast(meta, indent + 1))

        if node.macros:
            result.append(f"{prefix}Macros:")
            for macro in node.macros:
                result.append(traverse_ast(macro, indent + 1))

        if node.tracks:
            result.append(f"{prefix}Tracks:")
            for track in node.tracks:
                result.append(traverse_ast(track, indent + 1))

    elif isinstance(node, Metadata):
        result.append(f"{prefix}Metadata:")
        if node.title:
            result.append(f"{prefix}  Title: {node.title}")

    elif isinstance(node, Macro):
        result.append(f"{prefix}Macro '{node.name}':")
        result.append(f"{prefix}  Parameters: {node.parameters}")
        result.append(f"{prefix}  Body:")
        for element in node.body:
            result.append(traverse_ast(element, indent + 2))

    elif isinstance(node, Track):
        result.append(f"{prefix}Track '{node.name}':")
        result.append(f"{prefix}  Movements:")
        for element in node.movements:
            result.append(traverse_ast(element, indent + 2))

    elif isinstance(node,Movement):
        result.append(f"{prefix}{node.instrument.value} {"" if node.tag == "" else node.tag.value} = ")
        if isinstance(node.expressions, ExprGroup):
            bruh()

        for element in node.expressions:
            result.append(traverse_ast(element,indent+2))

    elif isinstance(node, Repetition):
        result.append(f"{prefix}Repeat*{node.times}")

    elif isinstance(node, HoldNote):
        result.append(f"{prefix}Hold(\n{prefix}{traverse_ast(node.note,indent)}\n{prefix})")

    elif( isinstance(node, SetOctave) or
          isinstance(node, SetDuration) or
          isinstance(node, SetTempo) or
          isinstance(node, SetTone) or
          isinstance(node, SetInterval) or
          isinstance(node, Note) or
          isinstance(node, Bar) or
          isinstance(node, Ident) or
          isinstance(node, ReleaseNote) or
          isinstance(node, SetMeasure) or
          isinstance(node, SetVolume) or
          isinstance(node, errExpr)
         ):

        return f"{prefix}{node}"

    elif isinstance(node,MacroCall):
        result.append(f"{prefix}{node.name.value}(")

        for expr in node.arguments:
            result.append(traverse_ast(expr,indent+2))
        result.append(f"{prefix})")

    elif isinstance(node, ExprGroup):
        result.append(f"{prefix}[")

        for expr in node.exprs:
            result.append(traverse_ast(expr,indent+2))

        result.append(f"{prefix}]")

    elif isinstance(node, Chord):
        result.append(f"{prefix}Chord:")
        for note in node.notes:
            result.append(f"{prefix}{traverse_ast(note,indent)}\\")
    
    else:
        raise ValueError(f"Unhandled case: {type(node)}")
    return "\n".join(result) if isinstance(result, list) else result

