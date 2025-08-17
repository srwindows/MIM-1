from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPainter, QColor

class PianoWidget(QWidget):
    nota_presionada = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.setFixedHeight(45)      # <--- Cambia este valor para tu altura preferida
        # self.setFixedWidth(600)     # <--- (opcional) Fija el ancho si lo necesitas
        self.nota_base = 21  # A0
        self.total_teclas_blancas = 52
        self.total_teclas = 88
        self.pulsada = None
        self.blancas = []
        self.negras = []
        self.init_teclas()

    def init_teclas(self):
        self.blancas = []
        self.negras = []
        nota = self.nota_base
        for _ in range(self.total_teclas):
            if self.is_white(nota):
                self.blancas.append(nota)
            else:
                self.negras.append(nota)
            nota += 1

    def paintEvent(self, event):
        painter = QPainter(self)
        w = self.width()
        h = self.height()
        key_w = w / self.total_teclas_blancas

        for i, nota in enumerate(self.blancas):
            x = int(i * key_w)
            color = QColor("#aaa") if nota == self.pulsada else QColor("white")
            painter.setBrush(color)
            painter.setPen(QColor("black"))
            painter.drawRect(x, 0, int(key_w), h)

        for nota in self.negras:
            idx = self.get_white_index_before(nota)
            if idx is not None:
                x = int((idx + 1) * key_w - key_w / 4)
                color = QColor("#333") if nota != self.pulsada else QColor("#666")
                painter.setBrush(color)
                painter.setPen(QColor("black"))
                painter.drawRect(x, 0, int(key_w / 2), int(h * 0.6))

    def mousePressEvent(self, event):
        nota = self.detectar_nota(event.x(), event.y())
        if nota is not None and nota != self.pulsada:
            self.pulsada = nota
            self.nota_presionada.emit(nota)
            self.update()

    def mouseMoveEvent(self, event):
        nota = self.detectar_nota(event.x(), event.y())
        if nota is not None and nota != self.pulsada:
            self.pulsada = nota
            self.nota_presionada.emit(nota)
            self.update()

    def mouseReleaseEvent(self, event):
        self.pulsada = None
        self.update()

    def detectar_nota(self, x, y):
        w = self.width()
        h = self.height()
        key_w = w / self.total_teclas_blancas

        # Detectar teclas negras primero
        for nota in self.negras:
            idx = self.get_white_index_before(nota)
            if idx is not None:
                key_x = (idx + 1) * key_w - key_w / 4
                if key_x <= x <= key_x + key_w / 2 and y < h * 0.6:
                    return nota

        # Detectar teclas blancas
        index = int(x // key_w)
        if 0 <= index < len(self.blancas):
            return self.blancas[index]
        return None

    def is_white(self, nota):
        return (nota % 12) not in [1, 3, 6, 8, 10]

    def get_white_index_before(self, nota):
        for i, b in enumerate(self.blancas):
            if b > nota:
                return i - 1
        return len(self.blancas) - 1
