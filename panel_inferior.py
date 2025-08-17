from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QSizePolicy, QMenu, QAction, QFileDialog
)
from PyQt5.QtCore import Qt
import os
import tempfile
from pydub import AudioSegment
from dial_panoramico import DialPanoramico
from vumetro import Vumetro
from fader_led import FaderLED

class PanelInferior(QWidget):
    def __init__(self, panel_central_ref=None, panel_izquierdo_ref=None, motor_sonido=None):
        super().__init__()
        self.setMinimumSize(50, 50)
        self.setMaximumSize(1700, 1000)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.panel_central_ref = panel_central_ref
        self.panel_izquierdo_ref = panel_izquierdo_ref
        self.motor_sonido = motor_sonido

        self.faders = []
        self.diales = []
        self.botones = []
        self.nombres_wav = [""] * 16
        self.temp_wavs = {}  # para temporales MP3
        self.vumetros = []
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(1, 6, 4, 51)
        layout.setSpacing(10)
        self.setLayout(layout)

        ALT_FADER = 125
        ALT_LABEL = 3
        SIZE_DIAL = 40

        for i in range(16):
            canal = QVBoxLayout()
            canal.setAlignment(Qt.AlignHCenter)

            # Botón del canal
            btn = QPushButton(str(i+1))
            btn.setFixedWidth(32)
            btn.setFixedHeight(23)
            btn.setCheckable(True)
            btn.setContextMenuPolicy(Qt.CustomContextMenu)
            # CORRECTO: así solo ese canal tendrá su menú
            btn.customContextMenuRequested.connect(lambda punto, ch=i: self.abrir_menu_contextual(ch))
            self.botones.append(btn)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #2c2c2c;
                    color: white;
                    font: bold 13px Arial;
                    border-radius: 10px;
                    border: 2px solid #777;
                    padding: 2px 0;
                }
                QPushButton:checked {
                    background-color: #38e100;
                    color: #111;
                    border: 2px solid #2a0;
                }
            """)
            canal.addWidget(btn, alignment=Qt.AlignHCenter)
            btn.toggled.connect(lambda checked, ch=i: self.canal_activado_toggled(ch, checked))

            # FADER
            fader = FaderLED()
            fader.setValue(25)
            fader.setFixedHeight(135)
            fader.setFixedWidth(15)
            self.faders.append(fader)
            canal.addWidget(fader, alignment=Qt.AlignHCenter)
            fader.valueChanged.connect(lambda valor, ch=i: self.cambiar_volumen_canal(ch, valor))

            # DIAL PANORAMICO
            dial = DialPanoramico()
            dial.setFixedSize(SIZE_DIAL, SIZE_DIAL)
            dial.setValue(0)
            self.diales.append(dial)
            canal.addWidget(dial, alignment=Qt.AlignHCenter)
            dial.valueChanged.connect(lambda valor, ch=i: self.cambiar_paneo_canal(ch, valor + 64))

            # VUMETRO ESTÉREO
            vumetro = Vumetro(self.motor_sonido, canal_idx=i)
            vumetro.setFixedHeight(100)
            vumetro.setFixedWidth(15)
            self.vumetros.append(vumetro)
            canal.addWidget(vumetro, alignment=Qt.AlignHCenter)

            layout.addLayout(canal)

    def abrir_menu_contextual(self, canal):
        menu = QMenu(self)
        cargar_audio = QAction("Cargar WAV o MP3 (sample)", self)
        cargar_audio.triggered.connect(lambda: self.cargar_audio_canal(canal))
        menu.addAction(cargar_audio)
        boton = self.botones[canal]
        menu.exec_(boton.mapToGlobal(boton.rect().bottomLeft()))

    def cargar_audio_canal(self, canal):
        opciones = "Archivos de audio (*.wav *.mp3)"
        ruta, _ = QFileDialog.getOpenFileName(self, "Selecciona un archivo de audio", "", opciones)
        if ruta and self.motor_sonido:
            ext = os.path.splitext(ruta)[1].lower()
            if ext == ".mp3":
                audio = AudioSegment.from_mp3(ruta)
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
                audio.export(temp_file.name, format="wav")
                ruta_wav = temp_file.name
                self.temp_wavs[canal] = ruta_wav
            else:
                ruta_wav = ruta
            self.motor_sonido.asignar_sample(canal, ruta_wav)
            nombre = os.path.basename(ruta)
            self.nombres_wav[canal] = nombre
            # Actualiza SOLO el canal correcto en el panel izquierdo
            if self.panel_izquierdo_ref:
                self.panel_izquierdo_ref.actualizar_nombre_sample_canal(canal, nombre)

    def canal_activado_toggled(self, canal, activo):
        pass

    def cambiar_volumen_canal(self, canal, valor):
        if self.motor_sonido:
            self.motor_sonido.set_volumen(canal, valor)

    def cambiar_paneo_canal(self, canal, valor):
        if self.motor_sonido:
            self.motor_sonido.set_paneo(canal, valor)

    def obtener_canales_activos(self):
        return [i for i, btn in enumerate(self.botones) if btn.isChecked()]
