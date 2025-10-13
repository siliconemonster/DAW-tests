# BBC Symphony Orchestra - Renderização em Lote via Reaper ReaScript (versão final)
# Requer: Python habilitado no Reaper (Options > Preferences > ReaScript > Python)

from reaper_python import *
import os
import time

# --- Função de espera segura ---
def wait_for_plugin(seconds=3.0, step=0.1):
    """
    Espera enquanto processa o Reaper internamente,
    evitando travar a GUI ou gerar renderizações vazias.
    """
    elapsed = 0.0
    while elapsed < seconds:
        RPR_UpdateTimeline()  # força Reaper a processar eventos
        time.sleep(step)
        elapsed += step

# --- Configurações ---
midi_files = [
    r"D:\testes mestrado\DAW-tests\midis\midi28.mid",
    r"D:\testes mestrado\DAW-tests\midis\midi29.mid",
    r"D:\testes mestrado\DAW-tests\midis\midi30.mid"
]
vst_name = "BBC Symphony Orchestra (64 Bit)"
vst_path = r"C:\Program Files\Steinberg\VSTPlugins\BBC Symphony Orchestra (64 Bit).dll"
output_dir = r"D:\testes mestrado\DAW-tests\waves"
preset_name = "Full Orchestra"
render_length_seconds = 10.0
wait_seconds = 3.0  # tempo de espera para carregar o VST

# --- Loop pelos arquivos MIDI ---
for midi_path in midi_files:
    midi_name = os.path.splitext(os.path.basename(midi_path))[0]
    output_path = os.path.join(output_dir, f"{midi_name}_bbc.wav")

    RPR_ShowConsoleMsg(f"\n Processando: {midi_name}\n")

    # --- Criar track temporária ---
    RPR_InsertTrackAtIndex(0, True)
    track = RPR_GetTrack(0, 0)

    # --- Inserir plugin ---
    fx_index = RPR_TrackFX_AddByName(track, vst_name, False, -1)
    if fx_index == -1:
        fx_index = RPR_TrackFX_AddByName(track, vst_path, False, -1)
    if fx_index == -1:
        RPR_ShowConsoleMsg(f" Falha ao carregar o VST para {midi_name}\n")
        RPR_DeleteTrack(track)
        continue

    # --- Selecionar preset ---
    RPR_TrackFX_SetPreset(track, fx_index, preset_name)
    RPR_ShowConsoleMsg(f" Preset selecionado: {preset_name}\n")

    # --- Importar MIDI ---
    RPR_InsertMedia(midi_path, 0)
    item = RPR_GetTrackMediaItem(track, 0)
    if not item:
        RPR_ShowConsoleMsg(f" Falha ao importar MIDI: {midi_path}\n")
        RPR_DeleteTrack(track)
        continue

    RPR_SetMediaItemInfo_Value(item, "D_POSITION", 0.0)
    RPR_SetMediaItemInfo_Value(item, "D_LENGTH", render_length_seconds)

    # --- Cursor em 0 ---
    RPR_SetEditCurPos(0.0, False, False)

    # --- Garantir que o arquivo de saída será sobrescrito ---
    if os.path.exists(output_path):
        os.remove(output_path)

    # --- Espera segura para carregar o VST ---
    RPR_ShowConsoleMsg(f" Aguardando {wait_seconds}s para inicialização do VST...\n")
    wait_for_plugin(wait_seconds)

    # --- Renderizar ---
    RPR_GetSetProjectInfo_String(0, "RENDER_FILE", output_path, True)
    RPR_ShowConsoleMsg(f" Renderizando: {output_path}\n")
    RPR_Main_OnCommand(41824, 0)  # File: Render project to disk (WAV)

    # --- Espera breve para garantir finalização do render ---
    wait_for_plugin(1.0)

    # --- Remover track ---
    RPR_DeleteTrack(track)
    RPR_ShowConsoleMsg(" Track temporária removida.\n")

    RPR_ShowConsoleMsg(f" Renderização concluída: {output_path}\n")

# --- Final ---
RPR_SetEditCurPos(0.0, False, False)
RPR_ShowConsoleMsg("\n Processamento finalizado para todos os MIDIs!\n")
