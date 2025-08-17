from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QPushButton, QSizePolicy, QFrame
)
from PyQt5.QtCore import Qt
from dial_panoramico import DialPanoramico

class ModuloEfectos(QWidget):
    def __init__(self):
        super().__init__()

        layout = QHBoxLayout()
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignBottom)
        self.setLayout(layout)

        layout.addLayout(self.crear_modulo("Compresor", [
            ("Threshold", "dB", "slider"),
            ("Ratio", ":1", "dial"),
            ("Attack", "ms", "dial"),
            ("Release", "ms", "dial")
        ]))

        layout.addLayout(self.crear_modulo("Filtro", [
            ("Corte", "Hz", "dial"),
            ("Pendiente", "%", "slider")
        ]))

        layout.addLayout(self.crear_modulo("Saturación", [
            ("Drive", "%", "slider"),
            ("Tono", "%", "dial"),
            ("Mix", "%", "slider")
        ]))

    def crear_modulo(self, nombre, controles):
        columna = QVBoxLayout()
        columna.setAlignment(Qt.AlignHCenter)

        lbl_nombre = QLabel(nombre)
        lbl_nombre.setStyleSheet("color: white; font-size: 9pt;")
        lbl_nombre.setAlignment(Qt.AlignCenter)
        columna.addWidget(lbl_nombre)

        # LED y botón ON/OFF
        fila_led = QHBoxLayout()
        led = QFrame()
        led.setFixedSize(10, 10)
        led.setStyleSheet("background-color: red; border-radius: 5px;")
        btn_on = QPushButton("ON")
        btn_on.setCheckable(True)
        btn_on.setStyleSheet("QPushButton { background-color: #333; color: white; border-radius: 3px; } QPushButton:checked { background-color: #0f0; color: black; }")
        btn_on.toggled.connect(lambda estado: led.setStyleSheet(f"background-color: {'#0f0' if estado else 'red'}; border-radius: 5px;"))
        fila_led.addWidget(led)
        fila_led.addWidget(btn_on)
        columna.addLayout(fila_led)

        for label, unidad, tipo in controles:
            lbl = QLabel(f"{label} ({unidad})")
            lbl.setStyleSheet("color: #ccc; font-size: 8pt;")
            lbl.setAlignment(Qt.AlignCenter)
            columna.addWidget(lbl)

            if tipo == "slider":
                slider_layout = QHBoxLayout()
                escala = QVBoxLayout()
                for val in reversed(range(0, 101, 25)):
                    lbl_val = QLabel(str(val))
                    lbl_val.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    lbl_val.setStyleSheet("color: #888; font-size: 7pt;")
                    escala.addWidget(lbl_val)

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
                columna.addLayout(slider_layout)

            elif tipo == "dial":
                dial = DialPanoramico()
                dial.setValue(0)
                dial.setFixedSize(40, 40)
                columna.addWidget(dial)

        return columna
