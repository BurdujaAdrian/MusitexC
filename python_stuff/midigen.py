from new_parser import *
from ai_ast import *
from midiutil import MIDIFile


class gen_state:
    def __init__(self):
        self.oct = 4
        self.tempo = 60
        self.meas = (1, 4)
        self.dur = 1
        self.channel = 0
        self.volume = 100

        self.semitone_dict = {
            'r': 0,
            'C': 0, 'do': 0,
            'D': 0, 're': 0,
            'E': 0, 'mi': 0,
            'F': 0, 'fa': 0,
            'G': 0, 'sol': 0,
            'A': 0, 'la': 0,
            'B': 0, 'si': 0

        }

        self.time = 0


def gen_midi(ast, output):
    # print()
    # print()
    # print("generating midi:")
    if len(ast.tracks) == 1:
        # print("for only one track")
        gen_mono_track(ast, output)
    # else:
        # gen_multi_track(ast.tracks, ast.metadata)
    pass


def gen_mono_track(ast, output):
    track = ast.tracks[0]
    meta = ast.metadata

    midi = MIDIFile(1, True, True, False, 1)  # default values for 1 track
    midi.addTempo(0, 0, 120)  # default values

    midi.addTrackName(0, 0, track.name)  # add the name of the track

    for m_id, movement in enumerate(track.movements):

        if movement.instrument.value in midi_instruments.keys():
            program = midi_instruments[movement.instrument.value]
        else:
            ast.err_list.append(f"""Compilation error: instrument \"{movement.instrument.value}\" is not supported
Tip: You can choose instruments like piano,guitar etc.
Tip: All the midi instruments are supported""")
        midi.addProgramChange(0, m_id, 0, program)

        state = gen_state()

        for e_id, event in enumerate(movement.expressions):
            if isinstance(event, Note):
                volume = state.volume

                if event.value.value.lower() == 'r':
                    # handle rests
                    # print("	no, it's a rest")
                    volume = 0

                note = event.value.value.lower()
                note_n = note_to_midi[note]
                # print(f"	note id: {note_n}")

                semitone = state.semitone_dict[note] if event.semitone == 999 else event.semitone
                octave = state.oct if event.octave == -1 else event.octave
                pitch = note_n + semitone + 12 * octave
                # print(f"	resulting pitch: {pitch}")

                duration = state.dur if event.duration == -1 else event.duration
                if isinstance(duration, Fraction):
                    duration = duration.x / duration.over
                duration *= 4

                if pitch < 0 or pitch > 127:
                    print(
                        f"WARNING: MIDI pitch {pitch} out of range for note {note}, octave {octave}, semitone {semitone}. Clamping to valid range.")
                pitch = max(0, min(127, pitch))
                midi.addNote(0, m_id, pitch, state.time, duration, volume)

                state.time += duration

                pass

            elif isinstance(event, SetMeasure):
                pass
                # print(f"	found measure{event}")
                # print()

            elif isinstance(event, ReleaseNote):
                pass
            elif isinstance(event, SetTone):
                note_name = event.note.value.lower()
                state.semitone_dict[note_name] = event.n


            elif isinstance(event, HoldNote):
                # If the event.note is a Chord, handle each note in the chord
                if isinstance(event.note, Chord):
                    for note_e in event.note.notes:
                        volume = state.volume

                        if note_e.value.value.lower() == 'r':
                            volume = 0
                            note_e.value.value = "do"  # or leave as is

                        note = note_e.value.value.lower()
                        note_n = note_to_midi[note]
                        semitone = state.semitone_dict[note] if note_e.semitone == 999 else note_e.semitone
                        octave = state.oct if note_e.octave == -1 else note_e.octave
                        pitch = note_n + semitone + 12 * octave
                        if pitch < 0 or pitch > 127:
                            print(
                                f"WARNING: MIDI pitch {pitch} out of range for note {note}, octave {octave}, semitone {semitone}. Clamping to valid range.")
                        pitch = max(0, min(127, pitch))

                        duration = state.dur if note_e.duration == -1 else note_e.duration
                        if isinstance(duration, Fraction):
                            duration = duration.x / duration.over

                        duration = duration * 4
                        midi.addNote(0, m_id, pitch, state.time, duration, volume)
                    state.time += duration
                # If the event.note is a single Note, handle as single note
                elif isinstance(event.note, Note):
                    note_e = event.note
                    volume = state.volume

                    if note_e.value.value.lower() == 'r':
                        volume = 0
                        note_e.value.value = "do"

                    note = note_e.value.value.lower()
                    note_n = note_to_midi[note]
                    semitone = state.semitone_dict[note] if note_e.semitone == 999 else note_e.semitone
                    octave = state.oct if note_e.octave == -1 else note_e.octave
                    pitch = note_n + semitone + 12 * octave
                    if pitch < 0 or pitch > 127:
                        print(
                            f"WARNING: MIDI pitch {pitch} out of range for note {note}, octave {octave}, semitone {semitone}. Clamping to valid range.")
                    pitch = max(0, min(127, pitch))


                    duration = state.dur if note_e.duration == -1 else note_e.duration
                    if isinstance(duration, Fraction):
                        duration = duration.x / duration.over

                    duration = duration * 4
                    midi.addNote(0, m_id, pitch, state.time, duration, volume)
                    state.time += duration
                # Optionally: handle Ident or MacroCall if those appear
                else:
                    ast.err_list.append("HoldNote of unsupported type: " + str(type(event.note)))


            elif isinstance(event, SetVolume):
                state.volume = event.vol
            elif isinstance(event, SetTempo):
                state.tempo = event.n

            elif isinstance(event, SetOctave):
                state.oct += event.n * event.dir

            elif isinstance(event, SetDuration):
                duration = event.dur
                if isinstance(duration, Fraction):
                    duration = duration.x / duration.over

                state.dur = duration

            elif isinstance(event, Bar):
                pass
                # print(f"	found bar")
                # print()

            elif isinstance(event, Chord):
                duration = 0
                for note_e in event.notes:
                    # handle note event
                    # print(f"ound note {note_e}")

                    volume = state.volume

                    if note_e.value.value.lower() == 'r':
                        # handle rests
                        # print("	no, it's a rest")
                        volume = 0
                        note_e.value.value = "do"

                    note = note_e.value.value.lower()
                    note_n = note_to_midi[note]
                    # print(f"	note id: {note_n}")

                    semitone = state.semitone_dict[note] if note_e.semitone == 999 else note_e.semitone
                    octave = state.oct if note_e.octave == -1 else note_e.octave
                    pitch = note_n + semitone + 12 * octave
                    # print(f"	resulting pitch: {pitch}")

                    if pitch < 0 or pitch > 127:
                        print(
                            f"WARNING: MIDI pitch {pitch} out of range for note {note}, octave {octave}, semitone {semitone}. Clamping to valid range.")
                    pitch = max(0, min(127, pitch))
                    duration = state.dur if note_e.duration == -1 else note_e.duration
                    if isinstance(duration, Fraction):
                        duration = duration.x / duration.over

                    duration = duration * 4

                    midi.addNote(0, m_id, pitch, state.time, duration, volume)

                state.time += duration


            elif isinstance(event, SetInterval):
                # Interpret the interval as a number (e.g., beats or quarter notes)
                interval = int(event.time.value) if hasattr(event.time, "value") else int(event.time)
                # Advance state.time by interval (assuming units are quarter notes, adjust as needed)
                state.time += interval

            else:
                raise ValueError(f"	Unhandled event type in movement:{event}")

    with open(output, "wb") as output_file:
        midi.writeFile(output_file)

    pass


