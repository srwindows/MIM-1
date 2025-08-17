from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QPushButton, QSizePolicy, QFrame
)
from PyQt5.QtCore import Qt, QTimer
from dial_panoramico import DialPanoramico
import random

class ModuloControl(QWidget):
    def __init__(self):
        super().__init__()

        layout = QHBoxLayout()
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignBottom)
        self.setLayout(layout)

        # Crear módulos: oscilador, reverb, delay
        layout.addLayout(self.crear_modulo("Oscilador", "Frecuencia", "Intensidad", unidad1="Hz", unidad2="%"))
        layout.addLayout(self.crear_modulo("Reverb", "Cola", "Tamaño", unidad1="ms", unidad2="%"))
        layout.addLayout(self.crear_modulo("Delay", "Tiempo", "Feedback", unidad1="ms", unidad2="%"))

    def crear_modulo(self, nombre, dial_label, slider_label, unidad1="", unidad2=""):
        columna = QVBoxLayout()
        columna.setAlignment(Qt.AlignHCenter)

        # Nombre del módulo y preset
        lbl_nombre = QLabel(nombre)
        lbl_nombre.setStyleSheet("color: white; font-size: 9pt;")
        lbl_nombre.setAlignment(Qt.AlignCenter)
        columna.addWidget(lbl_nombre)

        lbl_preset = QLabel("Preset 1")
        lbl_preset.setStyleSheet("color: #0ff; font-size: 8pt;")
        lbl_preset.setAlignment(Qt.AlignCenter)
        columna.addWidget(lbl_preset)

        # LED indicador y boton ON/OFF
        fila_led = QHBoxLayout()
        self.led = QFrame()
        self.led.setFixedSize(10, 10)
        self.led.setStyleSheet("background-color: red; border-radius: 5px;")
        btn_on = QPushButton("ON")
        btn_on.setCheckable(True)
        btn_on.setStyleSheet("QPushButton { background-color: #333; color: white; border-radius: 3px; } QPushButton:checked { background-color: #0f0; color: black; }")
        btn_on.toggled.connect(lambda estado: self.led.setStyleSheet(f"background-color: {'#0f0' if estado else 'red'}; border-radius: 5px;"))
        fila_led.addWidget(self.led)
        fila_led.addWidget(btn_on)
        columna.addLayout(fila_led)

        # Dial con etiqueta y unidad
        lbl_dial = QLabel(f"{dial_label} ({unidad1})")
        lbl_dial.setStyleSheet("color: #ccc; font-size: 8pt;")
        lbl_dial.setAlignment(Qt.AlignCenter)
        dial = DialPanoramico()
        dial.setValue(0)
        dial.setFixedSize(40, 40)
        columna.addWidget(lbl_dial)
        columna.addWidget(dial)

        # Deslizador con escala
        lbl_slider = QLabel(f"{slider_label} ({unidad2})")
        lbl_slider.setStyleSheet("color: #ccc; font-size: 8pt;")
        lbl_slider.setAlignment(Qt.AlignCenter)

        slider_layout = QHBoxLayout()
        escala = QVBoxLayout()
        for val in reversed(range(0, 101, 25)):
            lbl = QLabel(str(val))
            lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            lbl.setStyleSheet("color: #888; font-size: 7pt;")
            escala.addWidget(lbl)

        slider = QSlider(Qt.Vertical)
        slider.setRange(0, 100)
        slider.setValue(50)
        slider.setTickInterval(25)
        slider.setTickPosition(QSlider.TicksRight)
        slider.setFixedHeight(100)
        slider.setFixedWidth(10)
        slider.setStyleSheet("""
            QSlider::groove:vertical {
                background: qlineargradient(x1:0, y1:1, x2:0, y2:0,
                    stop:0 #111, stop:0.5 #4af, stop:1 #0ff);
                width: 8px;
                border-radius: 4px;
            }
            QSlider::handle:vertical {
                background: #0af;
                height: 16px;
                margin: -2px -4px;
                border-radius: 4px;
            }
        """)

        slider_layout.addLayout(escala)
        slider_layout.addWidget(slider)

        columna.addWidget(lbl_slider)
        columna.addLayout(slider_layout)

        return columna
