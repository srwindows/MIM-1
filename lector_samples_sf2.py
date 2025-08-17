import struct

def leer_chunk(file, chunk_id):
    """Busca un chunk específico y devuelve su posición y tamaño."""
    file.seek(0)
    while True:
        data = file.read(8)
        if len(data) < 8:
            break
        chunk_type, chunk_size = struct.unpack('<4sI', data)
        if chunk_type == chunk_id:
            return file.tell(), chunk_size
        file.seek(chunk_size, 1)
    return None, None

def leer_lista_chunks(file):
    """Devuelve una lista de todos los chunks (tipo, posición, tamaño) en el archivo."""
    file.seek(0)
    chunks = []
    while True:
        data = file.read(8)
        if len(data) < 8:
            break
        chunk_type, chunk_size = struct.unpack('<4sI', data)
        pos = file.tell()
        chunks.append((chunk_type, pos, chunk_size))
        file.seek(chunk_size, 1)
    return chunks

def extraer_samples_sf2(ruta_sf2):
    """Extrae el bloque de samples 'smpl' del archivo SF2 y lo devuelve como bytes."""
    with open(ruta_sf2, "rb") as f:
        while True:
            data = f.read(8)
            if len(data) < 8:
                break
            chunk_type, chunk_size = struct.unpack('<4sI', data)
            if chunk_type == b'smpl':
                return f.read(chunk_size)
            f.seek(chunk_size, 1)
    return None

def extraer_lista_presets(ruta_sf2):
    """Devuelve una lista de presets encontrados en el archivo SF2."""
    # Nota: Esto es un ejemplo, la implementación depende de tu estructura SF2.
    # Aquí solo se devuelven nombres dummy.
    return [("Piano", 0, 0), ("Guitarra", 0, 24), ("Bajo", 0, 32)]

def cargar_samples_sf2(ruta_sf2):
    """Carga todos los samples (bloque 'smpl') y los devuelve como lista de arrays."""
    # Implementación ficticia, depende de la estructura real del SF2.
    raw = extraer_samples_sf2(ruta_sf2)
    if not raw:
        return []
    # Divídelo en fragmentos de ejemplo (no real parsing).
    fragmentos = [raw[i:i+512] for i in range(0, len(raw), 512)]
    return fragmentos

def info_basica_sf2(ruta_sf2):
    """Devuelve información básica del archivo SF2."""
    # Ejemplo dummy
    return {
        "ruta": ruta_sf2,
        "num_presets": 10,
        "num_samples": 256,
        "fabricante": "Desconocido"
    }

# ---------------------------
# ⬇️ FUNCIÓN NECESARIA PARA MOTORSONIDO (NO TOCAR EL RESTO)
# ---------------------------
def extraer_seccion_smpl(ruta_sf2):
    """
    Devuelve la sección de samples 'smpl' de un archivo SF2 como bytes.
    Compatible con MotorSonido (busca el chunk 'smpl').
    """
    with open(ruta_sf2, "rb") as f:
        while True:
            data = f.read(8)
            if len(data) < 8:
                break
            chunk_type, chunk_size = struct.unpack('<4sI', data)
            if chunk_type == b'smpl':
                return f.read(chunk_size)
            f.seek(chunk_size, 1)
    return None
# ---------------------------
# ⬆️ FIN DE LA FUNCIÓN AÑADIDA
# ---------------------------
