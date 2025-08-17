


import sounddevice as sd
import numpy as np

# Frecuencia de la nota (por ejemplo, 440 Hz = La4)
frec = 440
# Duración en segundos
dur = 1.0
# Frecuencia de muestreo
fs = 44100

# Generar onda seno simple (¡esto es un beep!)
t = np.linspace(0, dur, int(fs * dur), False)
onda = 0.5 * np.sin(2 * np.pi * frec * t)

print("¡Suena 1 segundo!")
sd.play(onda, fs)
sd.wait()
