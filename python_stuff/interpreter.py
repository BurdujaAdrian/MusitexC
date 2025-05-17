from lexer import TokenType, Token, Tokenizer
from ai_ast import *

class MusicNote:
    NOTE_VALUES = {
        'do': 'C', 're': 'D', 'mi': 'E', 'fa': 'F', 
        'sol': 'G', 'la': 'A', 'si': 'B', 'ti': 'B'
    }
    
    def __init__(self, name, octave=4, duration=1.0, accidental=None):
        self.name = name
        self.octave = octave
        self.duration = duration  # in beats
        self.accidental = accidental  # '#' for sharp, 'b' for flat
        
        # Convert solfege to letter names if needed
        if name.lower() in self.NOTE_VALUES:
            self.letter_name = self.NOTE_VALUES[name.lower()]
        else:
            self.letter_name = name.upper()
            
    def __str__(self):
        acc = self.accidental if self.accidental else ""
        return f"{self.letter_name}{acc}{self.octave}"
    
    def frequency(self):
        # Basic implementation - could be expanded with proper frequency calculation
        note_values = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
        acc_value = 1 if self.accidental == '#' else -1 if self.accidental == 'b' else 0
        
        # A4 = 440Hz
        semitones_from_a4 = (self.octave - 4) * 12 + note_values[self.letter_name] - 9 + acc_value
        return 440 * (2 ** (semitones_from_a4 / 12))

class Interpreter:
    def __init__(self, ast):
        self.ast = ast
        self.variables = {}
        self.macros = {}
        self.current_octave = 4
        self.current_tempo = 120  # Default tempo
        self.tracks = {}
        self.output = []
        
    def interpret(self):
        """Interpret the AST and return the results"""
        self._process_program(self.ast)
        return self.output
        
    def _process_program(self, program):
        """Process the Program node (root of AST)"""
        # Process metadata first
        if program.metadata:
            self._process_metadata(program.metadata)
            
        # Then process macros and variables
        for macro in program.macros:
            self._register_macro(macro)
            
        for variable in program.variables:
            self._register_variable(variable)
            
        # Finally process tracks
        for track in program.tracks:
            self._process_track(track)
    
    def _process_metadata(self, metadata):
        """Process metadata information"""
        if metadata.title:
            self.output.append(f"Title: {metadata.title}")
            
        if metadata.tempo:
            self.current_tempo = metadata.tempo
            self.output.append(f"Tempo: {self.current_tempo} BPM")
            
        if metadata.key:
            self.output.append(f"Key: {metadata.key}")
    
    def _register_macro(self, macro):
        """Register a macro definition"""
        self.macros[macro.name] = macro
        self.output.append(f"Registered macro: {macro.name} with {len(macro.parameters)} parameters")
    
    def _register_variable(self, variable):
        """Register a variable assignment"""
        if isinstance(variable.value, Note):
            self.variables[variable.name] = self._process_note(variable.value)
        else:
            # For other variable types if needed
            self.variables[variable.name] = variable.value
        self.output.append(f"Registered variable: {variable.name} = {self.variables[variable.name]}")
    
    def _process_track(self, track):
        """Process a track and its elements"""
        track_notes = []
        self.output.append(f"\nTrack: {track.name}")
        
        for element in track.elements:
            result = self._process_track_element(element)
            if result:
                if isinstance(result, list):
                    track_notes.extend(result)
                    for note in result:
                        self.output.append(f"  {note}:{note.duration}")
                else:
                    track_notes.append(result)
                    self.output.append(f"  {result}:{result.duration}")
        
        self.tracks[track.name] = track_notes
    
    def _process_track_element(self, element):
        """Process an individual track element"""
        if isinstance(element, Note):
            return self._process_note(element)
        elif isinstance(element, MacroCall):
            return self._expand_macro(element)
        elif isinstance(element, VariableReference):
            return self._resolve_variable(element)
        elif isinstance(element, Separator):
            return None  # Separators don't produce notes
    
    def _process_note(self, note):
        """Process a Note node"""
        # Check if this is a variable reference
        if note.value in self.variables:
            return self.variables[note.value]

        # Otherwise create a new note
        note_name = note.value.lower()

        # Extract duration if specified
        duration = 1.0  # Default duration
        if '*' in note_name:
            parts = note_name.split('*')
            note_name = parts[0]
            print("Important debug: "+ parts[1])
            try:
                duration = float(parts[1])
            except ValueError:
                print(f"Warning: Invalid duration multiplier: {parts[1]}")
        elif '/' in note_name:
            parts = note_name.split('/')
            note_name = parts[0]
            try:
                duration = 1.0 / float(parts[1])
            except (ValueError, ZeroDivisionError):
                print(f"Warning: Invalid duration divisor: {parts[1]}")

        # Check for accidentals 
        accidental = None
        if '#' in note_name:
            note_name = note_name.replace('#', '')
            accidental = '#'
        elif 'b' in note_name:
            note_name = note_name.replace('b', '')
            accidental = 'b'
            
        # Handle octave modifiers (like do5 for C in the 5th octave)
        octave = self.current_octave
        if len(note_name) > 1 and note_name[-1].isdigit():
            octave = int(note_name[-1])
            note_name = note_name[:-1]
        print(note_name + " " + str(octave) + " " + str(duration) + " " + str(accidental))
        return MusicNote(note_name, octave, duration, accidental=accidental)
    
    def _expand_macro(self, macro_call):
        """Expand a macro call into its constituent notes"""
        if macro_call.name not in self.macros:
            raise RuntimeError(f"Undefined macro: {macro_call.name}")
        
        macro = self.macros[macro_call.name]
        
        # Create a parameter binding
        bindings = {}
        for i, param_name in enumerate(macro.parameters):
            if i < len(macro_call.arguments):
                arg_value = macro_call.arguments[i]
                # If the argument is a variable, resolve it
                if arg_value in self.variables:
                    bindings[param_name] = self.variables[arg_value]
                else:
                    # Otherwise treat it as a note
                    bindings[param_name] = self._process_note(Note(arg_value))
        
        # Process the macro body with the bindings
        result = []
        for element in macro.body:
            if isinstance(element, Note):
                # If the note is a parameter, substitute it
                if element.value in bindings:
                    result.append(bindings[element.value])
                else:
                    result.append(self._process_note(element))
            elif isinstance(element, MacroCall):
                # Handle nested macro calls
                nested_result = self._expand_macro(element)
                if isinstance(nested_result, list):
                    result.extend(nested_result)
                else:
                    result.append(nested_result)
        
        return result
    
    def _resolve_variable(self, var_ref):
        """Resolve a variable reference"""
        if var_ref.name not in self.variables:
            raise RuntimeError(f"Undefined variable: {var_ref.name}")
        return self.variables[var_ref.name]


def interpret_music(ast):
    """Main function to interpret music AST"""
    interpreter = Interpreter(ast)
    return interpreter.interpret()