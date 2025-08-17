# mapeo_midi.py – Mapeo básico de teclas MIDI a nombres de nota
def nota_a_nombre(nota):
    nombres = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    return nombres[nota % 12] + str(nota // 12)

def nombre_a_nota(nombre):
    nombres = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    nota = nombres.index(nombre[:-1])
    octava = int(nombre[-1])
    return nota + octava * 12
