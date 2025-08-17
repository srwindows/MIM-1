from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
from dial_panoramico import DialPanoramico  # ¡Debe estar en el mismo directorio!
import sys

app = QApplication(sys.argv)
w = QWidget()
w.setWindowTitle("Prueba Dial Panorámico")
layout = QVBoxLayout(w)
dial = DialPanoramico()
dial.setFixedSize(110, 110)  # Bien grande para ver todo
layout.addWidget(dial)
w.setLayout(layout)
w.show()
sys.exit(app.exec_())
