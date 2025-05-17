from midiutil import MIDIFile
from interpreter import MusicNote
import os

class MIDIGenerator:
    NOTE_TO_MIDI = {
        'C': 0, 'C#': 1, 'Db': 1,
        'D': 2, 'D#': 3, 'Eb': 3,
        'E': 4, 
        'F': 5, 'F#': 6, 'Fb': 6,
        'G': 7, 'G#': 8, 'Gb': 8,
        'A': 9, 'A#': 10, 'Ab': 10,
        'B': 11, 'Bb': 10, 'Cb': 11
    }
    
    def __init__(self, tracks, tempo=120):
        self.tracks = tracks
        self.tempo = tempo
        self.midi = MIDIFile(len(tracks))
        
    def note_to_midi_number(self, note):
        """Convert a MusicNote to MIDI note number"""
        if not isinstance(note, MusicNote):
            raise TypeError(f"Expected MusicNote, got {type(note)}")
        
        base_note = note.letter_name
        if note.accidental:
            base_note += note.accidental
            
        # Get the base note value (0-11)
        base_value = self.NOTE_TO_MIDI.get(base_note, 0)
        
        # Calculate the MIDI note number (C4 = 60)
        return base_value + (note.octave + 1) * 12
    
    def generate(self, filename="music_output.mid"):
        """Generate a MIDI file from the tracks"""
        # Set up tracks in MIDI file
        for i, (track_name, notes) in enumerate(self.tracks.items()):
            self.midi.addTrackName(i, 0, track_name)
            self.midi.addTempo(i, 0, self.tempo)
            
            # Add notes to track
            time = 0
            for note in notes:
                if isinstance(note, MusicNote):
                    midi_note = self.note_to_midi_number(note)
                    # Arguments: track, channel, note, time, duration, volume
                    print(f"Adding note {note} with duration {note.duration} at time {time}")
                    self.midi.addNote(i, 0, midi_note, time, note.duration, 100)
                    time += note.duration
        
        # Write the MIDI file
        with open(filename, 'wb') as output_file:
            self.midi.writeFile(output_file)
            
        return os.path.abspath(filename)

def generate_midi_from_interpreter_output(interpreter_output, filename="music_output.mid"):
    """Generate MIDI file from interpreter output"""
    # Extract tempo
    tempo = 120  # Default tempo
    for line in interpreter_output:
        if line.startswith("Tempo:"):
            try:
                tempo = int(line.split(":")[-1].strip().split()[0])
            except (ValueError, IndexError):
                pass
    
    # Extract tracks
    tracks = {}
    current_track = None
    print(interpreter_output)
    for line in interpreter_output:
        if line.startswith("\nTrack:"):
            current_track = line.split(":")[-1].strip()
            tracks[current_track] = []
        elif line.startswith("  ") and current_track:
            # Here we need to parse the note output string to recreate MusicNote objects
            note_str = line.strip()
            
            # Check if it matches a note pattern (simple implementation - can be enhanced)
            if len(note_str) > 0 and note_str[0] in 'ABCDEFG':
                # Extract the note letter and octave
                letter = note_str[0]
                
                # Check for accidental
                accidental = None
                idx = 1
                if idx < len(note_str) and note_str[idx] in '#b':
                    accidental = note_str[idx]
                    idx += 1
                
                # Get octave
                octave = 4  # Default octave
                if idx < len(note_str) and note_str[idx].isdigit():
                    octave = int(note_str[idx])
                    
                duration = 1.0  # Default duration
                
                # Look for duration information in the note_str
                # This is assuming the interpreter outputs notes in a format like "C4*2.0" 
                remaining = note_str[idx:].strip()
                if ':' in remaining:
                    try:
                        duration = float(remaining.split(':')[1])
                    except (ValueError, IndexError):
                        pass
                
                # Create MusicNote object
                note = MusicNote(letter, octave, duration, accidental)
                tracks[current_track].append(note)
    
    # Generate MIDI
    print("Debug: Tracks found: ", tracks)
    print("Debug: Tempo found: ", tempo)
    print("Debug: Generating MIDI file...")
    if tracks:
        generator = MIDIGenerator(tracks, tempo)
        return generator.generate(filename)
    else:
        return "No tracks found to generate MIDI file"

if __name__ == "__main__":
    from test import main
    
    # Run the interpreter
    output = main()
    
    # Generate MIDI from the output
    midi_path = generate_midi_from_interpreter_output(output)
    print(f"\nMIDI file generated: {midi_path}")