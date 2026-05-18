"""
Funciones básicas para manejar archivos JSON
"""

import json
from pathlib import Path

# Rutas principales
BASE_DIR = Path(__file__).resolve().parents[1]

DATA_DIR = BASE_DIR / "data"
MAPS_DIR = BASE_DIR / "maps"
MODELS_DIR = BASE_DIR / "models"


# Crear carpeta si no existe
def crear_directorio(ruta):
    ruta = Path(ruta)

    # Uso de comando mkdir para la creación de carpetas
    if not ruta.exists():
        ruta.mkdir(parents=True)

    return ruta


# Leer archivo JSON
def leer_json(ruta, valor_defecto=None):
    ruta = Path(ruta)

    # Si el archivo no existe
    if not ruta.exists():
        if valor_defecto is None:
            return {}
        else:
            return valor_defecto

    # Abrir y leer archivo
    with open(ruta, "r", encoding="utf-8") as archivo:
        datos = json.load(archivo)

    return datos


# Guardar archivo JSON
def escribir_json(ruta, datos):
    ruta = Path(ruta)

    # Crear carpeta padre
    crear_directorio(ruta.parent)

    # Escribir archivo
    with open(ruta, "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, indent=4, ensure_ascii=False)

    return ruta


# Obtener ruta de la carpeta data
def obtener_ruta_data(nombre_archivo):
    crear_directorio(DATA_DIR)
    return DATA_DIR / nombre_archivo


# Obtener ruta de la carpeta maps
def obtener_ruta_mapa(nombre_archivo):
    crear_directorio(MAPS_DIR)
    return MAPS_DIR / nombre_archivo


# Obtener ruta de la carpeta models
def obtener_ruta_modelo(nombre_archivo):
    crear_directorio(MODELS_DIR)
    return MODELS_DIR / nombre_archivo