from sf2utils.sf2parse import SF2File

def listar_presets(ruta_sf2):
    presets = []
    with open(ruta_sf2, 'rb') as f:
        sf2 = SF2File(f)
        for preset in sf2.presets:
            presets.append((preset.name, preset.bank, preset.preset))
    return presets
