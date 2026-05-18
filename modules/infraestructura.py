"""
Gestión de infraestructura vial
"""

import math
import modules.inicializarData as ini


# Agregar electrolinera
def agregar_electrolinera_con_conexiones(electrolinera,conexiones=2):

    datos = ini.cargar_datos_proyecto()

    # Validar si existe
    for item in datos["electrolineras"]:

        if item["id"] == electrolinera["id"]:
            raise ValueError("La electrolinera ya existe")

    # Guardar electrolinera
    electrolineras = ini.cargar_electrolineras()

    electrolineras.append(electrolinera)

    ini.guardar_electrolineras(electrolineras)

    # Crear conexiones
    configuracion = ini.cargar_configuracion()

    enlaces = crear_enlaces_para_nodo(
        {
            "id": electrolinera["id"],
            "latitud": electrolinera["latitud"],
            "longitud": electrolinera["longitud"]
        },
        datos["nodos"],
        conexiones
    )

    configuracion.setdefault(
        "aristas",
        []
    )

    configuracion["aristas"].extend(
        enlaces
    )

    ini.guardar_configuracion(
        configuracion
    )

    return electrolinera


# Agregar punto fijo
def agregar_punto_fijo_con_conexiones(punto_fijo,conexiones=2):

    datos = ini.cargar_datos_proyecto()

    # Validar si existe
    for item in datos["puntos_fijos"]:
        if item["id"] == punto_fijo["id"]:
            raise ValueError("El punto fijo ya existe")

    # Guardar punto fijo
    puntos = ini.cargar_puntos_fijos()
    puntos.append(punto_fijo)
    ini.guardar_puntos_fijos(puntos)

    # Crear conexiones
    configuracion = ini.cargar_configuracion()

    enlaces = crear_enlaces_para_nodo(
        {
            "id": punto_fijo["id"],
            "latitud":
                punto_fijo["coordenadas"]["latitud"],
            "longitud":
                punto_fijo["coordenadas"]["longitud"]
        },
        datos["nodos"],
        conexiones
    )

    # Validación si la palabra aristas no existe la crea como una lista vacoa
    configuracion.setdefault("aristas", [])
    #extend añade elementos a la lista ya existente
    configuracion["aristas"].extend( enlaces)
    ini.guardar_configuracion(configuracion)

    return punto_fijo


# Eliminar electrolinera  y las conexiones asociadas a esta
def eliminar_electrolinera_con_conexiones(electrolinera_id):

    eliminado = ini.eliminar_electrolinera(electrolinera_id)

    if not eliminado:
        return False

    eliminar_conexiones_nodo(electrolinera_id)

    return True


# Actualizar disponibilidad electrolinera
def actualizar_disponibilidad_estacion(electrolinera_id, disponibilidad):

    return ini.actualizar_electrolinera(
        electrolinera_id,
        {
            "disponibilidad":
                int(disponibilidad)
        }
    )


# Actualizar punto fijo
def actualizar_punto_fijo_con_conexiones(punto_fijo_id, cambios):

    punto = ini.actualizar_punto_fijo(punto_fijo_id, cambios)

    eliminar_conexiones_nodo(punto_fijo_id)

    datos = ini.cargar_datos_proyecto()
    configuracion = ini.cargar_configuracion()

    enlaces = crear_enlaces_para_nodo(
        {
            "id": punto["id"],
            "latitud":
                punto["coordenadas"]["latitud"],
            "longitud":
                punto["coordenadas"]["longitud"]
        },
        datos["nodos"],
        2
    )

    configuracion.setdefault("aristas", [])

    configuracion["aristas"].extend(enlaces)

    ini.guardar_configuracion(configuracion)

    return punto


# Eliminar punto fijo
def eliminar_punto_fijo_con_conexiones(punto_fijo_id):

    eliminado = ini.eliminar_punto_fijo(punto_fijo_id)

    if not eliminado:
        return False

    eliminar_conexiones_nodo(punto_fijo_id)

    return True


# Eliminar conexiones de un nodo
def eliminar_conexiones_nodo(nodo_id):

    configuracion = ini.cargar_configuracion()

    nuevas_aristas = []

    for arista in configuracion.get("aristas", []):
        if (arista["origen"] != nodo_id and arista["destino"] != nodo_id):
            nuevas_aristas.append(arista)

    configuracion["aristas"] = (nuevas_aristas)

    ini.guardar_configuracion(configuracion)


# Crear enlaces automáticos
def crear_enlaces_para_nodo(nodo_nuevo,nodos_existentes,conexiones):

    candidatos = []

    # Calcular distancias
    for nodo in nodos_existentes:

        if nodo["id"] == nodo_nuevo["id"]:
            continue

        distancia = haversine_km(
            nodo_nuevo["latitud"],
            nodo_nuevo["longitud"],
            nodo["latitud"],
            nodo["longitud"]
        )

        candidatos.append({
            "id": nodo["id"],
            "distancia": distancia
        })

    # Ordenar por distancia
    candidatos.sort(key=lambda x: x["distancia"])

    enlaces = []

    # Crear conexiones
    for item in candidatos[:conexiones]:

        distancia = item["distancia"]

        tiempo = (distancia / 24) * 60

        enlaces.append({
            "origen":
                nodo_nuevo["id"],

            "destino":
                item["id"],

            "distancia_km":
                round(distancia, 2),

            "tiempo_min":
                round(tiempo, 2),

            "consumo_kwh":
                round(distancia * 0.18,2)
        })

    return enlaces


# Calcular distancia entre coordenadas con la fórmula del Haversine
# Calcula la distancia en línea recta en km entre dos puntos a partir de la latitud y la longitud
def haversine_km(lat1,lon1,lat2,lon2):

    # Radio de la tierra en km
    radio_tierra = 6371

    # Punto uno latitud y longitud
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)

    # Punto dos latitud y longitud
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    diferencia_lat = lat2 - lat1
    diferencia_lon = lon2 - lon1

    a = (math.sin(diferencia_lat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(diferencia_lon / 2) ** 2)

    c = (2* math.atan2(math.sqrt(a),math.sqrt(1 - a)))

    distancia = radio_tierra * c

    return distancia