import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QSizePolicy
from panel_central import PanelCentral
from panel_izquierdo import PanelIzquierdo
from panel_derecho import PanelDerecho
from motor_sonido import MotorSonido  # <-- ¡AÑADIDO!

class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MIM-1 MODULAR - Vista previa")
        self.setGeometry(100, 100, 1600, 800)
        self.setMinimumSize(150, 150)

        # Crear el motor de sonido
        self.motor_sonido = MotorSonido()   # <-- ¡AÑADIDO!

        # Crear los paneles (sin pasar motor_sonido al panel izquierdo)
        self.panel_central = PanelCentral(motor_sonido=self.motor_sonido)
        self.panel_izquierdo = PanelIzquierdo(
            panel_central_ref=self.panel_central,
            motor_sonido=self.motor_sonido
        )
        self.panel_derecho = PanelDerecho()

        # Establecer referencias mutuas para presets
        self.panel_central.panel_inferior.panel_central_ref = self.panel_central
        self.panel_central.panel_inferior.panel_izquierdo_ref = self.panel_izquierdo

        # Ajustes de tamaño mínimos
        self.panel_izquierdo.setMinimumWidth(100)
        self.panel_derecho.setMinimumWidth(100)
        self.panel_central.setMinimumWidth(100)
        self.panel_izquierdo.setMinimumHeight(100)
        self.panel_derecho.setMinimumHeight(100)
        self.panel_central.setMinimumHeight(100)

        # Políticas de expansión
        self.panel_izquierdo.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.panel_central.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.panel_derecho.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

        # Crear contenedor central con layout horizontal
        central_widget = QWidget()
        central_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        central_widget.setStyleSheet("background-color: blue;")  # Fondo color aqua
        layout = QHBoxLayout(central_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)

        # Añadir los paneles al layout
        layout.addWidget(self.panel_izquierdo)
        layout.addWidget(self.panel_central, stretch=2)
        layout.addWidget(self.panel_derecho, stretch=1)

        self.setCentralWidget(central_widget)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec_())
