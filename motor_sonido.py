import numpy as np
import threading
import sounddevice as sd
import wave
from pydub import AudioSegment
from lector_samples_sf2 import extraer_seccion_smpl

MAX_POLIFONIA = 512
SR = 44100

def cargar_wav(path):
    with wave.open(path, "rb") as wavf:
        frames = wavf.readframes(wavf.getnframes())
        datos = np.frombuffer(frames, dtype=np.int16)
        return datos, wavf.getframerate()

def cargar_mp3(path):
    audio = AudioSegment.from_mp3(path)
    y = np.array(audio.get_array_of_samples())
    if audio.channels == 2:
        y = y.reshape((-1, 2))
        y = y.mean(axis=1).astype(np.int16)
    return y, audio.frame_rate

def cargar_sf2_sample(path_sf2):
    data = extraer_seccion_smpl(path_sf2)
    if data is None:
        print("[ERROR al cargar muestras SF2] Archivo no encontrado:", path_sf2)
        return None, SR
    audio = np.frombuffer(data, dtype=np.int16)
    return audio, SR

def pitch_shift(data, orig_note, target_note):
    ratio = 2 ** ((target_note - orig_note) / 12)
    idx = np.round(np.arange(0, len(data), 1/ratio)).astype(int)
    idx = idx[idx < len(data)]
    return data[idx]

def eq_simple_numpy(audio, sr, graves=0.5, medios=0.5, agudos=0.5):
    """
    Ecualizador simple 3 bandas solo con numpy FFT.
    graves, medios, agudos: 0.0 a 1.0 (ganancia de cada banda)
    """
    if audio.ndim == 1:
        audio = np.stack([audio, audio], axis=1)  # Fuerza estéreo

    n = audio.shape[0]
    X_L = np.fft.rfft(audio[:, 0])
    X_R = np.fft.rfft(audio[:, 1])
    freqs = np.fft.rfftfreq(n, 1/sr)

    # Bandas: Graves <400Hz, Medios 400-4000Hz, Agudos >4000Hz
    low = freqs < 400
    mid = (freqs >= 400) & (freqs < 4000)
    high = freqs >= 4000

    X_L[low] *= graves
    X_L[mid] *= medios
    X_L[high] *= agudos

    X_R[low] *= graves
    X_R[mid] *= medios
    X_R[high] *= agudos

    audio_L = np.fft.irfft(X_L, n)
    audio_R = np.fft.irfft(X_R, n)
    audio_out = np.stack([audio_L, audio_R], axis=1)
    audio_out = np.clip(audio_out, -32768, 32767)
    return audio_out.astype(np.int16)

class PolifoniaManager:
    def __init__(self, max_voices=512):
        self.voices = []
        self.max_voices = max_voices
        self.lock = threading.Lock()
    def note_on(self, datos, nota_midi, canal, sr=SR, velocity=127, base_note=60, volumen=1.0, paneo=64):
        if datos is None: return
        pan = np.clip(paneo, 0, 127) / 127.0
        vol_L = np.cos(pan * np.pi / 2) * volumen * (velocity / 127)
        vol_R = np.sin(pan * np.pi / 2) * volumen * (velocity / 127)
        samples = pitch_shift(datos, base_note, nota_midi).astype(np.float32)
        data_L = samples * vol_L
        data_R = samples * vol_R
        data_stereo = np.stack([data_L, data_R], axis=1)
        voice = {
            "data": data_stereo,
            "sr": sr,
            "pos": 0,
            "active": True,
            "canal": canal,
            "nota": nota_midi
        }
        with self.lock:
            if len(self.voices) >= self.max_voices:
                self.voices.pop(0)
            self.voices.append(voice)
    def note_off(self, canal, nota_midi):
        with self.lock:
            for v in self.voices:
                if v["canal"] == canal and v["nota"] == nota_midi:
                    v["active"] = False
    def mix(self, length=2048):
        output = np.zeros((length, 2), dtype=np.float32)
        remove = []
        with self.lock:
            for v in self.voices:
                disp = len(v["data"]) - v["pos"]
                fin = min(disp, length)
                if fin <= 0 or not v["active"]:
                    remove.append(v)
                    continue
                data_chunk = v["data"][v["pos"]:v["pos"]+fin]
                if len(data_chunk) < length:
                    output[:len(data_chunk)] += data_chunk
                else:
                    output[:length] += data_chunk[:length]
                v["pos"] += fin
                if v["pos"] >= len(v["data"]):
                    remove.append(v)
            for v in remove:
                self.voices.remove(v)
        output = np.clip(output, -32768, 32767)
        return output.astype(np.int16)

