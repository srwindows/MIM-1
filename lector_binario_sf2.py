# lector_binario_sf2.py
# Lista los instrumentos/presets de un archivo SF2 General MIDI compatible

import struct

def listar_presets_sf2(ruta_sf2):
    presets = []
    try:
        with open(ruta_sf2, "rb") as f:
            data = f.read()
        phdr_idx = data.find(b'phdr')
        if phdr_idx == -1:
            return []
        # El número de presets es la cantidad de bloques menos uno (finalizador)
        preset_bytes = 38
        n = (data.find(b'pbag') - (phdr_idx + 8)) // preset_bytes
        off = phdr_idx + 8
        for i in range(n):
            bloque = data[off:off+38]
            nombre = bloque[:20].split(b'\0')[0].decode(errors='replace')
            preset = struct.unpack("<H", bloque[20:22])[0]
            banco = struct.unpack("<H", bloque[22:24])[0]
            presets.append((nombre, banco, preset))
            off += 38
        return presets
    except Exception as e:
        print(f"[lector_binario_sf2] Error: {e}")
        return []
