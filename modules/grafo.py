"""
Construcción y utilidades del grafo vial
"""

import networkx as nx
# Intentar importar osmnx
try:
    import osmnx as ox
except:
    ox = None


# Construir grafo
def construir_grafo(datos):

    grafo = nx.Graph()

    # Agregar nodos
    for nodo in datos.get("nodos", []):
        grafo.add_node(
            nodo["id"],
            nombre=nodo["nombre"],
            tipo=nodo["tipo"],
            categoria=nodo.get(
                "categoria",
                nodo["tipo"]
            ),
            latitud=nodo["latitud"],
            longitud=nodo["longitud"],
            capacidad=nodo.get(
                "capacidad",
                0
            ),
            disponibilidad=nodo.get(
                "disponibilidad",
                0
            ),
            potencia=nodo.get(
                "potencia",
                0
            )
        )

    # Obtener ids válidos
    nodos_validos = list(grafo.nodes())

    # Agregar aristas
    aristas = datos.get("configuracion",{}).get("aristas",[])

    for arista in aristas:
        origen = arista["origen"]
        destino = arista["destino"]

        # Validar nodos
        if (origen not in nodos_validos or destino not in nodos_validos):
            continue

        grafo.add_edge(
            origen,
            destino,
            distancia_km=float(
                arista["distancia_km"]
            ),
            tiempo_min=float(
                arista["tiempo_min"]
            ),
            consumo_kwh=float(
                arista["consumo_kwh"]
            )
        )

    return grafo


# Cargar grafo desde OpenStreetMap
def cargar_grafo_osm(configuracion):

    if ox is None:
        raise ImportError("OSMnx no está instalado")

    osm = configuracion.get("osm", {})

    lugar = osm.get("lugar")
    tipo_red = osm.get("tipo_red", "drive")

    if not lugar:
        raise ValueError("No se encontró el lugar")

    grafo = ox.graph_from_place(lugar, network_type=tipo_red)
    return grafo


# Simular tráfico
def simular_trafico(grafo,factor_trafico):

    copia = grafo.copy()

    for origen, destino, datos in copia.edges(data=True):

        tiempo = datos.get("tiempo_min", 0)

        nuevo_tiempo = (tiempo * factor_trafico)

        copia[origen][destino]["tiempo_min"] = round(nuevo_tiempo,2)

    return copia


# Obtener nodos por tipo
def obtener_nodos_por_tipo(grafo,tipo):

    lista = []

    for nodo, datos in grafo.nodes(data=True):

        if datos.get("tipo") == tipo:
            lista.append(nodo)

    return lista


# Obtener catálogo de nodos
def obtener_catalogo_nodos(grafo):

    catalogo = []

    for nodo, datos in grafo.nodes(data=True):

        catalogo.append(
            {
                "id": nodo,
                "nombre": datos.get(
                    "nombre",
                    nodo
                ),
                "tipo": datos.get(
                    "tipo",
                    "general"
                )
            }
        )

    # Ordenar por nombre
    catalogo.sort(key=lambda x: x["nombre"])

    return catalogo


# Obtener resumen del grafo
def obtener_resumen_grafo(grafo):

    total_distancia = 0
    total_tiempo = 0

    # Recorrer aristas
    for _, _, datos in grafo.edges(data=True):

        total_distancia += datos.get("distancia_km", 0)

        total_tiempo += datos.get("tiempo_min", 0)

    resumen = {
        "nodos":
            grafo.number_of_nodes(),

        "aristas":
            grafo.number_of_edges(),

        "electrolineras":
            len(
                obtener_nodos_por_tipo(grafo,"electrolinera")
            ),

        "puntos_fijos":
            len(
                obtener_nodos_por_tipo(grafo, "punto_fijo"
                )
            ),

        "distancia_total_km":
            round(total_distancia, 2),

        "tiempo_total_min":
            round(total_tiempo, 2),

        "grafo_conectado":
            nx.is_connected(grafo)
            if grafo.number_of_nodes() > 0
            else False
    }

    return resumen