class MotorSonido:
    def __init__(self):
        self.samples = [None]*16
        self.types = [None]*16
        self.sr = [SR]*16
        self.base_note = [60]*16
        self.volumen = [1.0]*16
        self.paneo = [64]*16  # 0=izq, 127=der, 64=centro
        self.voices = PolifoniaManager(MAX_POLIFONIA)
        self._stream = None
        self._last_output = np.zeros((2048,2), dtype=np.int16)
        self._running = True

        # MASTER / EQ
        self._master_vol = 1.0         # 0.0 - 1.0
        self._balance = 0              # -100 (izq) ... 0 ... 100 (der)
        self._eq_graves = 0.5          # 0.0 - 1.0
        self._eq_medios = 0.5          # 0.0 - 1.0
        self._eq_agudos = 0.5          # 0.0 - 1.0
        self._master_on = True         # True = salida activa

        self._start_audio()

    def reset(self):
        self.samples = [None]*16
        self.types = [None]*16
        self.sr = [SR]*16
        self.base_note = [60]*16
        self.volumen = [1.0]*16
        self.paneo = [64]*16
        self.voices = PolifoniaManager(MAX_POLIFONIA)

    def asignar_sample(self, canal, ruta, nota_base=60):
        if ruta.lower().endswith(".wav"):
            datos, sr = cargar_wav(ruta)
            self.samples[canal] = datos
            self.sr[canal] = sr
            self.types[canal] = "wav"
            self.base_note[canal] = nota_base
        elif ruta.lower().endswith(".mp3"):
            datos, sr = cargar_mp3(ruta)
            self.samples[canal] = datos
            self.sr[canal] = sr
            self.types[canal] = "mp3"
            self.base_note[canal] = nota_base
        else:
            print("[ERROR] Formato no soportado")

    def asignar_sf2(self, canal, ruta_sf2, banco=0, preset=0, nota_base=60):
        datos, sr = cargar_sf2_sample(ruta_sf2)
        if datos is not None:
            self.samples[canal] = datos
            self.sr[canal] = sr
            self.types[canal] = "sf2"
            self.base_note[canal] = nota_base

    def nota_on(self, canal, nota_midi, velocity=127):
        datos = self.samples[canal]
        if datos is None:
            print(f"[Canal {canal}] No hay instrumento asignado")
            return
        base_note = self.base_note[canal]
        sr = self.sr[canal]
        volumen = self.volumen[canal]
        paneo = self.paneo[canal]
        self.voices.note_on(datos, nota_midi, canal, sr, velocity, base_note, volumen, paneo)

    def nota_off(self, canal, nota_midi):
        self.voices.note_off(canal, nota_midi)

    def set_volumen(self, canal, valor):
        self.volumen[canal] = float(valor) / 100.0

    def set_paneo(self, canal, valor):
        self.paneo[canal] = int(valor)

    # ---------------- MASTER Y EQ GLOBALES -----------------

    def set_master_volume(self, valor):
        """0.0 - 1.0"""
        self._master_vol = max(0.0, min(1.0, float(valor)))

    def set_balance(self, valor):
        """-100 a 100, 0 es centro"""
        self._balance = int(valor)

    def set_eq(self, graves, medios, agudos):
        """Cada uno 0.0 a 1.0"""
        self._eq_graves = max(0.0, min(1.0, float(graves)))
        self._eq_medios = max(0.0, min(1.0, float(medios)))
        self._eq_agudos = max(0.0, min(1.0, float(agudos)))

    def set_master_on(self, estado):
        """True=activo, False=mute total"""
        self._master_on = bool(estado)

    # -------------------------------------------------------

    def _callback(self, outdata, frames, time, status):
        mix = self.voices.mix(frames).astype(np.float32)   # (-32768..32767)
        if mix.shape[1] == 1:
            mix = np.repeat(mix, 2, axis=1)
        # --- EQ simple ---
        if not self._master_on:
            mix *= 0
        else:
            # Balance L-R (panorama global)
            bal = self._balance
            if bal < 0:
                lmul = 1.0
                rmul = (100+bal)/100
            elif bal > 0:
                lmul = (100-bal)/100
                rmul = 1.0
            else:
                lmul = rmul = 1.0
            mix[:,0] *= lmul
            mix[:,1] *= rmul
            # EQ usando solo numpy (sin scipy)
            eq_g = self._eq_graves
            eq_m = self._eq_medios
            eq_a = self._eq_agudos
            mix = eq_simple_numpy(mix, self.sr[0] if self.sr else SR, eq_g, eq_m, eq_a)
            # Master volumen
            mix = mix.astype(np.float32) * self._master_vol
        # Clip a rango int16
        mix = np.clip(mix, -32768, 32767).astype(np.int16)
        self._last_output = mix
        outdata[:] = mix

    def _start_audio(self):
        print("[MotorSonido] Iniciando audio (estéreo)")
        self._stream = sd.OutputStream(
            channels=2, samplerate=SR, dtype='int16',
            callback=self._callback, blocksize=2048
        )
        self._stream.start()

    def get_salida_actual(self):
        return self._last_output

    def close(self):
        self._running = False
        if self._stream:
            self._stream.stop()
            self._stream.close()
