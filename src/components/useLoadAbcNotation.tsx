import { useEffect } from "react";
// Adjust this import to the path of your midi2abc.js (make sure it's accessible as a module)
import midi2abc from "./midi2abc";

type SetAbcNotation = (abc: string) => void;

export const useLoadAbcNotation = (setAbcNotation: SetAbcNotation) => {
  useEffect(() => {
    const fetchAndConvert = async () => {
      try {
        const response = await fetch("http://localhost:8000/api/compile", { method: "POST" });
        const contentType = response.headers.get("content-type") || "";
        if (!response.ok || !contentType.includes("audio/midi")) {
          throw new Error("MIDI file not returned");
        }
        const blob = await response.blob();
        const arrayBuffer = await blob.arrayBuffer();
        const { Midi } = await import("@tonejs/midi");
        const midi = new Midi(arrayBuffer);

        // Convert Tone.js Midi to NoteSequence-like object
        const toneMidiToNoteSequence = (midi: any) => {
          const notes: any[] = [];
          midi.tracks.forEach((track: any, trackIdx: number) => {
            track.notes.forEach((note: any) => {
              notes.push({
                instrument: trackIdx,
                program: track.instrument.number || 0,
                startTime: note.time,
                endTime: note.time + note.duration,
                pitch: note.midi,
                velocity: Math.round(note.velocity * 127),
                isDrum: false,
              });
            });
          });
          const tempos =
            midi.header.tempos && midi.header.tempos.length > 0
              ? midi.header.tempos.map((t: any) => ({
                  time: t.ticks !== undefined ? midi.header.ticksToSeconds(t.ticks) : t.time,
                  qpm: t.bpm,
                }))
              : [{ time: 0, qpm: 120 }];
          const totalTime = midi.duration;
          return {
            notes,
            tempos,
            totalTime,
            timeSignatures: [
              {
                time: 0,
                numerator: midi.header.timeSignatures[0]?.numerator || 4,
                denominator: midi.header.timeSignatures[0]?.denominator || 4,
              },
            ],
          };
        };

        const ns = toneMidiToNoteSequence(midi);
        const abc = midi2abc(ns);
        setAbcNotation(abc);
      } catch (err) {
        console.error("Failed to load or convert MIDI:", err);
        setAbcNotation("X:1\nT:Error loading ABC\nM:4/4\nK:C\nC D E F|G A B c|");
      }
    };
    fetchAndConvert();
  }, [setAbcNotation]);
};