from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QRectF, QTimer, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QLinearGradient, QFont

class FaderLED(QWidget):
    valueChanged = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(32)
        self.setMinimumHeight(146)
        self._value = 50  # 0 a 100
        self.show_label = False
        self.timer = QTimer(self)
        self.timer.setInterval(1200)
        self.timer.timeout.connect(self.oculta_label)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, val):
        val = max(0, min(100, int(val)))
        if self._value != val:
            self._value = val
            self.show_label = True
            self.timer.start()
            self.update()
            self.valueChanged.emit(self._value)

    def setValue(self, val):
        self.value = val  # Redirige al setter

    def oculta_label(self):
        self.show_label = False
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._set_from_pos(event.pos())

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self._set_from_pos(event.pos())

    def _set_from_pos(self, pos):
        margen = 22
        usable = self.height() - 2 * margen
        if usable <= 0:
            usable = 1
        v = 100 - int((pos.y() - margen) * 100 / usable)
        self.value = v  # Usa la propiedad

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        margen = 22
        rail_rect = QRectF(w//2-7, margen, 14, h - 2*margen)
        # --- rail mate (fondo del fader)
        grad = QLinearGradient(rail_rect.left(), rail_rect.top(), rail_rect.left(), rail_rect.bottom())
        grad.setColorAt(0.0, QColor(30,30,30))
        grad.setColorAt(1.0, QColor(60,60,60))
        painter.setBrush(QBrush(grad))
        painter.setPen(QPen(QColor(16,16,16),2))
        painter.drawRoundedRect(rail_rect, 7, 7)

        # --- pista de volumen: solo debajo del botón
        pos_y = margen + (100-self._value)*(h-2*margen)/100
        pista_rect = QRectF(w//2-4, pos_y, 8, rail_rect.bottom()-pos_y)
        grad_led = QLinearGradient(pista_rect.left(), pista_rect.top(), pista_rect.left(), pista_rect.bottom())
        grad_led.setColorAt(0.0, QColor(20,200,255,200))
        grad_led.setColorAt(1.0, QColor(40,255,180,40))
        painter.setBrush(QBrush(grad_led))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(pista_rect, 3, 3)

        # --- botón del fader (grande, metálico)
        btn_rect = QRectF(w//2-14, pos_y-10, 28, 20)
        grad_btn = QLinearGradient(btn_rect.left(), btn_rect.top(), btn_rect.left(), btn_rect.bottom())
        grad_btn.setColorAt(0.0, QColor(230,230,230))
        grad_btn.setColorAt(0.7, QColor(140,140,140))
        grad_btn.setColorAt(1.0, QColor(80,80,80))
        painter.setBrush(QBrush(grad_btn))
        painter.setPen(QPen(QColor(44,44,44),2))
        painter.drawRoundedRect(btn_rect, 9, 9)

        # --- destello central del botón (efecto brillo cristal)
        brillo_rect = QRectF(btn_rect.center().x()-8, btn_rect.top()+2, 16, 8)
        grad_brillo = QLinearGradient(brillo_rect.left(), brillo_rect.top(), brillo_rect.left(), brillo_rect.bottom())
        grad_brillo.setColorAt(0.0, QColor(255,255,255,180))
        grad_brillo.setColorAt(1.0, QColor(200,200,200,0))
        painter.setBrush(QBrush(grad_brillo))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(brillo_rect)

        # --- valor flotante (transparente/cristal) encima
        if self.show_label:
            painter.setFont(QFont("Arial Black", 10, QFont.Bold))
            painter.setPen(QColor(10,255,220,240))
            painter.drawText(QRectF(btn_rect.left()-10, btn_rect.top()-30, btn_rect.width()+20, 24), Qt.AlignCenter, str(self._value))
