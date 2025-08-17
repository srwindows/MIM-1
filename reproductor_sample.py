# reproductor_sample.py – Usa motor_sonido para lanzar sonidos desde código
from motor_sonido import ReproductorSample

def prueba_sample(ruta_wav):
    motor = ReproductorSample()
    motor.reproducir_wave(ruta_wav)
    motor.cerrar()

if __name__ == "__main__":
    prueba_sample("tests/sample.wav")  # ← cambia esto a tu sample
