from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTreeWidget, QTreeWidgetItem,
    QSizePolicy, QFileDialog, QMessageBox, QLabel, QMenu, QAction, QSplitter, QInputDialog, QScrollArea,
    QDialog, QDialogButtonBox, QComboBox
)
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QIcon, QFontMetrics
from lector_binario_sf2 import listar_presets_sf2
from modulo_master import ModuloMaster
import os
import json
import sounddevice as sd

AUDIO_CONFIG_PATH = os.path.expanduser("~/MIM-1-MODULAR/audio_config.json")

def guardar_audio_config(backend, device_id):
    config = {"backend": backend, "device_id": device_id}
    with open(AUDIO_CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=4)

def cargar_audio_config():
    if os.path.exists(AUDIO_CONFIG_PATH):
        with open(AUDIO_CONFIG_PATH, "r") as f:
            return json.load(f)
    return None

def aplicar_audio_config():
    config = cargar_audio_config()
    if not config: return
    try:
        backends = [api['name'] for api in sd.query_hostapis()]
        if config.get("backend") in backends:
            backend_index = backends.index(config["backend"])
            sd.default.hostapi = backend_index
        if isinstance(config.get("device_id"), int):
            sd.default.device = config["device_id"]
    except Exception as e:
        print("[AudioConfig] No se pudo aplicar configuración guardada:", e)

class AudioPropertiesDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Propiedades del audio")
        self.setMinimumWidth(420)
        self.setMinimumHeight(220)
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Backend de audio:"))
        self.combo_backend = QComboBox()
        try:
            self.backends = [api['name'] for api in sd.query_hostapis()]
            self.combo_backend.addItems(self.backends)
        except Exception as e:
            self.backends = []
            self.combo_backend.addItem("No detectado")
        layout.addWidget(self.combo_backend)

        layout.addWidget(QLabel("Tarjeta / Dispositivo de audio:"))
        self.combo_device = QComboBox()
        try:
            self.devices = sd.query_devices()
            self.device_names = [
                f"{i}: {d['name']} [{sd.query_hostapis()[d['hostapi']]['name']}]"
                for i, d in enumerate(self.devices) if d['max_output_channels'] > 0
            ]
            self.device_ids = [i for i, d in enumerate(self.devices) if d['max_output_channels'] > 0]
            self.combo_device.addItems(self.device_names)
        except Exception as e:
            self.device_ids = []
            self.combo_device.addItem("No detectado")
        layout.addWidget(self.combo_device)

        config = cargar_audio_config()
        if config:
            if config.get("backend") in self.backends:
                self.combo_backend.setCurrentIndex(self.backends.index(config["backend"]))
            if config.get("device_id") in self.device_ids:
                self.combo_device.setCurrentIndex(self.device_ids.index(config["device_id"]))

        layout.addWidget(QLabel("\nElige el backend y dispositivo a usar para el audio.\nRecuerda que hay que reiniciar la salida de audio para que tenga efecto."))

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def accept(self):
        backend = self.combo_backend.currentText()
        device_index = self.combo_device.currentIndex()
        device_id = self.device_ids[device_index] if self.device_ids else None
        guardar_audio_config(backend, device_id)
        aplicar_audio_config()
        super().accept()

# ----------------------- RESTO PANEL IZQUIERDO -----------------------

PRESETS_PATH = os.path.expanduser("~/MIM-1-MODULAR/presets")
ESCENARIOS_PATH = os.path.join(PRESETS_PATH, "escenarios")
INSTRUMENTOS_PATH = os.path.join(PRESETS_PATH, "instrumentos")
EXCLUSIVOS_PATH = os.path.join(PRESETS_PATH, "exclusivos.json")
BANCO_GUARDADO_PATH = os.path.join(PRESETS_PATH, "banco_guardado.json")
os.makedirs(ESCENARIOS_PATH, exist_ok=True)
os.makedirs(INSTRUMENTOS_PATH, exist_ok=True)

