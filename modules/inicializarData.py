"""
Manejo de archivos JSON del proyecto
"""

from utils.archivos import (
    DATA_DIR,
    crear_directorio,
    escribir_json,
    leer_json,
    obtener_ruta_data
)


# Rutas de archivos
RUTA_ELECTROLINERAS = obtener_ruta_data(
    "electrolineras.json"
)

RUTA_PUNTOS_FIJOS = obtener_ruta_data(
    "puntos_fijos.json"
)

RUTA_CONFIGURACION = obtener_ruta_data(
    "configuracion.json"
)

RUTA_RESULTADOS = obtener_ruta_data(
    "resultados.json"
)


# Crear archivos base
def inicializar_archivos_base():

    crear_directorio(DATA_DIR)

    if not RUTA_ELECTROLINERAS.exists():
        escribir_json(
            RUTA_ELECTROLINERAS,
            []
        )

    if not RUTA_PUNTOS_FIJOS.exists():
        escribir_json(
            RUTA_PUNTOS_FIJOS,
            []
        )

    if not RUTA_CONFIGURACION.exists():
        escribir_json(
            RUTA_CONFIGURACION,
            {}
        )

    if not RUTA_RESULTADOS.exists():

        escribir_json(
            RUTA_RESULTADOS,
            {
                "simulaciones": [],
                "metricas_ml": [],
                "comparaciones": []
            }
        )

    return {
        "electrolineras": RUTA_ELECTROLINERAS,
        "puntos_fijos": RUTA_PUNTOS_FIJOS,
        "configuracion": RUTA_CONFIGURACION,
        "resultados": RUTA_RESULTADOS
    }

# Cargar electrolineras
def cargar_electrolineras():

    return leer_json(
        RUTA_ELECTROLINERAS,
        []
    )


# Guardar electrolineras
def guardar_electrolineras(
    electrolineras
):

    return escribir_json(
        RUTA_ELECTROLINERAS,
        electrolineras
    )


# Actualizar electrolinera
def actualizar_electrolinera(electrolinera_id,cambios):

    electrolineras = cargar_electrolineras()
    for electrolinera in electrolineras:
        if electrolinera["id"] == electrolinera_id:
            # Actualizar electrolinera
            electrolinera.update(cambios)
            guardar_electrolineras(electrolineras)
            return electrolinera

    raise ValueError("Electrolinera no encontrada")


# Eliminar electrolinera
def eliminar_electrolinera(electrolinera_id):

    electrolineras = cargar_electrolineras()
    nuevas = []
    for item in electrolineras:
        if item["id"] != electrolinera_id:
            nuevas.append(item)

    guardar_electrolineras(nuevas)
    return True

# Cargar puntos fijos
def cargar_puntos_fijos():

    return leer_json(
        RUTA_PUNTOS_FIJOS,
        []
    )


# Guardar puntos fijos
def guardar_puntos_fijos(puntos_fijos):

    return escribir_json(
        RUTA_PUNTOS_FIJOS,
        puntos_fijos
    )


# Agregar punto fijo
def agregar_punto_fijo(punto_fijo):

    puntos = cargar_puntos_fijos()

    for item in puntos:
        if item["id"] == punto_fijo["id"]:
            raise ValueError("El punto fijo ya existe")

    puntos.append(punto_fijo)
    guardar_puntos_fijos(puntos)
    return punto_fijo


# Actualizar punto fijo
def actualizar_punto_fijo(punto_fijo_id,cambios):

    puntos = cargar_puntos_fijos()
    for punto in puntos:
        if punto["id"] == punto_fijo_id:
            punto.update(cambios)
            guardar_puntos_fijos(puntos)
            return punto

    raise ValueError("Punto fijo no encontrado")


# Eliminar punto fijo
def eliminar_punto_fijo(punto_fijo_id):

    puntos = cargar_puntos_fijos()
    nuevos = []
    for item in puntos:
        if item["id"] != punto_fijo_id:
            nuevos.append(item)

    guardar_puntos_fijos(nuevos)
    return True

# Cargar configuración
def cargar_configuracion():

    return leer_json(
        RUTA_CONFIGURACION,
        {}
    )


# Guardar configuración
def guardar_configuracion(configuracion):

    return escribir_json(
        RUTA_CONFIGURACION,
        configuracion
    )

# Guardar resultados
def guardar_resultados(resultados):

    base = leer_json(
        RUTA_RESULTADOS,
        {
            "simulaciones": [],
            "metricas_ml": [],
            "comparaciones": []
        }
    )

    base.update(resultados)
    return escribir_json(
        RUTA_RESULTADOS,
        base
    )


# Cargar resultados
def cargar_resultados():

    return leer_json(
        RUTA_RESULTADOS,
        {
            "simulaciones": [],
            "metricas_ml": [],
            "comparaciones": []
        }
    )

# Cargar todos los datos
def cargar_datos_proyecto():

    datos = {
        "electrolineras":
            cargar_electrolineras(),

        "puntos_fijos":
            cargar_puntos_fijos(),

        "configuracion":
            cargar_configuracion()
    }

    datos["nodos"] = construir_catalogo_nodos(
        datos["electrolineras"],
        datos["puntos_fijos"]
    )

    return datos


# Crear lista de nodos
def construir_catalogo_nodos(electrolineras, puntos_fijos):

    nodos = []

    # Agregar puntos fijos
    for punto in puntos_fijos:

        nodos.append({
            "id": punto["id"],
            "nombre": punto["nombre"],
            "tipo": "punto_fijo",
            "latitud":
                punto["coordenadas"]["latitud"],
            "longitud":
                punto["coordenadas"]["longitud"]
        })

    # Agregar electrolineras
    for electrolinera in electrolineras:

        nodos.append({
            "id": electrolinera["id"],
            "nombre": electrolinera["nombre"],
            "tipo": "electrolinera",
            "latitud":
                electrolinera["latitud"],
            "longitud":
                electrolinera["longitud"],
            "capacidad":
                electrolinera.get(
                    "capacidad",
                    0
                ),
            "disponibilidad":
                electrolinera.get(
                    "disponibilidad",
                    0
                ),
            "potencia":
                electrolinera.get(
                    "potencia",
                    0
                )
        })

    return nodos
