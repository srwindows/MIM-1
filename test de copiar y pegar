from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QTreeWidget, QTreeWidgetItem, QMessageBox
from PyQt5.QtCore import Qt
import sys

class DragLabel(QLabel):
    def __init__(self, text, index, parent=None):
        super().__init__(text, parent)
        self.index = index
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        event.acceptProposedAction()
        self.setStyleSheet("background-color: yellow;")  # Para ver que entra

    def dragLeaveEvent(self, event):
        self.setStyleSheet("")  # Quita color al salir

    def dropEvent(self, event):
        datos = event.mimeData().text()
        if datos:
            reply = QMessageBox.question(self, "Asignar", f"¿Asignar '{datos}' al canal {self.index+1}?", QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.setText(f"CH {self.index+1}: {datos}")
        self.setStyleSheet("")
        event.acceptProposedAction()

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Drag & Drop Demo")
        layout = QVBoxLayout(self)
        # Árbol con instrumentos
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("Instrumentos")
        for name in ["Piano", "Guitarra", "Bajo"]:
            item = QTreeWidgetItem([name])
            self.tree.addTopLevelItem(item)
        self.tree.setDragEnabled(True)
        self.tree.startDrag = self.startDrag  # Monkey patch
        layout.addWidget(self.tree)
        # Etiquetas de canales
        self.labels = []
        for i in range(4):
            lbl = DragLabel(f"CH {i+1}: -", i)
            lbl.setStyleSheet("padding: 6px; border: 1px solid #333;")
            self.labels.append(lbl)
            layout.addWidget(lbl)

    def startDrag(self, supportedActions):
        item = self.tree.currentItem()
        if item:
            from PyQt5.QtCore import QMimeData
            from PyQt5.QtGui import QDrag
            mime = QMimeData()
            mime.setText(item.text(0))
            drag = QDrag(self.tree)
            drag.setMimeData(mime)
            drag.exec_(Qt.CopyAction)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.resize(350, 400)
    win.show()
    sys.exit(app.exec_())
