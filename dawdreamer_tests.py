import dawdreamer as daw
import soundfile as sf
import os
import numpy as np
import mido


def render_bbcsymphony_vst(midi_path, output_path, vst_path, preset_path=None, duration=120.0, sample_rate=44100, block_size=512):

    # Step 1: Verify file paths
    if not os.path.exists(midi_path):
        raise FileNotFoundError(f"MIDI file not found: {midi_path}")
    if not os.path.exists(vst_path):
        raise FileNotFoundError(f"VST plugin not found: {vst_path}")
    print("1: File paths verified")

    # Step 2: Check MIDI file channels
    midi_file = mido.MidiFile(midi_path)
    channels = set()
    for track_idx, track in enumerate(midi_file.tracks):
        for msg_idx, msg in enumerate(track):
            if msg.type in ['note_on', 'note_off']:
                channels.add(msg.channel)
    if not channels:
        raise ValueError("MIDI file contains no note data")
    print("2: Midi Channel verified")

    # Step 3: Create render engine
    engine = daw.RenderEngine(sample_rate=sample_rate, block_size=block_size)
    print("3: Render engine created")

    # Step 4: Create plugin processor
    plugin = engine.make_plugin_processor("BBCSO", vst_path)
    # plugin.open_editor() # --- test if the plugin is loaded correctly
    if not plugin:
        raise RuntimeError("Failed to load BBC Symphony Orchestra VST")
    print("4: Plugin processor created")

    # Step 5: Load preset or set instrument parameters
    if preset_path and os.path.exists(preset_path):
        plugin.load_preset(preset_path)
        print("5: Preset loaded")
    else:
        plugin.set_parameter(0, 0.0)
        plugin.set_parameter(1, 0.8)
        plugin.set_parameter(2, 0.0)
        print("5: Instrument parameters set (strings)")

    # Step 6: Create silent audio for PlaybackProcessor
    silent_audio = np.zeros((2, int(sample_rate * duration)), dtype=np.float32)
    playback = engine.make_playback_processor("Playback", silent_audio)
    print("6: Playback processor created")

    # Step 7: Load MIDI into plugin
    plugin.load_midi(midi_path, clear_previous=True, beats=False, all_events=True)
    print("7: MIDI loaded into plugin")

    # Step 8: Load processing graph
    engine.load_graph([
        (playback, []),
        (plugin, [])
    ])
    print("8: Processing graph created")

    # Step 9: Render audio and get output
    engine.render(duration)
    audio = engine.get_audio()
    if audio is None or np.all(audio == 0):
        raise RuntimeError("Rendered audio is None or silent (all zeros). Check VST license, MIDI channels, or preset.")

    # Step 10: Ensure output directory exists
    out_dir = os.path.dirname(output_path)
    os.makedirs(out_dir, exist_ok=True)
    print("10: Output directory ensured")

    # Step 11: Save WAV file
    sf.write(output_path, audio.transpose(), sample_rate, subtype='PCM_24')
    print(f"11: WAV file saved to {output_path}")

    return True

if __name__ == "__main__":
    midi_path = r"midis\midi1.mid"
    output_path = r"waves\output.wav"
    vst_path = r"C:\Program Files\Steinberg\VSTPlugins\BBC Symphony Orchestra (64 Bit).dll"
    preset_path = None

    render_bbcsymphony_vst(midi_path, output_path, vst_path, preset_path, duration=120.0)
