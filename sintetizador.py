import sounddevice as sd
import numpy as np
import threading
import wave
import os

class Sintetizador:
    def __init__(self):
        self.instrumentos_canal = {}  # canal -> (banco, preset, archivo, muestra)
        self.salida_actual = np.zeros(1, dtype=np.int16)

    def cargar_instrumento_sf2(self, archivo, banco, preset, canal):
        muestra = self.extraer_muestra_prueba()
        if muestra is not None:
            self.instrumentos_canal[canal] = (banco, preset, archivo, muestra)
            print(f"[OK] Cargado SF2 preset {preset} del banco '{banco}' en canal 'canal{canal}'")
        else:
            print(f"[ERROR al cargar muestras SF2] Archivo no encontrado: {archivo}")

    def asignar_a_canal(self, canal, nombre_canal):
        print(f"[OK] Asignado '{nombre_canal}' al canal {canal + 1}")

    def reproducir_nota(self, canal, nota_midi):
        if canal not in self.instrumentos_canal:
            print(f"[Canal {canal}] No hay instrumento asignado")
            return
        banco, preset, archivo, muestra = self.instrumentos_canal[canal]
        print(f"[SF2] Reproduciendo nota {nota_midi} del preset {preset} de '{banco}' (ruta: {archivo})")
        self.reproducir_muestra(muestra)

    def extraer_muestra_prueba(self):
        ruta = os.path.expanduser("~/MIM-1-MODULAR/Muestras/note60.wav")
        if os.path.exists(ruta):
            with wave.open(ruta, "rb") as wav:
                frames = wav.readframes(wav.getnframes())
                datos = np.frombuffer(frames, dtype=np.int16)
                return datos
        return None

    def reproducir_muestra(self, datos):
        if datos is None or len(datos) == 0:
            print("[ERROR] Muestra vacía o nula")
            return
        self.salida_actual = datos
        threading.Thread(target=lambda: sd.play(datos, 44100, blocking=True), daemon=True).start()