"""
Algoritmos de rutas y simulacion de bateria.
"""

import time
import networkx as nx


def calcular_ruta_dijkstra(grafo, origen, destino, peso):

    validar_nodos(grafo, origen, destino)

    ruta = nx.shortest_path(grafo, origen, destino, weight=peso, method="dijkstra")

    metricas = calcular_metricas_ruta(grafo, ruta)

    return {
        "ruta": ruta,
        "distancia_km": metricas["distancia_km"],
        "tiempo_min": metricas["tiempo_min"],
        "consumo_kwh": metricas["consumo_kwh"]
    }


def calcular_ruta_floyd_warshall(grafo, origen, destino, peso):

    validar_nodos(grafo, origen, destino)

    predecesores, distancias = nx.floyd_warshall_predecessor_and_distance(grafo, weight=peso)

    ruta = []

    if origen == destino:
        ruta = [origen]
    elif destino not in predecesores.get(origen, {}):
        raise nx.NetworkXNoPath(
            f"No existe ruta entre {origen} y {destino}"
        )
    else:
        actual = destino
        ruta.append(actual)

        while actual != origen:
            actual = predecesores[origen][actual]
            ruta.append(actual)

        ruta.reverse()

    metricas = calcular_metricas_ruta(grafo, ruta)

    return {
        "ruta": ruta,
        "distancia_km": metricas["distancia_km"],
        "tiempo_min": metricas["tiempo_min"],
        "consumo_kwh": metricas["consumo_kwh"],
        "distancia_floyd": float(distancias[origen][destino])
    }


def resolver_ruta(grafo, origen, destino, algoritmo, peso):

    if algoritmo == "dijkstra":
        resultado = calcular_ruta_dijkstra(grafo, origen, destino, peso)
    elif algoritmo == "floyd_warshall":
        resultado = calcular_ruta_floyd_warshall(grafo, origen, destino, peso)
    else:
        raise ValueError("Algoritmo no soportado")

    resultado["algoritmo"] = algoritmo
    resultado["peso"] = peso

    return resultado


def calcular_metricas_ruta(grafo, ruta, vehiculo=None):

    if len(ruta) < 2:
        return {
            "distancia_km": 0,
            "tiempo_min": 0,
            "consumo_kwh": 0
        }

    distancia = 0
    tiempo = 0
    consumo = 0

    for i in range(len(ruta) - 1):
        origen = ruta[i]
        destino = ruta[i + 1]
        arista = grafo[origen][destino]

        distancia += float(arista.get("distancia_km", 0))
        tiempo += float(arista.get("tiempo_min", 0))
        consumo += calcular_consumo_tramo(arista, vehiculo)

    return {
        "distancia_km": round(distancia, 2),
        "tiempo_min": round(tiempo, 2),
        "consumo_kwh": round(consumo, 2)
    }


def buscar_electrolinera_cercana(grafo, origen, peso="distancia_km", solo_disponibles=False):
    mejor_estacion = None
    mejor_valor = None

    for nodo, datos in grafo.nodes(data=True):
        if datos.get("tipo") != "electrolinera":
            continue

        if solo_disponibles and int(datos.get("disponibilidad", 0)) <= 0:
            continue

        try:
            resultado = calcular_ruta_dijkstra(grafo, origen, nodo, peso)
            valor = resultado[peso]

            if mejor_valor is None or valor < mejor_valor:
                mejor_valor = valor
                mejor_estacion = {
                    "estacion_id": nodo,
                    "estacion_nombre": datos.get("nombre", nodo),
                    "ruta": resultado["ruta"],
                    "distancia_km": resultado["distancia_km"],
                    "tiempo_min": resultado["tiempo_min"],
                    "consumo_kwh": resultado["consumo_kwh"]
                }

        except nx.NetworkXNoPath:
            continue

    return mejor_estacion


