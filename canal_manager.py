class Canal:
    def __init__(self, numero):
        self.numero = numero
        self.activo = True
        self.banco = None
        self.preset = None
        self.volumen = 100
        self.paneo = 0

    def asignar_instrumento(self, banco, preset):
        self.banco = banco
        self.preset = preset

class GestorCanales:
    def __init__(self):
        self.canales = [Canal(i) for i in range(16)]

    def get_canal(self, numero):
        return self.canales[numero]

    def activar(self, numero, estado):
        self.canales[numero].activo = estado

    def asignar(self, numero, banco, preset):
        self.canales[numero].asignar_instrumento(banco, preset)
