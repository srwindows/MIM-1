from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QPushButton, QLabel

class SelectorDispositivoDialog(QDialog):
    def __init__(self, motor_sonido, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Seleccionar dispositivo de audio")
        self.motor_sonido = motor_sonido

        self.layout = QVBoxLayout(self)

        self.label = QLabel("Selecciona el dispositivo de salida de audio:")
        self.layout.addWidget(self.label)

        self.lista = QListWidget()
        self.dispositivos = self.motor_sonido.listar_dispositivos()
        for idx, name in self.dispositivos:
            self.lista.addItem(f"[{idx}] {name}")
        # Marca el actual
        for i, (idx, _) in enumerate(self.dispositivos):
            if idx == self.motor_sonido.dispositivo_idx:
                self.lista.setCurrentRow(i)
                break

        self.layout.addWidget(self.lista)

        botones = QHBoxLayout()
        btn_ok = QPushButton("Aceptar")
        btn_cancel = QPushButton("Cancelar")
        botones.addWidget(btn_ok)
        botones.addWidget(btn_cancel)
        self.layout.addLayout(botones)

        btn_ok.clicked.connect(self.aceptar)
        btn_cancel.clicked.connect(self.reject)

    def aceptar(self):
        fila = self.lista.currentRow()
        if fila >= 0:
            idx, _ = self.dispositivos[fila]
            self.motor_sonido.set_dispositivo(idx)
        self.accept()
