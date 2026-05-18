"""
Estadisticas de uso de electrolineras y puntos estrategicos.
"""

from collections import Counter

import networkx as nx

from modules.rutas import buscar_electrolinera_cercana


def calcular_estadisticas_electrolineras(grafo, simulaciones, limite_puntos=5):

    simulaciones_planas = _normalizar_simulaciones(simulaciones)
    contador_estaciones = Counter()
    total_recargas = 0
    total_alertas = 0

    for simulacion in simulaciones_planas:
        estaciones = simulacion.get("electrolineras_utilizadas", [])
        if not estaciones:
            estaciones = simulacion.get("electrolineras_sugeridas", [])
        if not estaciones:
            estaciones = [
                {
                    "estacion_id": recarga.get("estacion_id"),
                    "estacion_nombre": recarga.get("estacion_nombre")
                }
                for recarga in simulacion.get("recargas", [])
            ]
        if not estaciones:
            estaciones = [
                {
                    "estacion_id": alerta.get("estacion_id"),
                    "estacion_nombre": alerta.get("estacion_nombre")
                }
                for alerta in simulacion.get("alertas_bateria", [])
            ]

        for estacion in estaciones:
            estacion_id = estacion.get("estacion_id")
            nombre = estacion.get("estacion_nombre", estacion_id)
            if estacion_id:
                contador_estaciones[(estacion_id, nombre)] += 1

        total_recargas += max(
            len(simulacion.get("electrolineras_utilizadas", [])),
            len(simulacion.get("electrolineras_sugeridas", [])),
            len(simulacion.get("recargas", []))
        )
        total_alertas += len(simulacion.get("alertas_bateria", []))

    electrolinera_mas_usada = None
    if contador_estaciones:
        (estacion_id, nombre), usos = contador_estaciones.most_common(1)[0]
        electrolinera_mas_usada = {
            "id": estacion_id,
            "nombre": nombre,
            "usos": usos
        }

    return {
        "total_simulaciones": len(simulaciones_planas),
        "total_recargas": total_recargas,
        "total_alertas": total_alertas,
        "electrolinera_mas_usada": electrolinera_mas_usada,
        "puntos_estrategicos": calcular_puntos_estrategicos(
            grafo,
            simulaciones_planas,
            limite=limite_puntos
        )
    }


def calcular_puntos_estrategicos(grafo, simulaciones, limite=5):

    frecuencias = Counter()
    centralidad = {}

    if grafo.number_of_nodes() > 1:
        centralidad = nx.betweenness_centrality(
            grafo,
            weight="distancia_km"
        )

    for simulacion in simulaciones:
        for nodo in simulacion.get("ruta_final", []):
            if grafo.nodes.get(nodo, {}).get("tipo") == "punto_fijo":
                frecuencias[nodo] += 1

        for alerta in simulacion.get("alertas_bateria", []):
            nodo = alerta.get("nodo")
            if grafo.nodes.get(nodo, {}).get("tipo") == "punto_fijo":
                frecuencias[nodo] += 2

    candidatos = []

    for nodo, datos in grafo.nodes(data=True):
        if datos.get("tipo") != "punto_fijo":
            continue

        estacion = buscar_electrolinera_cercana(
            grafo,
            nodo,
            peso="distancia_km"
        )

        distancia = 9999.0
        estacion_nombre = "Sin electrolinera cercana"

        if estacion is not None:
            distancia = float(estacion.get("distancia_km", 9999.0))
            estacion_nombre = estacion.get("estacion_nombre", estacion.get("estacion_id", "-"))

        frecuencia = frecuencias.get(nodo, 0)
        valor_centralidad = float(centralidad.get(nodo, 0.0))
        puntaje = round((frecuencia * 2.0) + distancia + (valor_centralidad * 10.0), 2)

        candidatos.append({
            "id": nodo,
            "nombre": datos.get("nombre", nodo),
            "frecuencia_rutas": frecuencia,
            "centralidad": round(valor_centralidad, 4),
            "distancia_electrolinera_km": round(distancia, 2),
            "electrolinera_cercana": estacion_nombre,
            "puntaje": puntaje
        })

    candidatos.sort(
        key=lambda item: (
            item["puntaje"],
            item["frecuencia_rutas"],
            item["distancia_electrolinera_km"]
        ),
        reverse=True
    )

    return candidatos[:limite]


def _normalizar_simulaciones(simulaciones):

    simulaciones_planas = []

    for simulacion in simulaciones or []:
        if isinstance(simulacion, dict) and simulacion.get("simulaciones"):
            simulaciones_planas.extend(simulacion["simulaciones"])
        elif isinstance(simulacion, dict):
            simulaciones_planas.append(simulacion)

    return simulaciones_planas