note_to_midi = {
    'r': 0,  # rest is just a silent note
    'C': 0, 'do': 0,
    'D': 2, 're': 2,
    'E': 4, 'mi': 4,
    'F': 5, 'fa': 5,
    'G': 7, 'sol': 7,
    'A': 9, 'la': 9,
    'B': 11, 'si': 11
}

midi_instruments = {
    # Piano (0-7)
    'piano': 0,  # default piano
    'acoustic_grand_piano': 0,
    'bright_acoustic_piano': 1,
    'electric_grand_piano': 2,
    'honkytonk_piano': 3,
    'electric_piano_1': 4,
    'electric_piano_2': 5,
    'harpsichord': 6,
    'clavinet': 7,

    # Chromatic Percussion (8-15)
    'celesta': 8,
    'glockenspiel': 9,
    'music_box': 10,
    'vibraphone': 11,
    'marimba': 12,
    'xylophone': 13,
    'tubular_bells': 14,
    'dulcimer': 15,

    # Organ (16-23)
    'organ': 16,
    'drawbar_organ': 16,
    'percussive_organ': 17,
    'rock_organ': 18,
    'church_organ': 19,
    'reed_organ': 20,
    'accordion': 21,
    'harmonica': 22,
    'tango_accordion': 23,

    # Guitar (24-31)
    'guitar': 24,
    'acoustic_guitar_nylon': 24,
    'acoustic_guitar_steel': 25,
    'electric_guitar_jazz': 26,
    'electric_guitar_clean': 27,
    'electric_guitar_muted': 28,
    'overdriven_guitar': 29,
    'distortion_guitar': 30,
    'guitar_harmonics': 31,

    # Bass (32-39)
    'bass': 32,
    'acoustic_bass': 32,
    'electric_bass_finger': 33,
    'electric_bass_pick': 34,
    'fretless_bass': 35,
    'slap_bass_1': 36,
    'slap_bass_2': 37,
    'synth_bass_1': 38,
    'synth_bass_2': 39,

    # Strings (40-47)
    'violin': 40,
    'viola': 41,
    'cello': 42,
    'contrabass': 43,
    'tremolo_strings': 44,
    'pizzicato_strings': 45,
    'orchestral_harp': 46,
    'timpani': 47,

    # Ensemble (48-55)
    'string_ensemble_1': 48,
    'string_ensemble_2': 49,
    'synth_strings_1': 50,
    'synth_strings_2': 51,
    'choir_aahs': 52,
    'voice_oohs': 53,
    'synth_choir': 54,
    'orchestra_hit': 55,

    # Brass (56-63)
    'trumpet': 56,
    'trombone': 57,
    'tuba': 58,
    'muted_trumpet': 59,
    'french_horn': 60,
    'brass_section': 61,
    'synth_brass_1': 62,
    'synth_brass_2': 63,

    # Reed (64-71)
    'soprano_sax': 64,
    'alto_sax': 65,
    'tenor_sax': 66,
    'baritone_sax': 67,
    'oboe': 68,
    'english_horn': 69,
    'bassoon': 70,
    'clarinet': 71,

    # Pipe (72-79)
    'piccolo': 72,
    'flute': 73,
    'recorder': 74,
    'pan_flute': 75,
    'blown_bottle': 76,
    'shakuhachi': 77,
    'whistle': 78,
    'ocarina': 79,

    # Synth Lead (80-87)
    'lead_1_square': 80,
    'lead_2_sawtooth': 81,
    'lead_3_calliope': 82,
    'lead_4_chiff': 83,
    'lead_5_charang': 84,
    'lead_6_voice': 85,
    'lead_7_fifths': 86,
    'lead_8_bass_lead': 87,

    # Synth Pad (88-95)
    'pad_1_new_age': 88,
    'pad_2_warm': 89,
    'pad_3_polysynth': 90,
    'pad_4_choir': 91,
    'pad_5_bowed': 92,
    'pad_6_metallic': 93,
    'pad_7_halo': 94,
    'pad_8_sweep': 95,

    # Synth Effects (96-103)
    'fx_1_rain': 96,
    'fx_2_soundtrack': 97,
    'fx_3_crystal': 98,
    'fx_4_atmosphere': 99,
    'fx_5_brightness': 100,
    'fx_6_goblins': 101,
    'fx_7_echoes': 102,
    'fx_8_scifi': 103,

    # Ethnic (104-111)
    'sitar': 104,
    'banjo': 105,
    'shamisen': 106,
    'koto': 107,
    'kalimba': 108,
    'bagpipe': 109,
    'fiddle': 110,
    'shanai': 111,

    # Percussive (112-119)
    'tinkle_bell': 112,
    'agogo': 113,
    'steel_drums': 114,
    'woodblock': 115,
    'taiko_drum': 116,
    'melodic_tom': 117,
    'synth_drum': 118,
    'reverse_cymbal': 119,

    # Sound Effects (120-127)
    'guitar_fret_noise': 120,
    'breath_noise': 121,
    'seashore': 122,
    'bird_tweet': 123,
    'telephone_ring': 124,
    'helicopter': 125,
    'applause': 126,
    'gunshot': 127
}
