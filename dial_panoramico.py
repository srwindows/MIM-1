from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QRectF, QPointF, QTimer, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QConicalGradient, QFont, QRadialGradient
import math

class DialPanoramico(QWidget):
    valueChanged = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(66, 66)
        self.value = 0
        self.min_val = -100
        self.max_val = 100
        self.last_y = None
        self._mostrar_valor = False
        self._timer = QTimer(self)
        self._timer.setInterval(1200)
        self._timer.timeout.connect(self.ocultar_valor)

    def setValue(self, val):
        self.value = max(self.min_val, min(self.max_val, val))
        self._mostrar_valor = True
        self._timer.start()
        self.update()
        self.valueChanged.emit(self.value)

    def value_(self):
        return self.value

    def ocultar_valor(self):
        self._mostrar_valor = False
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        center = QPointF(w / 2, h / 2)
        radio_ext = min(w, h) / 2 - 5

        # 1. Sombra suave exterior
        grad_sombra = QRadialGradient(center, radio_ext+7)
        grad_sombra.setColorAt(0.82, QColor(0,0,0,70))
        grad_sombra.setColorAt(1.0, QColor(0,0,0,18))
        painter.setBrush(QBrush(grad_sombra))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(center, radio_ext+5, radio_ext+5)

        # 2. Bisel metálico exterior
        grad_bisel = QConicalGradient(center, -90)
        grad_bisel.setColorAt(0.0, QColor(220,225,235))
        grad_bisel.setColorAt(0.25, QColor(100,105,120))
        grad_bisel.setColorAt(0.50, QColor(220,220,250))
        grad_bisel.setColorAt(0.75, QColor(90,105,120))
        grad_bisel.setColorAt(1.0, QColor(220,225,235))
        painter.setBrush(QBrush(grad_bisel))
        painter.setPen(QPen(QColor(30, 35, 45), 2))
        painter.drawEllipse(center, radio_ext, radio_ext)

        # 3. Anillo de escala solo en el arco 270º, con ticks por fuera
        ticks_r = radio_ext + 2
        for i in range(41):
            ang = -135 + i * (270/40)
            rad = math.radians(ang - 90)
            is_major = i in (0, 20, 40)
            tick_len = 12 if is_major else 6
            col = QColor("#00ffd0") if is_major else QColor(110,240,255,160)
            penw = 2 if is_major else 1
            x1 = center.x() + math.cos(rad) * (ticks_r+2)
            y1 = center.y() + math.sin(rad) * (ticks_r+2)
            x2 = center.x() + math.cos(rad) * (ticks_r+2+tick_len)
            y2 = center.y() + math.sin(rad) * (ticks_r+2+tick_len)
            painter.setPen(QPen(col, penw))
            painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))

        # 4. Letras LCR FUERA y separadas
        for i, txt in enumerate(["L", "C", "R"]):
            idx = i*20  # 0, 20, 40
            ang = -135 + idx * (270/40)
            rad = math.radians(ang - 90)
            dist = ticks_r + 22
            rx = center.x() + math.cos(rad) * dist
            ry = center.y() + math.sin(rad) * dist
            painter.setFont(QFont("Arial Black", 12, QFont.Bold))
            painter.setPen(QPen(QColor(0,255,230,230), 2))
            painter.drawText(QRectF(rx-10, ry-13, 20, 26), Qt.AlignCenter, txt)

        # 5. Anillo de color
        for i in range(41):
            ang = -135 + i * (270/40)
            val = self.min_val + i * (self.max_val - self.min_val) // 40
            if abs(val) < 8:
                color = QColor("#0f0")
            elif val > 0:
                color = QColor("#f44")
            elif val < 0:
                color = QColor("#09f")
            else:
                color = QColor("#fff")
            ancho = 3 if val == 0 else 2
            painter.setPen(QPen(color, ancho))
            painter.drawArc(
                QRectF(center.x() - radio_ext + 2, center.y() - radio_ext + 2, (radio_ext - 2)*2, (radio_ext - 2)*2),
                int((ang-90)*16), int(2*16)
            )

        # 6. Esfera central
        grad_central = QRadialGradient(center, radio_ext * 0.80)
        grad_central.setColorAt(0.0, QColor(255,255,255,240))
        grad_central.setColorAt(0.28, QColor(110,130,140))
        grad_central.setColorAt(1.0, QColor(25,25,38))
        painter.setBrush(QBrush(grad_central))
        painter.setPen(QPen(QColor(70, 85, 100), 2))
        painter.drawEllipse(center, radio_ext * 0.78, radio_ext * 0.78)

        # 7. Aguja/Marcador
        painter.setPen(QPen(QColor("#00f7ff"), 3))
        angle = -135 + ((self.value - self.min_val) / (self.max_val - self.min_val)) * 270
        rad = math.radians(angle - 90)
        x = center.x() + math.cos(rad) * (radio_ext * 0.62)
        y = center.y() + math.sin(rad) * (radio_ext * 0.62)
        painter.drawLine(center, QPointF(x, y))

        # 8. Botón central realista
        grad_btn = QRadialGradient(center, radio_ext*0.20)
        grad_btn.setColorAt(0.0, QColor(250,250,255,170))
        grad_btn.setColorAt(0.65, QColor(120,150,210,200))
        grad_btn.setColorAt(1.0, QColor(45,55,60,240))
        painter.setBrush(QBrush(grad_btn))
        painter.setPen(QPen(QColor(70,90,130), 1))
        painter.drawEllipse(center, radio_ext*0.16, radio_ext*0.16)

        # 9. Valor flotante central al mover
        if self._mostrar_valor:
            painter.setFont(QFont("Arial", 13, QFont.Bold))
            painter.setPen(QColor(0,0,0,100))
            painter.drawText(QRectF(2, h/2-14, w-4, 32), Qt.AlignHCenter|Qt.AlignVCenter, f"{self.value:+}")
            painter.setPen(QColor("#00ffee"))
            painter.drawText(QRectF(0, h/2-16, w, 32), Qt.AlignHCenter|Qt.AlignVCenter, f"{self.value:+}")

    def mousePressEvent(self, event):
        self.last_y = event.y()
        self._mostrar_valor = True
        self._timer.start()
        self.update()

    def mouseMoveEvent(self, event):
        if self.last_y is None:
            return
        dy = self.last_y - event.y()
        if abs(dy) > 0:
            step = int(dy / 2)
            self.setValue(self.value + step)
            self.last_y = event.y()
