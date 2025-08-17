from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QTimer, QRectF
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QLinearGradient, QFont
import numpy as np

class Vumetro(QWidget):
    def __init__(self, motor_sonido, canal_idx=0, parent=None):
        super().__init__(parent)
        self.motor_sonido = motor_sonido
        self.canal_idx = canal_idx
        self.nivel_L = 0  # Nivel de 0 a 127 para Izquierda
        self.nivel_R = 0  # Nivel de 0 a 127 para Derecha
        self.setMinimumWidth(28)
        self.setMinimumHeight(76)
        self.setMaximumWidth(36)
        self.setMaximumHeight(180)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.update_level)
        self._timer.start(50)

    def update_level(self):
        if not self.motor_sonido:
            self.nivel_L = 0
            self.nivel_R = 0
            self.update()
            return
        audio = self.motor_sonido.get_salida_actual()
        # print("audio en vumetro:", type(audio), "shape:", getattr(audio, 'shape', None))
        if audio is not None and isinstance(audio, np.ndarray) and audio.size > 0:
            if audio.ndim == 2 and audio.shape[1] >= 2:
                canalL = audio[:, 0]
                canalR = audio[:, 1]
            elif audio.ndim == 2:
                canalL = canalR = audio[:, 0]
            else:
                canalL = canalR = audio

            def nivel_vumetro(canal):
                rms = np.sqrt(np.mean(canal.astype(np.float32) ** 2))
                if rms < 1e-8:
                    db = -60  # Nivel muy bajo
                else:
                    db = 20 * np.log10(rms)
                    # --- Aquí subimos la sensibilidad ---
                    db = db + -6 # Sube la sensibilidad 10 dB. Si sube mucho, pon +5 en vez de +10
                    if db < -60:
                        db = -60
                    if db > 0:
                        db = 0
                nivel = int(127 * (db + 35) / 35)
                return nivel

            self.nivel_L = nivel_vumetro(canalL)
            self.nivel_R = nivel_vumetro(canalR)
        else:
            self.nivel_L = 0
            self.nivel_R = 0
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w = self.width()
        h = self.height()
        margen = 10
        bar_w = (w - 18) // 2
        bar_h = h - 2 * margen

        # Marco exterior
        painter.setBrush(QBrush(QColor(30, 30, 30)))
        painter.setPen(QPen(QColor(70, 70, 70), 3))
        painter.drawRoundedRect(1, 1, w-2, h-2, 6, 6)

        # Fondo oscuro
        painter.setBrush(QBrush(QColor(8, 8, 10)))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(4, 4, w-8, h-8, 4, 4)

        # Barra Izquierda
        nivel_px_L = int(bar_h * self.nivel_L / 127)
        y0_L = h - margen - nivel_px_L
        rect_L = QRectF(6, y0_L, bar_w, nivel_px_L)
        grad_L = QLinearGradient(rect_L.left(), rect_L.bottom(), rect_L.left(), rect_L.top())
        grad_L.setColorAt(0.0, QColor("#0f0"))
        grad_L.setColorAt(0.7, QColor("#ff0"))
        grad_L.setColorAt(0.93, QColor("#f90"))
        grad_L.setColorAt(1.0, QColor("#f00"))
        painter.setBrush(QBrush(grad_L))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(rect_L, 2, 2)

        # Barra Derecha
        nivel_px_R = int(bar_h * self.nivel_R / 127)
        y0_R = h - margen - nivel_px_R
        rect_R = QRectF(6 + bar_w + 6, y0_R, bar_w, nivel_px_R)
        grad_R = QLinearGradient(rect_R.left(), rect_R.bottom(), rect_R.left(), rect_R.top())
        grad_R.setColorAt(0.0, QColor("#0f0"))
        grad_R.setColorAt(0.7, QColor("#ff0"))
        grad_R.setColorAt(0.93, QColor("#f90"))
        grad_R.setColorAt(1.0, QColor("#f00"))
        painter.setBrush(QBrush(grad_R))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(rect_R, 2, 2)

        # Reflejo suave (cristal superior)
        reflejo = QRectF(6, 4, w-12, (h-8)*0.45)
        grad_r = QLinearGradient(reflejo.left(), reflejo.top(), reflejo.left(), reflejo.bottom())
        grad_r.setColorAt(0.0, QColor(255,255,255,80))
        grad_r.setColorAt(1.0, QColor(255,255,255,5))
        painter.setBrush(grad_r)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(reflejo, 2, 2)

        # Escala dBFS (lado izquierdo)
        painter.setPen(QColor(130,220,255,180))
        painter.setFont(QFont("Arial", 7, QFont.Bold))
        pasos = [0, -6, -12, -18, -24, -36, -48, -60]
        for i, db in enumerate(pasos):
            y = margen + i*(bar_h//(len(pasos)-1))
            painter.drawText(2, y+10, 22, 11, Qt.AlignLeft, f"{db}")

        # L/R
        painter.setPen(QColor(170,170,255,160))
        painter.setFont(QFont("Arial", 8, QFont.Bold))
        painter.drawText(8, h-3, "L")
        painter.drawText(8 + bar_w + 6, h-3, "R")

        # Marco brillante lateral
        gradb = QLinearGradient(0, 0, w, 0)
        gradb.setColorAt(0.0, QColor(220,255,255,45))
        gradb.setColorAt(0.4, QColor(70,90,140,30))
        gradb.setColorAt(1.0, QColor(250,250,255,45))
        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(QBrush(gradb), 2))
        painter.drawRoundedRect(1, 1, w-2, h-2, 6, 6)
