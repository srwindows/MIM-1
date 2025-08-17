
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton
from modulo_master import ModuloMaster
from modulo_control import ModuloControl
from modulo_efectos import ModuloEfectos
from modulo_vst import ModuloVST

class VentanaEfectos(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Efectos Máster")
        self.setMinimumSize(1000, 700)
        self.setStyleSheet("background-color: #222; color: white;")

        layout_general = QVBoxLayout()
        layout_general.setContentsMargins(10, 10, 10, 10)
        layout_general.setSpacing(12)

        # Fila 1: Módulo Master (volumen, pan, vumetro, EQ)
        fila1 = QHBoxLayout()
        fila1.addWidget(ModuloMaster())
        layout_general.addLayout(fila1)

        # Fila 2: Módulo Control (oscilador, reverb, delay)
        fila2 = QHBoxLayout()
        fila2.addWidget(ModuloControl())
        layout_general.addLayout(fila2)

        # Fila 3: Módulo Efectos (compresor, filtro, saturación)
        fila3 = QHBoxLayout()
        fila3.addWidget(ModuloEfectos())
        layout_general.addLayout(fila3)

        # Fila 4: Módulo VST
        fila4 = QHBoxLayout()
        fila4.addWidget(ModuloVST())
        layout_general.addLayout(fila4)

        # Botón cerrar
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.clicked.connect(self.close)
        btn_cerrar.setStyleSheet("background-color: #500; color: white; padding: 4px;")
        layout_general.addWidget(btn_cerrar)

        self.setLayout(layout_general)