def obtener_categoria(preset):
    if 0 <= preset <= 7: return "Pianos"
    elif 24 <= preset <= 31: return "Guitarras"
    elif 32 <= preset <= 39: return "Bajos"
    elif 40 <= preset <= 47: return "Cuerdas"
    elif 48 <= preset <= 55: return "Vientos de Madera"
    elif 56 <= preset <= 63: return "Vientos de Metal"
    elif 64 <= preset <= 71: return "Órganos"
    elif 72 <= preset <= 79: return "Ensamble Vocal"
    elif 80 <= preset <= 87: return "Sintetizadores"
    elif 88 <= preset <= 95: return "Étnicos"
    elif 96 <= preset <= 103: return "Percusión Melódica"
    elif 118 <= preset <= 119: return "Efectos"
    elif 128 <= preset <= 135: return "Kits de Batería"
    else: return "Otros"

class PanelIzquierdo(QWidget):
    def __init__(self, panel_central_ref, motor_sonido=None):
        super().__init__()
        self.setMinimumWidth(60)
        self.setMaximumWidth(400)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.panel_central_ref = panel_central_ref
        self.motor_sonido = motor_sonido
        self.labels_canales = []
        self.nombres_sample_canales = [""] * 16

        self.init_ui()
        self._crear_estructura_presets()
        self._crear_estructura_exclusivos()
        self._cargar_banco_guardado()
        self.mostrar_banco()
        self._agregar_item_largo_test()
        self._actualizar_ancho_arbol()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(10)

        barra_top = QHBoxLayout()
        self.btn_audio = QPushButton(" Propiedades del audio")
        icon_path = os.path.expanduser("~/MIM-1-MODULAR/Iconos/audio.png")
        if os.path.exists(icon_path):
            self.btn_audio.setIcon(QIcon(icon_path))
        self.btn_audio.setStyleSheet("padding: 4px 12px; font-weight: bold;")
        self.btn_audio.clicked.connect(self.abrir_propiedades_audio)
        barra_top.addWidget(self.btn_audio)
        barra_top.addStretch()
        self.layout.addLayout(barra_top)

        botones_layout = QHBoxLayout()
        self.btn_banco = QPushButton("Banco")
        self.btn_banco.clicked.connect(self.mostrar_banco)
        botones_layout.addWidget(self.btn_banco)

        self.btn_exclusivos = QPushButton("Exclusivos")
        self.btn_exclusivos.clicked.connect(self.mostrar_exclusivos)
        botones_layout.addWidget(self.btn_exclusivos)

        self.btn_presets = QPushButton("Presets")
        self.btn_presets.clicked.connect(self.mostrar_presets)
        botones_layout.addWidget(self.btn_presets)

        self.layout.addLayout(botones_layout)

        self.btn_cargar_banco = QPushButton("Cargar banco SF2")
        self.btn_cargar_banco.clicked.connect(self.cargar_banco)
        self.layout.addWidget(self.btn_cargar_banco)

        self.splitter = QSplitter(Qt.Horizontal)
        self.layout.addWidget(self.splitter, stretch=1)

        self.tree_banco = QTreeWidget()
        self.tree_banco.setHeaderLabel("Instrumentos")
        self.tree_banco.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_banco.customContextMenuRequested.connect(self.abrir_menu_contextual)
        self.tree_banco.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.tree_banco.setHorizontalScrollMode(QTreeWidget.ScrollPerPixel)
        self.tree_banco.setUniformRowHeights(False)
        self.tree_banco.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.tree_banco.header().setSectionResizeMode(0, self.tree_banco.header().Fixed)
        self.tree_banco.header().resizeSection(0, 160)

        self.widget_arbol = QWidget()
        self.layout_arbol = QVBoxLayout(self.widget_arbol)
        self.layout_arbol.setContentsMargins(0,0,2,0)
        self.layout_arbol.addWidget(self.tree_banco)
        self.widget_arbol.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.scroll_banco = QScrollArea()
        self.scroll_banco.setWidgetResizable(True)
        self.scroll_banco.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_banco.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_banco.setFrameShape(QScrollArea.NoFrame)
        self.scroll_banco.setWidget(self.widget_arbol)
        self.scroll_banco.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.splitter.addWidget(self.scroll_banco)

        self.labels_widget = QWidget()
        self.labels_widget.setFixedWidth(155)
        self.labels_widget.setStyleSheet("background-color: #0a1d7d; border-radius: 7px;")
        self.lista_canales = QVBoxLayout(self.labels_widget)
        self.lista_canales.setContentsMargins(10, 10, 10, 10)
        self.lista_canales.setSpacing(6)
        for i in range(16):
            lbl = QLabel(f"CH {i+1}: -")
            lbl.setStyleSheet(
                "font-size: 8pt; color: #fff; font-weight: bold; padding: 3px 8px;"
                "background: transparent;"
            )
            lbl.setMinimumHeight(22)
            lbl.setMinimumWidth(152)
            lbl.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
            self.labels_canales.append(lbl)
            self.lista_canales.addWidget(lbl)
        self.splitter.addWidget(self.labels_widget)
        self.splitter.setSizes([200, 220])

        self.tree_presets = QTreeWidget()
        self.tree_presets.setHeaderLabel("Presets")
        self.tree_presets.setVisible(False)
        self.tree_presets.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_presets.customContextMenuRequested.connect(self.menu_presets)
        self.layout.addWidget(self.tree_presets)

        self.tree_exclusivos = QTreeWidget()
        self.tree_exclusivos.setHeaderLabel("Exclusivos")
        self.tree_exclusivos.setVisible(False)
        self.tree_exclusivos.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_exclusivos.customContextMenuRequested.connect(self.menu_exclusivos)
        self.layout.addWidget(self.tree_exclusivos)

        self.btn_reset = QPushButton("Resetear todo")
        self.btn_reset.clicked.connect(self._resetear_todo)
        self.layout.addWidget(self.btn_reset)

        self.modulo_master = ModuloMaster(self.motor_sonido)
        self.modulo_master.setFixedHeight(200)
        self.layout.addWidget(self.modulo_master)

    # ------------------ NUEVO: mostrar el nombre del sample en el canal ---------------
    def actualizar_nombre_sample_canal(self, canal, nombre_sample):
        canal = int(canal)
        anterior = self.nombres_sample_canales[canal]
        if anterior and anterior != nombre_sample:
            res = QMessageBox.question(
                self, "Reemplazar sample",
                f"El canal {canal+1} ya tiene asignado '{anterior}'.\n¿Quieres reemplazarlo por '{nombre_sample}'?",
                QMessageBox.Yes | QMessageBox.No
            )
            if res != QMessageBox.Yes:
                return
        self.nombres_sample_canales[canal] = nombre_sample
        self.labels_canales[canal].setText(f"CH {canal+1}: {nombre_sample}")

    def habilitar_drag_drop(self):
        self.tree_banco.setDragEnabled(True)
        self.tree_banco.setAcceptDrops(True)
        self.tree_banco.viewport().setAcceptDrops(True)
        self.tree_banco.setDropIndicatorShown(True)
        self.tree_banco.dragMoveEvent = self.dragMoveEvent_banco
        self.tree_banco.dropEvent = self.dropEvent_banco
        self.tree_exclusivos.setDragEnabled(True)
        self.tree_exclusivos.setAcceptDrops(True)
        self.tree_exclusivos.viewport().setAcceptDrops(True)
        self.tree_exclusivos.setDropIndicatorShown(True)
        self.tree_exclusivos.dragMoveEvent = self.dragMoveEvent_exclusivos
        self.tree_exclusivos.dropEvent = self.dropEvent_exclusivos
        self.tree_presets.setDragEnabled(True)
        self.tree_presets.setAcceptDrops(False)
        self.tree_presets.viewport().setAcceptDrops(False)
        self.tree_presets.setDropIndicatorShown(False)
        for label in self.labels_canales:
            label.setAcceptDrops(True)
            label.dragEnterEvent = self.dragEnterEvent_label
            label.dropEvent = self.dropEvent_label

    def dragMoveEvent_banco(self, event):
        event.accept()

    def dragMoveEvent_exclusivos(self, event):
        event.accept()

    def dragEnterEvent_label(self, event):
        event.accept()

    def dropEvent_banco(self, event):
        pass

    def dropEvent_exclusivos(self, event):
        item = self.tree_exclusivos.itemAt(event.pos())
        if not item:
            return
        datos = event.source().currentItem().data(0, Qt.UserRole)
        if not datos:
            return
        nombre, banco, preset, archivo = datos
        nombre_base = nombre
        nombres_existentes = [item.child(i).text(0) for i in range(item.childCount())]
        contador = 1
        nombre_nuevo = nombre_base
        while nombre_nuevo in nombres_existentes:
            contador += 1
            nombre_nuevo = f"{nombre_base}_{contador}"
        from PyQt5.QtWidgets import QInputDialog
        nuevo_nombre, ok = QInputDialog.getText(self, "Clonar instrumento",
                                f"Nombre para el nuevo instrumento en '{item.text(0)}':", text=nombre_nuevo)
        if ok and nuevo_nombre:
            item_nuevo = QTreeWidgetItem([nuevo_nombre])
            item_nuevo.setData(0, Qt.UserRole, (nuevo_nombre, banco, preset, archivo))
            item.addChild(item_nuevo)
            item.setExpanded(True)
            self._guardar_exclusivos()
            item_nuevo.setBackground(0, Qt.yellow)
        event.accept()

    def dropEvent_label(self, event):
        datos = event.source().currentItem().data(0, Qt.UserRole)
        if not datos:
            return
        ch = self.labels_canales.index(event.source().parent())
        nombre, banco, preset, archivo = datos
        res = QMessageBox.question(self, "Asignar instrumento",
                                   f"¿Asignar '{nombre}' a canal {ch+1}?",
                                   QMessageBox.Yes | QMessageBox.No)
        if res == QMessageBox.Yes:
            self.panel_central_ref.asignar_instrumento(nombre, banco, preset, archivo, ch)
            self.labels_canales[ch].setText(f"CH {ch+1}: {nombre}")
        event.accept()

    def abrir_propiedades_audio(self):
        dlg = AudioPropertiesDialog(self)
        dlg.exec_()

    def _actualizar_ancho_arbol(self):
        max_ancho = 160
        fm = QFontMetrics(self.tree_banco.font())
        def check_item(item, nivel=0):
            nonlocal max_ancho
            w = fm.width(item.text(0)) + 30 + nivel * 18
            if w > max_ancho:
                max_ancho = w
            for i in range(item.childCount()):
                check_item(item.child(i), nivel+1)
        for i in range(self.tree_banco.topLevelItemCount()):
            check_item(self.tree_banco.topLevelItem(i), 0)
        self.widget_arbol.setMinimumWidth(255)
        self.widget_arbol.setMaximumWidth(255)

    def _cargar_banco_guardado(self):
        if os.path.exists(BANCO_GUARDADO_PATH):
            with open(BANCO_GUARDADO_PATH) as f:
                archivo = json.load(f)
            if os.path.exists(archivo):
                self._cargar_y_guardar_banco(archivo)

    def mostrar_banco(self):
        self.btn_cargar_banco.setVisible(True)
        self.splitter.setVisible(True)
        self.tree_presets.setVisible(False)
        self.tree_exclusivos.setVisible(False)
        self.tree_banco.collapseAll()
        self._actualizar_ancho_arbol()

    def cargar_banco(self):
        archivo, _ = QFileDialog.getOpenFileName(self, "Seleccionar banco SoundFont", "", "SoundFont (*.sf2)")
        if archivo:
            self._cargar_y_guardar_banco(archivo)

    def _cargar_y_guardar_banco(self, archivo):
        self.tree_banco.clear()
        try:
            presets = listar_presets_sf2(archivo)
            agrupados = {}
            for nombre, banco, preset in presets:
                cat = obtener_categoria(preset)
                agrupados.setdefault(cat, []).append((nombre, banco, preset, archivo))
            for cat in sorted(agrupados):
                item_cat = QTreeWidgetItem([cat])
                icono = self.obtener_icono(cat)
                if icono:
                    item_cat.setIcon(0, icono)
                self.tree_banco.addTopLevelItem(item_cat)
                for i, (nombre, banco, preset, archivo) in enumerate(agrupados[cat], 1):
                    texto = f"{i:03d} - {nombre}"
                    item = QTreeWidgetItem([texto])
                    item.setData(0, Qt.UserRole, (nombre, banco, preset, archivo))
                    item.setToolTip(0, texto)
                    item_cat.addChild(item)
            self.tree_banco.collapseAll()
            with open(BANCO_GUARDADO_PATH, "w") as f:
                json.dump(archivo, f)
            self._actualizar_ancho_arbol()
        except Exception as e:
            QMessageBox.critical(self, "Error al cargar SF2", str(e))

    def _agregar_item_largo_test(self):
        item_cat = QTreeWidgetItem(["TestScroll"])
        self.tree_banco.addTopLevelItem(item_cat)
        nombre_largo = "ESTE ES UN NOMBRE DE INSTRUMENTO MUUUUUUUUUUY LARGO QUE SOBREPASA EL ANCHO DE LA COLUMNA PARA PROBAR EL SCROLL HORIZONTAL EN QTREEWIDGET"
        item = QTreeWidgetItem([nombre_largo])
        item.setData(0, Qt.UserRole, ("PruebaScroll", 0, 0, ""))
        item.setToolTip(0, nombre_largo)
        item_cat.addChild(item)

    def mostrar_presets(self):
        self.btn_cargar_banco.setVisible(False)
        self.splitter.setVisible(False)
        self.tree_presets.setVisible(True)
        self.tree_exclusivos.setVisible(False)

    def mostrar_exclusivos(self):
        self.btn_cargar_banco.setVisible(False)
        self.splitter.setVisible(False)
        self.tree_presets.setVisible(False)
        self.tree_exclusivos.setVisible(True)

    def abrir_menu_contextual(self, punto: QPoint):
        item = self.tree_banco.itemAt(punto)
        if item and item.data(0, Qt.UserRole):
            menu = QMenu(self)
            asignar_menu = menu.addMenu("Asignar a canal")
            for ch in range(16):
                asignar_menu.addAction(f"Canal {ch+1}", lambda ch=ch: self.asignar_a_canal(item, ch))
            menu.exec_(self.tree_banco.viewport().mapToGlobal(punto))

    def asignar_a_canal(self, item, canal):
        datos = item.data(0, Qt.UserRole)
        if datos and self.panel_central_ref:
            nombre, banco, preset, archivo = datos
            # --- AVISO si ya hay sample/instrumento ---
            anterior = self.nombres_sample_canales[canal]
            if anterior and anterior != nombre:
                res = QMessageBox.question(
                    self, "Reemplazar instrumento",
                    f"El canal {canal+1} ya tiene asignado '{anterior}'.\n¿Quieres reemplazarlo por '{nombre}'?",
                    QMessageBox.Yes | QMessageBox.No
                )
                if res != QMessageBox.Yes:
                    return
            self.panel_central_ref.asignar_instrumento(nombre, banco, preset, archivo, canal)
            self.labels_canales[canal].setText(f"CH {canal+1}: {nombre}")
            self.nombres_sample_canales[canal] = nombre


    def obtener_icono(self, categoria):
        base = os.path.expanduser("~/MIM-1-MODULAR/Iconos")
        nombre_archivo = categoria.lower().replace(" ", "_") + ".png"
        ruta = os.path.join(base, nombre_archivo)
        try:
            return QIcon(ruta) if os.path.exists(ruta) else None
        except Exception:
            return None

    def _resetear_todo(self):
        if self.panel_central_ref:
            self.panel_central_ref.resetear_todos_los_canales()
        for i in range(16):
            self.labels_canales[i].setText(f"CH {i+1}: -")
            self.nombres_sample_canales[i] = ""

    def _crear_estructura_presets(self):
        self.tree_presets.clear()
        escenario_item = QTreeWidgetItem(["Escenarios"])
        self.tree_presets.addTopLevelItem(escenario_item)
        for archivo in os.listdir(ESCENARIOS_PATH):
            if archivo.endswith(".json"):
                nombre = os.path.splitext(archivo)[0]
                escenario_item.addChild(QTreeWidgetItem([nombre]))

        instrumentos_item = QTreeWidgetItem(["Instrumentos"])
        self.tree_presets.addTopLevelItem(instrumentos_item)
        for archivo in os.listdir(INSTRUMENTOS_PATH):
            if archivo.endswith(".json"):
                nombre = os.path.splitext(archivo)[0]
                instrumentos_item.addChild(QTreeWidgetItem([nombre]))

    def menu_presets(self, punto):
        item = self.tree_presets.itemAt(punto)
        if not item:
            return
        if item.text(0) == "Escenarios":
            menu = QMenu(self)
            guardar = QAction("Guardar escenario", self)
            guardar.triggered.connect(self.guardar_escenario)
            menu.addAction(guardar)
            menu.exec_(self.tree_presets.viewport().mapToGlobal(punto))
        elif item.parent() and item.parent().text(0) == "Escenarios":
            menu = QMenu(self)
            cargar = QAction("Cargar escenario", self)
            cargar.triggered.connect(lambda: self.cargar_escenario(item.text(0)))
            eliminar = QAction("Eliminar escenario", self)
            eliminar.triggered.connect(lambda: self.eliminar_escenario(item))
            menu.addAction(cargar)
            menu.addAction(eliminar)
            menu.exec_(self.tree_presets.viewport().mapToGlobal(punto))
        elif item.parent() and item.parent().text(0) == "Instrumentos":
            menu = QMenu(self)
            asignar_menu = menu.addMenu("Asignar a canal")
            for ch in range(16):
                asignar_menu.addAction(
                    f"Canal {ch+1}", 
                    lambda ch=ch: self.asignar_instrumento_preset(item, ch)
                )
            eliminar = QAction("Eliminar instrumento", self)
            eliminar.triggered.connect(lambda: self.eliminar_instrumento_preset(item))
            menu.addAction(eliminar)
            menu.exec_(self.tree_presets.viewport().mapToGlobal(punto))

    def asignar_instrumento_preset(self, item, canal):
        nombre_preset = item.text(0)
        ruta = os.path.join(INSTRUMENTOS_PATH, nombre_preset + ".json")
        if os.path.exists(ruta):
            with open(ruta) as f:
                datos = json.load(f)
            if isinstance(datos, dict) and "datos" in datos:
                args = datos["datos"]
            elif isinstance(datos, list) and len(datos) == 4:
                args = datos
            else:
                QMessageBox.warning(self, "Error", "Preset corrupto o incompatible")
                return
            self.panel_central_ref.asignar_instrumento(*args, canal)
            nombre = args[0] if args[0] and args[0] != "Instrumento no seleccionado" else nombre_preset
            self.labels_canales[canal].setText(f"CH {canal+1}: {nombre}")

    def eliminar_instrumento_preset(self, item):
        nombre = item.text(0)
        confirm = QMessageBox.question(self, "Eliminar instrumento",
                                       f"¿Seguro que quieres eliminar el preset '{nombre}'?",
                                       QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            ruta = os.path.join(INSTRUMENTOS_PATH, nombre + ".json")
            if os.path.exists(ruta):
                os.remove(ruta)
            self._crear_estructura_presets()

    def guardar_escenario(self):
        nombre, ok = QInputDialog.getText(self, "Guardar escenario", "Nombre del escenario:")
        if ok and nombre:
            try:
                datos = self.panel_central_ref.obtener_estado_completo()
                ruta = os.path.join(ESCENARIOS_PATH, nombre + ".json")
                with open(ruta, "w") as f:
                    json.dump(datos, f, indent=4)
                self._crear_estructura_presets()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def cargar_escenario(self, nombre):
        ruta = os.path.join(ESCENARIOS_PATH, nombre + ".json")
        if os.path.exists(ruta):
            with open(ruta) as f:
                datos = json.load(f)
            try:
                self.panel_central_ref.cargar_estado_completo(datos)
                QMessageBox.information(self, "Cargar escenario", "Escenario cargado correctamente.")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def eliminar_escenario(self, item):
        nombre = item.text(0)
        ruta = os.path.join(ESCENARIOS_PATH, nombre + ".json")
        if os.path.exists(ruta):
            os.remove(ruta)
            self._crear_estructura_presets()

    def _crear_estructura_exclusivos(self):
        self.tree_exclusivos.clear()
        categorias = [
            "Pianos", "Guitarras", "Bajos", "Cuerdas", "Vientos de Madera", "Vientos de Metal",
            "Órganos", "Ensamble Vocal", "Sintetizadores", "Étnicos", "Percusión Melódica",
            "Efectos", "Kits de Batería", "Otros"
        ]
        if os.path.exists(EXCLUSIVOS_PATH):
            with open(EXCLUSIVOS_PATH, "r") as f:
                datos = json.load(f)
        else:
            datos = {cat: [] for cat in categorias}
        for cat in categorias:
            if cat not in datos:
                datos[cat] = []
        for categoria in categorias:
            cat_item = QTreeWidgetItem([categoria])
            self.tree_exclusivos.addTopLevelItem(cat_item)
            for nombre, banco, preset, archivo in datos.get(categoria, []):
                item = QTreeWidgetItem([nombre])
                item.setData(0, Qt.UserRole, (nombre, banco, preset, archivo))
                item.setToolTip(0, nombre)
                cat_item.addChild(item)

    def menu_exclusivos(self, punto):
        item = self.tree_exclusivos.itemAt(punto)
        menu = QMenu(self)
        if item and item.parent():
            asignar_menu = menu.addMenu("Asignar a canal")
            for ch in range(16):
                asignar_menu.addAction(f"Canal {ch+1}", lambda ch=ch: self.asignar_a_canal(item, ch))
            eliminar = QAction("Eliminar instrumento", self)
            eliminar.triggered.connect(lambda: self.eliminar_instrumento_exclusivo(item))
            menu.addAction(eliminar)
        elif item:
            agregar = QAction("Agregar SF2", self)
            agregar.triggered.connect(lambda: self.agregar_sf2_exclusivo(item))
            menu.addAction(agregar)
        menu.exec_(self.tree_exclusivos.viewport().mapToGlobal(punto))

    def agregar_sf2_exclusivo(self, categoria_item):
        archivo, _ = QFileDialog.getOpenFileName(self, "Añadir banco SF2", "", "SoundFont (*.sf2)")
        if not archivo:
            return
        presets = listar_presets_sf2(archivo)
        for i, (nombre, banco, preset) in enumerate(presets):
            item = QTreeWidgetItem([f"{i+1:03d} - {nombre}"])
            item.setData(0, Qt.UserRole, (nombre, banco, preset, archivo))
            item.setToolTip(0, f"{i+1:03d} - {nombre}")
            categoria_item.addChild(item)
        self._guardar_exclusivos()

    def eliminar_instrumento_exclusivo(self, item):
        padre = item.parent()
        if padre:
            padre.removeChild(item)
            self._guardar_exclusivos()

    def _guardar_exclusivos(self):
        datos = {}
        for i in range(self.tree_exclusivos.topLevelItemCount()):
            cat_item = self.tree_exclusivos.topLevelItem(i)
            nombre_cat = cat_item.text(0)
            instrumentos = []
            for j in range(cat_item.childCount()):
                hijo = cat_item.child(j)
                datos_inst = hijo.data(0, Qt.UserRole)
                if datos_inst:
                    instrumentos.append(datos_inst)
            datos[nombre_cat] = instrumentos
        with open(EXCLUSIVOS_PATH, "w") as f:
            json.dump(datos, f, indent=4)

