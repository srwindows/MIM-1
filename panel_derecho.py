from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSizePolicy
from modulo_control import ModuloControl
from modulo_efectos import ModuloEfectos
from modulo_vst import ModuloVST

class PanelDerecho(QWidget):
    def __init__(self):
        super().__init__()

        # Políticas de tamaño dinámico
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumWidth(200)

        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Crear módulos
        self.control = ModuloControl()
        self.efectos = ModuloEfectos()
        self.vst = ModuloVST()

        # Asegurar que cada módulo se expanda bien
        for widget in [self.control, self.efectos, self.vst]:
            widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            layout.addWidget(widget, stretch=1)

        self.setLayout(layout)