def simular_recorrido(grafo, origen, destino, vehiculo, algoritmo, peso, bateria_inicial_pct=100, bateria_minima_pct=20, recarga_objetivo_pct=95, umbral_alerta_min_pct=10, umbral_alerta_max_pct=20):

    validar_nodos(grafo, origen, destino)

    capacidad = float(vehiculo["capacidad_bateria_kwh"])
    bateria_inicial_pct = normalizar_porcentaje(bateria_inicial_pct)
    bateria_minima_pct = normalizar_porcentaje(bateria_minima_pct)
    umbral_alerta_min_pct = normalizar_porcentaje(umbral_alerta_min_pct)
    umbral_alerta_max_pct = normalizar_porcentaje(umbral_alerta_max_pct)

    bateria_actual = capacidad * (bateria_inicial_pct / 100)
    destino_alcanzado = True
    simulacion_interrumpida = False
    motivo_interrupcion = ""

    resultado = resolver_ruta(grafo, origen, destino, algoritmo, peso)
    ruta_planificada = resultado["ruta"]
    ruta_recorrida = [ruta_planificada[0]] if ruta_planificada else []

    pasos = []
    recargas = []
    alertas_bateria = []
    advertencias = []
    electrolineras_utilizadas = []
    electrolineras_sugeridas = []

    for i in range(len(ruta_planificada) - 1):
        nodo_actual = ruta_planificada[i]
        siguiente = ruta_planificada[i + 1]
        arista = grafo[nodo_actual][siguiente]
        consumo = calcular_consumo_tramo(arista, vehiculo)

        bateria_antes_tramo = bateria_actual
        bateria_actual -= consumo
        bateria_restante_pct = porcentaje_bateria(bateria_actual, capacidad)
        ruta_recorrida.append(siguiente)

        pasos.append({
            "origen": nodo_actual,
            "destino": siguiente,
            "distancia_km": arista.get("distancia_km", 0),
            "tiempo_min": arista.get("tiempo_min", 0),
            "consumo_kwh": round(consumo, 2),
            "bateria_antes_kwh": round(bateria_antes_tramo, 2),
            "bateria_restante": round(bateria_actual, 2),
            "bateria_restante_pct": round(bateria_restante_pct, 2)
        })

        if bateria_restante_pct <= umbral_alerta_max_pct:
            estacion = _seleccionar_estacion_recarga(grafo, siguiente, peso)

            if estacion is None:
                advertencias.append(
                    f"No se encontro una electrolinera accesible desde {siguiente}."
                )
                simulacion_interrumpida = True
                destino_alcanzado = False
                motivo_interrupcion = (
                    f"Bateria baja en {siguiente} recorrido y no hay una electrolinera accesible."
                )
                break
            else:
                nivel_alerta = "critica"
                if bateria_restante_pct >= umbral_alerta_min_pct:
                    nivel_alerta = "preventiva"

                alerta = {
                    "nodo": siguiente,
                    "bateria_pct": round(bateria_restante_pct, 2),
                    "nivel": nivel_alerta,
                    "estacion_id": estacion["estacion_id"],
                    "estacion_nombre": estacion["estacion_nombre"],
                    "ruta_estacion": estacion["ruta"],
                    "distancia_estacion_km": estacion["distancia_km"],
                    "tiempo_estacion_min": estacion["tiempo_min"]
                }
                alertas_bateria.append(alerta)
                electrolineras_sugeridas.append({
                    "desde": siguiente,
                    "estacion_id": estacion["estacion_id"],
                    "estacion_nombre": estacion["estacion_nombre"],
                    "ruta_estacion": estacion["ruta"],
                    "distancia_estacion_km": estacion["distancia_km"],
                    "tiempo_estacion_min": estacion["tiempo_min"]
                })
                simulacion_interrumpida = True
                destino_alcanzado = (siguiente == destino)
                motivo_interrupcion = (
                    f"Bateria baja en {siguiente} recorrido. Se recomienda dirigirse a "
                    f"{estacion['estacion_nombre']}."
                )
                break

        if bateria_actual < 0:
            advertencias.append(
                f"La bateria no alcanza para completar el tramo {nodo_actual} -> {siguiente}."
            )
            simulacion_interrumpida = True
            destino_alcanzado = False
            motivo_interrupcion = (
                f"La bateria se agoto antes de completar el recorrido hacia {destino}."
            )
            break

    metricas = calcular_metricas_ruta(grafo, ruta_recorrida, vehiculo)
    bateria_final = porcentaje_bateria(bateria_actual, capacidad)

    return {
        "ruta_final": ruta_recorrida,
        "ruta_planificada": ruta_planificada,
        "distancia_km": metricas["distancia_km"],
        "tiempo_min": metricas["tiempo_min"],
        "consumo_kwh": metricas["consumo_kwh"],
        "bateria_final_pct": round(bateria_final, 2),
        "pasos": pasos,
        "recargas": recargas,
        "alertas_bateria": alertas_bateria,
        "advertencias": advertencias,
        "electrolineras_utilizadas": electrolineras_utilizadas,
        "electrolineras_sugeridas": electrolineras_sugeridas,
        "simulacion_interrumpida": simulacion_interrumpida,
        "motivo_interrupcion": motivo_interrupcion,
        "destino_alcanzado": destino_alcanzado,
        "algoritmo": algoritmo,
        "peso": peso,
        "bateria_minima_pct": bateria_minima_pct,
        "recarga_objetivo_pct": recarga_objetivo_pct
    }


