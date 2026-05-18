"""Visualizacion del grafo, nodos y rutas en diferentes formatos."""

from __future__ import annotations

from pathlib import Path
from typing import Any
import folium
import networkx as nx

from utils.archivos import crear_directorio, obtener_ruta_mapa


COLORES_NODO = {
    "electrolinera": "green",
    "punto_fijo": "blue",
}

# Exportar visualizaciones principales
def exportar_visualizaciones(grafo, ruta=None, nombre_base="red_vial"):

    # Crear carpeta de mapas
    carpeta = Path(obtener_ruta_mapa("temp.tmp")).parent
    crear_directorio(carpeta)

    archivos = {
        "folium": str(
            exportar_mapa_folium(
                grafo,
                ruta,
                nombre_base + "_folium.html"
            )
        )
    }

    return archivos


# Crea un mapa interactivo HTML con Folium.
# Exportar visualizaciones principales
def exportar_visualizaciones(grafo, ruta=None, nombre_base="red_vial"):

    # Crear carpeta de mapas
    carpeta = Path(obtener_ruta_mapa("temp.tmp")).parent
    crear_directorio(carpeta)

    archivos = {
        "folium": str(
            exportar_mapa_folium(
                grafo,
                ruta,
                nombre_base + "_folium.html"
            )
        )
    }

    return archivos


# Crear mapa HTML con Folium
def exportar_mapa_folium(grafo, ruta, nombre_archivo):

    # Obtener centro del mapa
    centro_lat, centro_lon = calcular_centro_mapa(grafo)

    # Crear mapa
    mapa = folium.Map(
        location=[centro_lat, centro_lon],
        zoom_start=12,
        tiles="CartoDB positron"
    )

    # Dibujar conexiones del grafo
    for origen, destino in grafo.edges():

        datos_origen = grafo.nodes[origen]
        datos_destino = grafo.nodes[destino]

        coordenadas = [
            [datos_origen["latitud"], datos_origen["longitud"]],
            [datos_destino["latitud"], datos_destino["longitud"]]
        ]

        folium.PolyLine(
            locations=coordenadas,
            color="gray",
            weight=2,
            opacity=0.7
        ).add_to(mapa)

    # Dibujar nodos
    for nodo, datos in grafo.nodes(data=True):

        popup = (
            f"<b>{datos.get('nombre', nodo)}</b><br>"
            f"Tipo: {datos.get('tipo', 'general')}<br>"
            f"Latitud: {datos.get('latitud', 0)}<br>"
            f"Longitud: {datos.get('longitud', 0)}"
        )

        # Información adicional para electrolineras
        if datos.get("tipo") == "electrolinera":

            popup += (
                f"<br>Capacidad: {datos.get('capacidad', 0)}"
                f"<br>Disponibilidad: {datos.get('disponibilidad', 0)}"
                f"<br>Potencia: {datos.get('potencia', 0)} kW"
            )

        # Color del nodo
        color = COLORES_NODO.get(datos.get("tipo"), "gray")

        # Crear marcador
        folium.CircleMarker(
            location=[datos["latitud"], datos["longitud"]],
            radius=7,
            popup=popup,
            color=color,
            fill=True,
            fill_opacity=0.8
        ).add_to(mapa)

    # Dibujar ruta resaltada
    if ruta:

        coordenadas_ruta = []

        for nodo in ruta:
            lat = grafo.nodes[nodo]["latitud"]
            lon = grafo.nodes[nodo]["longitud"]

            coordenadas_ruta.append([lat, lon])

        folium.PolyLine(
            locations=coordenadas_ruta,
            color="red",
            weight=5,
            opacity=0.9
        ).add_to(mapa)

    # Guardar archivo
    archivo = obtener_ruta_mapa(nombre_archivo)

    mapa.save(str(archivo))

    return archivo


# Calcular centro del mapa
def calcular_centro_mapa(grafo):

    latitudes = []
    longitudes = []

    for _, datos in grafo.nodes(data=True):

        latitudes.append(datos["latitud"])
        longitudes.append(datos["longitud"])

    promedio_lat = sum(latitudes) / len(latitudes)
    promedio_lon = sum(longitudes) / len(longitudes)

    return promedio_lat, promedio_lon
