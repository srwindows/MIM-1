from sf2utils.sf2parse import Sf2File

def extraer_presets_desde_sf2(ruta_sf2):
    instrumentos = []
    try:
        with open(ruta_sf2, 'rb') as f:
            sf2 = Sf2File(f)
            for preset in sf2.presets:
                nombre = preset.name.strip()
                banco = preset.bank
                programa = preset.preset
                instrumentos.append({
                    "nombre": nombre,
                    "banco": banco,
                    "programa": programa
                })
    except Exception as e:
        print(f"Error al leer SF2: {e}")
    return instrumentos