def simular_varios_recorridos(grafo, origen, destino, vehiculo, algoritmo, peso, cantidad_recorridos=1, bateria_inicial_pct=100, bateria_minima_pct=20, recarga_objetivo_pct=95, umbral_alerta_min_pct=10, umbral_alerta_max_pct=20):

    cantidad_recorridos = max(1, int(cantidad_recorridos))
    bateria_actual_pct = normalizar_porcentaje(bateria_inicial_pct)

    simulaciones = []
    recargas = []
    alertas_bateria = []
    electrolineras_utilizadas = []
    electrolineras_sugeridas = []
    simulacion_interrumpida = False
    motivo_interrupcion = ""

    for numero_recorrido in range(1, cantidad_recorridos + 1):
        simulacion = simular_recorrido(grafo,origen,destino,vehiculo,algoritmo,peso,bateria_inicial_pct=bateria_actual_pct,bateria_minima_pct=bateria_minima_pct,recarga_objetivo_pct=recarga_objetivo_pct,umbral_alerta_min_pct=umbral_alerta_min_pct,umbral_alerta_max_pct=umbral_alerta_max_pct)

        simulacion["numero_recorrido"] = numero_recorrido
        simulacion["bateria_inicial_recorrido_pct"] = round(bateria_actual_pct, 2)
        simulaciones.append(simulacion)
        bateria_actual_pct = simulacion.get("bateria_final_pct", bateria_actual_pct)

        for recarga in simulacion.get("recargas", []):
            recarga_consecutiva = recarga.copy()
            recarga_consecutiva["numero_recorrido"] = numero_recorrido
            recargas.append(recarga_consecutiva)

        for alerta in simulacion.get("alertas_bateria", []):
            alerta_consecutiva = alerta.copy()
            alerta_consecutiva["numero_recorrido"] = numero_recorrido
            alertas_bateria.append(alerta_consecutiva)

        for estacion in simulacion.get("electrolineras_utilizadas", []):
            estacion_consecutiva = estacion.copy()
            estacion_consecutiva["numero_recorrido"] = numero_recorrido
            electrolineras_utilizadas.append(estacion_consecutiva)

        for sugerencia in simulacion.get("electrolineras_sugeridas", []):
            sugerencia_consecutiva = sugerencia.copy()
            sugerencia_consecutiva["numero_recorrido"] = numero_recorrido
            electrolineras_sugeridas.append(sugerencia_consecutiva)

        if simulacion.get("simulacion_interrumpida"):
            simulacion_interrumpida = True
            motivo_interrupcion = simulacion.get("motivo_interrupcion", "")
            break

    ultimo = simulaciones[-1]
    bateria_promedio = sum(
        item.get("bateria_final_pct", 0)
        for item in simulaciones
    ) / len(simulaciones)

    return {
        "tipo": "lote" if cantidad_recorridos > 1 else "individual",
        "cantidad_recorridos": len(simulaciones),
        "cantidad_recorridos_solicitados": cantidad_recorridos,
        "bateria_inicial_lote_pct": normalizar_porcentaje(bateria_inicial_pct),
        "ruta_final": ultimo.get("ruta_final", []),
        "distancia_km": round(sum(item.get("distancia_km", 0) for item in simulaciones), 2),
        "tiempo_min": round(sum(item.get("tiempo_min", 0) for item in simulaciones), 2),
        "consumo_kwh": round(sum(item.get("consumo_kwh", 0) for item in simulaciones), 2),
        "bateria_final_pct": round(ultimo.get("bateria_final_pct", 0), 2),
        "bateria_promedio_final_pct": round(bateria_promedio, 2),
        "bateria_final_ultimo_pct": ultimo.get("bateria_final_pct", 0),
        "recargas": recargas,
        "alertas_bateria": alertas_bateria,
        "electrolineras_utilizadas": electrolineras_utilizadas,
        "electrolineras_sugeridas": electrolineras_sugeridas,
        "simulaciones": simulaciones,
        "simulacion_interrumpida": simulacion_interrumpida,
        "motivo_interrupcion": motivo_interrupcion,
        "destino_alcanzado": ultimo.get("destino_alcanzado", False),
        "algoritmo": algoritmo,
        "peso": peso
    }


def comparar_algoritmos(grafo, origen, destino, pesos=None):

    if pesos is None:
        pesos = [
            "distancia_km",
            "tiempo_min",
            "consumo_kwh"
        ]

    resultados = []
    algoritmos = [
        "dijkstra",
        "floyd_warshall"
    ]

    for algoritmo in algoritmos:
        for peso in pesos:
            inicio = time.perf_counter()
            resultado = resolver_ruta(grafo, origen, destino, algoritmo, peso)
            fin = time.perf_counter()

            resultado["tiempo_ejecucion_ms"] = round((fin - inicio) * 1000, 3)
            resultados.append(resultado)

    return resultados


def validar_nodos(grafo, origen, destino):

    if origen not in grafo:
        raise ValueError(
            f"El nodo origen {origen} no existe"
        )

    if destino not in grafo:
        raise ValueError(
            f"El nodo destino {destino} no existe"
        )


def normalizar_porcentaje(valor):

    if valor < 0:
        return 0.0

    if valor > 100:
        return 100.0

    return float(valor)


def porcentaje_bateria(bateria_actual, capacidad):

    if capacidad <= 0:
        return 0.0

    return (bateria_actual / capacidad) * 100


def _seleccionar_estacion_recarga(grafo, origen, peso):

    estacion = buscar_electrolinera_cercana(grafo,origen,peso=peso,solo_disponibles=True)

    if estacion is not None:
        return estacion

    return buscar_electrolinera_cercana(grafo,origen,peso=peso)


def calcular_consumo_tramo(arista, vehiculo=None):

    if vehiculo is None:
        return float(
            arista.get("consumo_kwh", 0)
        )

    distancia = float(arista.get("distancia_km", 0))
    consumo_vehiculo = float(vehiculo.get("consumo_kwh_km", 0.18))

    return round(distancia * consumo_vehiculo, 4)
