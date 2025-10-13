import os
import dawdreamer as daw
import mido
import soundfile as sf

def midi_to_wav(
    midi_path: str,
    vst_path: str,
    output_path: str,
    preset_path: str = None,
    duration: float = 10.0,
    sample_rate: int = 44100,
    block_size: int = 512
):
    """Renderiza um arquivo MIDI usando um VST e salva como WAV."""
    # --- Ler MIDI ---
    midi_file = mido.MidiFile(midi_path)
    note_count = sum(1 for track in midi_file.tracks for msg in track if msg.type in ['note_on', 'note_off'])
    print(f"MIDI carregado, {note_count} notas encontradas.")

    # --- Criar motor e plugin ---
    engine = daw.RenderEngine(sample_rate=sample_rate, block_size=block_size)
    plugin = engine.make_plugin_processor("Plugin", vst_path)
    if not plugin:
        raise RuntimeError("Falha ao carregar o VST")

    # --- Carregar preset ---
    if preset_path and os.path.exists(preset_path):
        plugin.load_preset(preset_path)
        print(f"Preset carregado: {preset_path}")
    else:
        print("Preset não encontrado, plugin usará padrão (pode ser mudo)")

    # --- Carregar MIDI ---
    plugin.load_midi(midi_path, clear_previous=True, beats=False, all_events=True)
    print(f"MIDI carregado no plugin. Eventos: {plugin.n_midi_events}")

    # --- Criar gráfico ---
    engine.load_graph([(plugin, [])])
    print("Gráfico carregado, pronto para renderizar.")

    # --- Renderizar áudio ---
    print(f"Renderizando {duration} segundos de áudio...")
    engine.render(duration)
    audio = engine.get_audio()
    print(f"Renderização concluída. Formato: {audio.shape}, max={audio.max()}")

    # --- Salvar WAV ---
    sf.write(output_path, audio.transpose(), sample_rate, subtype='PCM_24')
    print(f"WAV salvo em: {output_path}")


if __name__ == "__main__":
    midi_to_wav(
        midi_path=r"D:\testes mestrado\DAW-tests\midis\midi1.mid",
        vst_path=r"C:\Program Files\VstPlugins\Dexed.dll",
        preset_path=r"C:\Users\aline\Dexed_Patches\PianoPatch.xfd",
        output_path=r"D:\testes mestrado\DAW-tests\waves\output.wav",
        duration=10.0
    )

