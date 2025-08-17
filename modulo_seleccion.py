# modulo_seleccion.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QDialog, QListWidget, QLabel
from PyQt5.QtCore import Qt

class SelectorDispositivoDialog(QDialog):
    def __init__(self, motor_sonido, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Seleccionar dispositivo de audio")
        self.motor_sonido = motor_sonido

        layout = QVBoxLayout(self)

        label = QLabel("Selecciona el dispositivo de salida de audio:")
        layout.addWidget(label)

        self.lista = QListWidget()
        self.dispositivos = self.motor_sonido.listar_dispositivos()
        for idx, name in self.dispositivos:
            self.lista.addItem(f"[{idx}] {name}")
        for i, (idx, _) in enumerate(self.dispositivos):
            if idx == self.motor_sonido.dispositivo_idx:
                self.lista.setCurrentRow(i)
                break
        layout.addWidget(self.lista)

        btns = QHBoxLayout()
        btn_ok = QPushButton("Aceptar")
        btn_cancel = QPushButton("Cancelar")
        btns.addWidget(btn_ok)
        btns.addWidget(btn_cancel)
        layout.addLayout(btns)

        btn_ok.clicked.connect(self.aceptar)
        btn_cancel.clicked.connect(self.reject)

    def aceptar(self):
        fila = self.lista.currentRow()
        if fila >= 0:
            idx, _ = self.dispositivos[fila]
            self.motor_sonido.set_dispositivo(idx)
        self.accept()

class ModuloSeleccion(QWidget):
    def __init__(self, motor_sonido, parent=None):
        super().__init__(parent)
        self.motor_sonido = motor_sonido
        self.setFixedWidth(120)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        self.boton_dispositivos = QPushButton("Dispositivos")
        self.boton_dispositivos.setStyleSheet("""
            QPushButton {
                background-color: #333; color: #0ff; font-weight: bold; padding: 4px;
                border-radius: 7px; border: 1px solid #099;
            }
            QPushButton:hover { background-color: #066; }
        """)
        self.boton_dispositivos.clicked.connect(self.abrir_selector_dispositivo)
        layout.addWidget(self.boton_dispositivos)

        # Aquí puedes añadir más botones de configuración en el futuro

    def abrir_selector_dispositivo(self):
        dlg = SelectorDispositivoDialog(self.motor_sonido, self)
        dlg.exec_()
