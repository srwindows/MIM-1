from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QListWidgetItem
from PyQt5.QtCore import Qt
from canal_manager import GestorCanales

class PanelSonido(QWidget):
    def __init__(self, on_instrumento_seleccionado):
        super().__init__()
        layout = QVBoxLayout(self)
        self.setLayout(layout)
        self.gestor = GestorCanales()
        self.lista = QListWidget()
        self.lista.itemClicked.connect(self.seleccionar)
        layout.addWidget(QLabel("Canales (clic para activar/desactivar):"))
        layout.addWidget(self.lista)
        self.on_instrumento_seleccionado = on_instrumento_seleccionado
        self.actualizar()

    def actualizar(self):
        self.lista.clear()
        for canal in self.gestor.canales:
            texto = f"{canal.numero+1:02d} - {'✔' if canal.activo else '✘'}"
            if canal.banco and canal.preset:
                texto += f" → {canal.preset}"
            item = QListWidgetItem(texto)
            item.setData(Qt.UserRole, canal.numero)
            self.lista.addItem(item)

    def seleccionar(self, item):
        numero = item.data(Qt.UserRole)
        canal = self.gestor.get_canal(numero)
        canal.activo = not canal.activo
        self.actualizar()

    def asignar_instrumento(self, canal_num, banco, preset):
        self.gestor.asignar(canal_num, banco, preset)
        self.actualizar()
        self.on_instrumento_seleccionado(canal_num, banco, preset)
