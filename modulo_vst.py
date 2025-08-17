from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QFileDialog
)
from PyQt5.QtCore import Qt
import os

class ModuloVST(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignTop)
        self.setLayout(layout)

        titulo = QLabel("VSTs (Máster)")
        titulo.setStyleSheet("color: white; font-size: 10pt;")
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)

        # Contenedor horizontal para 4 VSTs
        self.vst_slots = []
        contenedor_botones = QHBoxLayout()
        for i in range(1, 5):
            slot_layout, led, btn_vst = self.crear_vst_slot(f"VST {i}", i)
            self.vst_slots.append((led, btn_vst))
            contenedor_botones.addLayout(slot_layout)

        layout.addLayout(contenedor_botones)

    def crear_vst_slot(self, nombre, index):
        slot = QVBoxLayout()
        slot.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        fila_superior = QHBoxLayout()
        fila_superior.setAlignment(Qt.AlignHCenter)

        # LED indicador (click para activar/desactivar VST asociado)
        led = QFrame()
        led.setFixedSize(10, 10)
        led.setStyleSheet("background-color: red; border-radius: 5px;")
        led.setObjectName(f"led_{index}")
        led.mousePressEvent = lambda event: self.toggle_led(index)

        # Botón CARGAR al lado del LED
        btn_cargar = QPushButton("Cargar")
        btn_cargar.setFixedSize(40, 16)
        btn_cargar.setStyleSheet("""
            QPushButton {
                font-size: 7pt;
                border-radius: 3px;
                background-color: #333;
                color: white;
            }
            QPushButton:hover {
                background-color: #555;
            }
        """)
        btn_cargar.clicked.connect(self.abrir_y_cargar_vst)

        fila_superior.addWidget(led)
        fila_superior.addWidget(btn_cargar)

        # Botón de nombre del VST
        btn_vst = QPushButton(nombre)
        btn_vst.setCheckable(True)
        btn_vst.setStyleSheet("""
            QPushButton {
                background-color: #444;
                color: white;
                font-size: 8pt;
                border-radius: 4px;
                padding: 2px 6px;
            }
            QPushButton:checked {
                background-color: #0f0;
                color: black;
            }
        """)
        btn_vst.toggled.connect(lambda estado, b=btn_vst: self.mostrar_ocultar_vst(b))

        # Agregar elementos al slot
        slot.addLayout(fila_superior)
        slot.addWidget(btn_vst)

        return slot, led, btn_vst

    def toggle_led(self, index):
        led, btn_vst = self.vst_slots[index - 1]
        is_active = led.styleSheet().find("#0f0") != -1
        if is_active:
            led.setStyleSheet("background-color: red; border-radius: 5px;")
        else:
            led.setStyleSheet("background-color: #0f0; border-radius: 5px;")
        # Aquí puedes agregar lógica para activar o desactivar el plugin VST real

    def mostrar_ocultar_vst(self, boton):
        if boton.isChecked():
            print(f"Mostrando interfaz de {boton.text()}")
            # Lógica para mostrar VST
        else:
            print(f"Ocultando interfaz de {boton.text()}")
            # Lógica para ocultar VST

    def abrir_y_cargar_vst(self):
        carpetas_vst = [
            os.path.expanduser("~/.vst"),
            "/usr/lib/vst",
            "/usr/local/lib/vst",
            os.path.expanduser("~/.lxvst")
        ]
        for carpeta in carpetas_vst:
            if os.path.isdir(carpeta):
                archivo, _ = QFileDialog.getOpenFileName(
                    self, "Cargar VST", carpeta, "Plugins VST (*.so *.vst *.dll)"
                )
                if archivo:
                    print(f"VST cargado: {archivo}")
                    break
