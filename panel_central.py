from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import os

from piano import PianoWidget
from panel_inferior import PanelInferior
from sintetizador import Sintetizador
from midi_entrada import EntradaMIDI

class PanelCentral(QWidget):
    def __init__(self, motor_sonido=None):
        super().__init__()
        self.setMinimumSize(50, 50)
        self.setMaximumSize(1700, 1000)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.instrumento_actual = (0, 0, "")
        self.canal_activo = 0   # <-- NUEVO: Canal activo (para polifonía real y panel inferior)
        self.motor_sonido = motor_sonido  # <-- ADAPTADO: Motor polifónico
        self.sintetizador = Sintetizador()
        self.midi = EntradaMIDI(self.reproducir_nota)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        self.setLayout(layout)

        self.nombre_instrumento = QLabel("Instrumento no seleccionado")
        self.nombre_instrumento.setAlignment(Qt.AlignCenter)
        self.nombre_instrumento.setStyleSheet("font-weight: bold; font-size: 16px; color: white; background: #444; padding: 6px;")
        layout.addWidget(self.nombre_instrumento)

        self.label = QLabel()
        self.label.setStyleSheet("background-color: #222; border: 1px solid #333;")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setMinimumHeight(220)
        self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.label)

        self.piano = PianoWidget()
        self.piano.nota_presionada.connect(self.reproducir_nota)
        layout.addWidget(self.piano)

        self.panel_inferior = PanelInferior(
            panel_central_ref=self,    # <-- NUEVO: así los botones podrán activar el canal
            motor_sonido=self.motor_sonido
        )
        layout.addWidget(self.panel_inferior)

        layout.setStretch(0, 0)  # Título
        layout.setStretch(1, 3)  # Imagen
        layout.setStretch(2, 1)  # Piano
        layout.setStretch(3, 0)  # Panel inferior

    def mostrar_instrumento(self, nombre):
        self.nombre_instrumento.setText(nombre)
        nombre_archivo = nombre.lower().replace(" ", "_").replace("-", "_")
        ruta_imagen = os.path.expanduser(f"~/MIM-1-MODULAR/Imagenes/{nombre_archivo}.png")
        if os.path.exists(ruta_imagen):
            pixmap = QPixmap(ruta_imagen).scaledToHeight(220, Qt.SmoothTransformation)
            self.label.setPixmap(pixmap)
        else:
            self.label.clear()

    def asignar_instrumento(self, nombre, banco, preset, archivo, canal):
        self.instrumento_actual = (banco, preset, archivo)
        self.nombre_instrumento.setText(nombre)
        nombre_archivo = nombre.lower().replace(" ", "_").replace("-", "_")
        ruta_imagen = os.path.expanduser(f"~/MIM-1-MODULAR/Imagenes/{nombre_archivo}.png")
        if os.path.exists(ruta_imagen):
            pixmap = QPixmap(ruta_imagen).scaledToHeight(220, Qt.SmoothTransformation)
            self.label.setPixmap(pixmap)
        else:
            self.label.clear()
        # INTEGRACIÓN CON MOTORSONIDO (si está disponible)
        if self.motor_sonido:
            if archivo.lower().endswith(".wav") or archivo.lower().endswith(".mp3"):
                self.motor_sonido.asignar_sample(canal, archivo, nota_base=60)  # <-- DO CENTRAL
            elif archivo.lower().endswith(".sf2"):
                self.motor_sonido.asignar_sf2(canal, archivo, banco, preset)
        # Para compatibilidad con el antiguo Sintetizador:
        self.sintetizador.cargar_instrumento_sf2(archivo, banco, preset, canal)
        self.sintetizador.asignar_a_canal(canal, f"canal{canal}")

    def reproducir_nota(self, nota_midi):
        # Usa el motor de sonido real (polifónico) si está disponible:
        if self.motor_sonido:
            self.motor_sonido.nota_on(self.canal_activo, nota_midi)  # <-- CANAL ACTIVO
        else:
            banco, preset, archivo = self.instrumento_actual
            self.sintetizador.reproducir_nota(self.canal_activo, nota_midi)

    def set_canal_activo(self, canal):
        """Método para que el panel inferior seleccione el canal."""
        self.canal_activo = canal   # <-- NUEVO: Setter de canal activo

    def resetear_todos_los_canales(self):
        if self.motor_sonido:
            self.motor_sonido.reset()
        # Si tienes más lógica, añádela aquí (como reiniciar sintes, nombres, etc.)

    # Mantén aquí tus métodos de presets, guardar/cargar escenarios, etc. si los tienes.
