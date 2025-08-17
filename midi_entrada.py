import mido
import threading

class EntradaMIDI:
    def __init__(self, callback_nota):
        self.callback_nota = callback_nota
        self.hilo = threading.Thread(target=self.escuchar, daemon=True)
        self.hilo.start()

    def escuchar(self):
        try:
            entrada = mido.open_input()
            for mensaje in entrada:
                if mensaje.type == "note_on" and mensaje.velocity > 0:
                    self.callback_nota(mensaje.note)
        except Exception as e:
            print("Error al leer MIDI:", e)
