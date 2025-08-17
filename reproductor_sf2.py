# reproductor_sf2.py – Reproduce los datos extraídos desde un .sf2 usando PyAudio

import pyaudio
import numpy as np
from lector_samples_sf2 import extraer_seccion_smpl

def reproducir_sf2_sample(ruta_sf2):
    data = extraer_seccion_smpl(ruta_sf2)
    if data is None:
        print("No se encontró la sección de samples (smpl)")
        return

    audio = np.frombuffer(data, dtype=np.int16)  # PCM 16 bits
    p = pyaudio.PyAudio()

    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=44100,
                    output=True)

    stream.write(audio.tobytes())

    stream.stop_stream()
    stream.close()
    p.terminate()

if __name__ == "__main__":
    reproducir_sf2_sample("tests/test.sf2")
