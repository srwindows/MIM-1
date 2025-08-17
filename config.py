import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DIR_BANCOS = os.path.join(BASE_DIR, "Bancos")
DIR_ESCENAS = os.path.join(BASE_DIR, "Escenas")
DIR_IMAGENES = os.path.join(BASE_DIR, "Imagenes")
DIR_VSTS = os.path.join(BASE_DIR, "VSTs")

GRUPOS_GM = [
    "Pianos acústicos", "Pianos eléctricos", "Órganos", "Guitarras acústicas",
    "Guitarras eléctricas", "Bajos", "Cuerdas", "Metales", "Sintetizadores",
    "Pads", "Leads", "FX", "Percusión", "Baterías", "Coros", "Étnicos"
]
