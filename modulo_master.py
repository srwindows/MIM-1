from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QSizePolicy,
    QPushButton
)
from PyQt5.QtCore import Qt, QTimer
from dial_panoramico import DialPanoramico
from vumetro import Vumetro
import numpy as np

class ModuloMaster(QWidget):
    def __init__(self, motor_sonido):
        super().__init__()

        self.motor_sonido = motor_sonido

        self.setObjectName("ModuloMaster")
        self.setStyleSheet("""
        QWidget#ModuloMaster {
            background-color: transparent;
            border: 8px ridge black;
            border-radius: 6px;
            margin: 0px;
            padding: 0px; 
        }
        """)

        # ---------- Layout principal ----------
        main_layout = QVBoxLayout()
        main_layout.setSpacing(2)
        main_layout.setContentsMargins(92, 2, 55, 72)

        # ---------- Escalas de vumetros ----------
        escala_layout = QHBoxLayout()
        escala_izq = QLabel("0  -3  -6  -12  -24  -48  -60       dB")
        escala_der = QLabel("          60  -48  -24  -12  -6  -3  0")
        for escala in [escala_izq, escala_der]:
            escala.setStyleSheet("color: #aaa; font-size: 7pt;")
            escala.setAlignment(Qt.AlignLeft)
            escala.setFixedWidth(130)
            escala.setFixedHeight(13)
        escala_layout.addWidget(escala_izq)
        escala_layout.addWidget(escala_der)
        main_layout.addLayout(escala_layout)

        # ---------- Vumetros profesionales ----------
        vumetro_layout = QHBoxLayout()
        # Vumetro de mezcla izquierda (toda la mezcla estéreo)
        self.vumetro_izq = Vumetro(self.motor_sonido, canal_idx=0)
        self.vumetro_der = Vumetro(self.motor_sonido, canal_idx=1)
        self.vumetro_izq.setFixedHeight(18)
        self.vumetro_izq.setFixedWidth(130)
        self.vumetro_der.setFixedHeight(18)
        self.vumetro_der.setFixedWidth(130)
        vumetro_layout.addWidget(self.vumetro_izq)
        vumetro_layout.addWidget(self.vumetro_der)
        main_layout.addLayout(vumetro_layout)

        # ---------- Etiquetas ----------
        etiquetas_layout = QHBoxLayout()
        for texto in ["Master", "Balance", "Graves", "Medios", "Agudos"]:
            lbl = QLabel(texto)
            lbl.setStyleSheet("color: white; font-size: 8pt;")
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setFixedWidth(45)
            etiquetas_layout.addWidget(lbl)
        main_layout.addLayout(etiquetas_layout)

        # ---------- Controles ----------
        controles_layout = QHBoxLayout()
        controles_layout.setSpacing(2)

        # --- Master (fader vertical) ---
        self.slider_master = self.crear_slider_vertical(valor_inicial=100, funcion=self.cambiar_master)
        controles_layout.addLayout(self.slider_master["layout"])

        # --- Balance (Dial panorámico) ---
        balance_layout = QVBoxLayout()
        self.boton_on = QPushButton("ON")
        self.boton_on.setCheckable(True)
        self.boton_on.setChecked(True)
        self.boton_on.setFixedHeight(18)
        self.boton_on.setFixedWidth(30)
        self.boton_on.setStyleSheet("""
            QPushButton {
                background-color: #0a0; color: white;
                font-size: 7pt; padding: 1px; border-radius: 6px;
            }
            QPushButton:checked { background-color: #0f0; }
            QPushButton:!checked { background-color: #a00; }
        """)
        self.boton_on.toggled.connect(self.cambiar_estado)
        balance_layout.addWidget(self.boton_on, alignment=Qt.AlignCenter)
        self.dial_balance = DialPanoramico()
        self.dial_balance.setFixedSize(40, 40)
        self.dial_balance.valueChanged.connect(self.cambiar_balance)
        balance_layout.addWidget(self.dial_balance, alignment=Qt.AlignCenter)
        controles_layout.addLayout(balance_layout)

        # --- EQ: Graves ---
        self.slider_graves = self.crear_slider_vertical(valor_inicial=50, funcion=self.cambiar_eq)
        controles_layout.addLayout(self.slider_graves["layout"])

        # --- EQ: Medios ---
        self.slider_medios = self.crear_slider_vertical(valor_inicial=50, funcion=self.cambiar_eq)
        controles_layout.addLayout(self.slider_medios["layout"])

        # --- EQ: Agudos ---
        self.slider_agudos = self.crear_slider_vertical(valor_inicial=50, funcion=self.cambiar_eq)
        controles_layout.addLayout(self.slider_agudos["layout"])

        main_layout.addLayout(controles_layout)
        self.setLayout(main_layout)

        # -------- Inicializar valores en motor_sonido --------
        self.cambiar_master(self.slider_master["slider"].value())
        self.cambiar_balance(self.dial_balance.value)
        self.cambiar_eq()

        # -------- Timer para actualizar vumetros --------
        self.timer = QTimer()
        self.timer.timeout.connect(self.actualizar_vumetros)
        self.timer.start(50)

    def crear_slider_vertical(self, valor_inicial=50, funcion=None):
        layout = QVBoxLayout()
        interno = QHBoxLayout()
        interno.setSpacing(0)
        interno.setContentsMargins(22,0,0,0)

        ALTURA_FADER = 115

        escala = QVBoxLayout()
        escala.setSpacing(0)
        escala.setContentsMargins(0,0,0,0)
        for val in reversed(range(0, 101, 25)):
            lbl = QLabel(str(val))
            lbl.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            lbl.setStyleSheet("color: #888; font-size: 7pt;")
            escala.addWidget(lbl)

        widget_escala = QWidget()
        widget_escala.setLayout(escala)
        widget_escala.setFixedHeight(ALTURA_FADER)

        slider = QSlider(Qt.Vertical)
        slider.setRange(0, 100)
        slider.setValue(valor_inicial)
        slider.setFixedHeight(ALTURA_FADER)
        slider.setFixedWidth(12)
        slider.setStyleSheet("""
            QSlider::groove:vertical {
                background: qlineargradient(x1:0, y1:1, x2:0, y2:0,
                    stop:0 #111, stop:0.5 #4af, stop:1 #0ff);
                width: 6px; border-radius: 3px;
            }
            QSlider::handle:vertical {
                background: #0af;
                height: 14px;
                margin: -2px -3px;
                border-radius: 4px;
            }
        """)

        if funcion:
            slider.valueChanged.connect(lambda v: funcion(v))

        interno.addWidget(slider)
        interno.addWidget(widget_escala)
        layout.addLayout(interno)
        return {"layout": layout, "slider": slider}

    def cambiar_master(self, valor):
        v = valor / 100.0
        if self.motor_sonido and hasattr(self.motor_sonido, "set_master_volume"):
            self.motor_sonido.set_master_volume(v)

    def cambiar_balance(self, valor):
        if self.motor_sonido and hasattr(self.motor_sonido, "set_balance"):
            self.motor_sonido.set_balance(valor)

    def cambiar_eq(self, *_):
        graves = self.slider_graves["slider"].value() / 100.0
        medios = self.slider_medios["slider"].value() / 100.0
        agudos = self.slider_agudos["slider"].value() / 100.0
        if self.motor_sonido and hasattr(self.motor_sonido, "set_eq"):
            self.motor_sonido.set_eq(graves, medios, agudos)

    def cambiar_estado(self, estado):
        if self.motor_sonido and hasattr(self.motor_sonido, "set_master_on"):
            self.motor_sonido.set_master_on(estado)

    def actualizar_vumetros(self):
        # El Vumetro (clase personalizada) se encarga de actualizarse solo con motor_sonido
        pass
