import os
from mido import Message, MidiFile, MidiTrack

# Generate note name → MIDI number for the full range
NOTE_NAMES = {}
note_order = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
for octave in range(0, 10):  # C0 (MIDI 12) to G9 (MIDI 127)
    for i, note in enumerate(note_order):
        midi_number = 12 + i + octave * 12
        if midi_number > 127:  # MIDI max note
            break
        NOTE_NAMES[f"{note}{octave}"] = midi_number

def create_midi(notes, base_name="midi", ext=".mid", quarter_note=480, subfolder="midis"):
    """
    Create a MIDI file from a list of note names, saved in a subfolder.

    Args:
        notes (list of str): Note names (e.g., ["C4", "D4", "E4", "C4"])
        base_name (str): Base name for the file (default "midi")
        ext (str): File extension (default ".mid")
        quarter_note (int): Duration of a quarter note in ticks (default 480)
        subfolder (str): Name of the subfolder to save MIDI files
    """
    try:
        midi_notes = [NOTE_NAMES[n] for n in notes]
    except KeyError as e:
        raise ValueError(f"Invalid note name: {e}")

    # Ensure subfolder exists
    os.makedirs(subfolder, exist_ok=True)

    # Find next available filename
    i = 1
    while os.path.exists(os.path.join(subfolder, f"{base_name}{i}{ext}")):
        i += 1
    filename = os.path.join(subfolder, f"{base_name}{i}{ext}")

    # Create MIDI file and track
    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)

    for note in midi_notes:
        track.append(Message('note_on', note=note, velocity=64, time=0))
        track.append(Message('note_off', note=note, velocity=64, time=quarter_note))

    mid.save(filename)
    print(f"MIDI file created: {filename}")
    return filename

# Usage
#create_midi(["C4", "D4", "E4", "C4", "G5", "A3", "F#6"])
