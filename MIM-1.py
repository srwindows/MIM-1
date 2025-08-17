#!/usr/bin/env python3
import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QHBoxLayout
)
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtCore import Qt


class MIM1(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MIM-1 Sampler - Laboratorio")
        self.setGeometry(100, 100, 1400, 800)

        # Asegura carpetas
        for carpeta in ["Bancos", "Escenas", "Imagenes", "VSTs"]:
            os.makedirs(os.path.join(os.getcwd(), carpeta), exist_ok=True)

        # Layout principal
        central = QWidget()
        main_layout = QVBoxLayout()
        central.setLayout(main_layout)
        self.setCentralWidget(central)

        # Pantalla central
        self.pantalla = QLabel("Pantalla Central")
        self.pantalla.setStyleSheet("background: #333; color: #fff;")
        self.pantalla.setAlignment(Qt.AlignCenter)
        self.pantalla.setMinimumHeight(300)
        main_layout.addWidget(self.pantalla)

        # Piano
        self.piano = PianoWidget()
        main_layout.addWidget(self.piano)

    def resizeEvent(self, event):
        self.pantalla.setMinimumWidth(int(self.width() * 0.8))
        super().resizeEvent(event)


class PianoWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumHeight(120)

    def paintEvent(self, event):
        painter = QPainter(self)
        w = self.width()
        h = self.height()
        num_white = 52
        key_w = w / num_white

        # Blancas
        for i in range(num_white):
            x = int(i * key_w)
            kw = int(key_w) + 1
            painter.setBrush(QColor("white"))
            painter.setPen(QColor("black"))
            painter.drawRect(x, 0, kw, h)

        # Negras
        black_pattern = [1, 3, 6, 8, 10]
        for i in range(7):
            for k in black_pattern:
                idx = i * 7 + k // 2
                x = int((idx + 1) * key_w - key_w / 4)
                if x + key_w / 2 < w:
                    painter.setBrush(QColor("black"))
                    painter.drawRect(x, 0, int(key_w / 2), int(h * 0.6))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = MIM1()
    ventana.show()
    sys.exit(app.exec_())
