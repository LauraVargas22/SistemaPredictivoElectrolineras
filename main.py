"""Aplicacion de consola para analisis vial y electrolineras."""

from __future__ import annotations

from typing import Any

from modules.customs import borrar_pantalla, pausar
import modules.estadisticas as est
import modules.grafo as gr
import modules.inicializarData as ini
import modules.infraestructura as inf
import modules.mensajes as msg
import modules.menus as me
from modules.modelos_ml import cargar_metricas_modelos, entrenar_modelos, predecir_escenario
from modules.reportes import exportar_reporte_json
from modules.rutas import (
    buscar_electrolinera_cercana,
    comparar_algoritmos,
    resolver_ruta,
    simular_varios_recorridos,
)
from modules.salir import confirmar_salida
from modules.titles import renderizar_titulo
from modules.visualizacion import exportar_visualizaciones


def cargar_estado() -> dict[str, Any]:
    datos = ini.cargar_datos_proyecto()
    grafo = gr.construir_grafo(datos)
    resultados_previos = ini.cargar_resultados()
    metricas_modelos = cargar_metricas_modelos() or resultados_previos.get("metricas_ml", [])

    return {
        "datos": datos,
        "grafo": grafo,
        "ultima_ruta": resultados_previos.get("ultima_ruta"),
        "ultima_simulacion": resultados_previos.get("ultima_simulacion"),
        "ultima_comparacion": resultados_previos.get("comparacion_algoritmos", []),
        "metricas_ml": metricas_modelos,
        "historico_simulaciones": _normalizar_historico_simulaciones(
            resultados_previos.get("simulaciones", [])
        ),
        "historico_comparaciones": resultados_previos.get("comparaciones", []),
    }


def recargar_estado(estado: dict[str, Any]) -> None:
    nuevo_estado = cargar_estado()
    estado.update(nuevo_estado)


def seleccionar_nodo(estado: dict[str, Any], titulo: str) -> dict[str, Any]:
    catalogo = gr.obtener_catalogo_nodos(estado["grafo"])
    return me.seleccionar_item(titulo, catalogo)


def seleccionar_vehiculo(estado: dict[str, Any]) -> dict[str, Any]:
    return me.seleccionar_item("Seleccione el vehiculo", estado["datos"]["configuracion"]["vehiculos"])


def opcion_cargar_datos(estado: dict[str, Any]) -> None:
    recargar_estado(estado)
    me.informar("Datos cargados correctamente desde los archivos JSON.")
    me.mostrar_resumen_grafo(gr.obtener_resumen_grafo(estado["grafo"]))
    me.mostrar_nodos(estado["datos"]["electrolineras"], "Electrolineras registradas")
    me.mostrar_nodos(estado["datos"]["puntos_fijos"], "Puntos fijos registrados")


def opcion_gestionar_infraestructura(estado: dict[str, Any]) -> None:
    is_active = True
    while is_active:
        opcion = me.mostrar_menu_gestion()
        match opcion:
            case 1:
                electrolinera = me.seleccionar_item(
                    "Seleccione la electrolinera a actualizar",
                    estado["datos"]["electrolineras"]
                )
                disponibilidad = int(me.solicitar_numero("Nueva disponibilidad", minimo=0))
                actualizada = inf.actualizar_disponibilidad_estacion(electrolinera["id"], disponibilidad)
                me.informar(f"Disponibilidad actualizada para {actualizada['nombre']}.")
                recargar_estado(estado)
            case 2:
                nueva = {
                    "id": me.solicitar_texto("ID de la electrolinera").lower().replace(" ", "_"),
                    "nombre": me.solicitar_texto("Nombre de la electrolinera"),
                    "latitud": me.solicitar_numero("Latitud"),
                    "longitud": me.solicitar_numero("Longitud"),
                    "capacidad": int(me.solicitar_numero("Capacidad de puestos", minimo=1)),
                    "disponibilidad": int(me.solicitar_numero("Disponibilidad actual", minimo=0)),
                    "potencia": int(me.solicitar_numero("Potencia (kW)", minimo=1)),
                }
                inf.agregar_electrolinera_con_conexiones(nueva)
                me.informar("Electrolinera agregada con conexiones sinteticas automaticas.")
                recargar_estado(estado)
            case 3:
                electrolinera = me.seleccionar_item(
                    "Electrolinera a eliminar",
                    estado["datos"]["electrolineras"]
                )
                if me.solicitar_confirmacion(f"Confirma eliminar {electrolinera['nombre']}"):
                    inf.eliminar_electrolinera_con_conexiones(electrolinera["id"])
                    me.informar("Electrolinera eliminada correctamente.")
                    recargar_estado(estado)
            case 4:
                nuevo_punto = {
                    "id": me.solicitar_texto("ID del punto fijo").lower().replace(" ", "_"),
                    "nombre": me.solicitar_texto("Nombre del punto fijo"),
                    "coordenadas": {
                        "latitud": me.solicitar_numero("Latitud"),
                        "longitud": me.solicitar_numero("Longitud"),
                    },
                    "tipo": me.solicitar_texto("Tipo del punto fijo"),
                }
                inf.agregar_punto_fijo_con_conexiones(nuevo_punto)
                me.informar("Punto fijo agregado y conectado automaticamente.")
                recargar_estado(estado)
            case 5:
                punto = me.seleccionar_item("Punto fijo a actualizar", estado["datos"]["puntos_fijos"])
                cambios = {
                    "nombre": me.solicitar_texto("Nuevo nombre"),
                    "coordenadas": {
                        "latitud": me.solicitar_numero("Nueva latitud"),
                        "longitud": me.solicitar_numero("Nueva longitud"),
                    },
                    "tipo": me.solicitar_texto("Nuevo tipo"),
                }
                inf.actualizar_punto_fijo_con_conexiones(punto["id"], cambios)
                me.informar("Punto fijo actualizado con nuevas conexiones sinteticas.")
                recargar_estado(estado)
            case 6:
                punto = me.seleccionar_item("Punto fijo a eliminar", estado["datos"]["puntos_fijos"])
                if me.solicitar_confirmacion(f"Confirma eliminar {punto['nombre']}"):
                    inf.eliminar_punto_fijo_con_conexiones(punto["id"])
                    me.informar("Punto fijo eliminado correctamente.")
                    recargar_estado(estado)
            case 7:
                is_active = False
            case _:
                print(msg.msgCase)
                pausar()

        pausar()
        borrar_pantalla()


def opcion_calcular_ruta(estado: dict[str, Any]) -> None:
    origen = seleccionar_nodo(estado, "Seleccione el origen")
    destino = seleccionar_nodo(estado, "Seleccione el destino")

    if origen["id"] == destino["id"]:
        print("El origen y el destino no pueden ser iguales. Intente nuevamente.")
        return

    algoritmo = me.seleccionar_algoritmo()
    peso = me.seleccionar_peso()
    trafico = me.seleccionar_trafico()
    factor = estado["datos"]["configuracion"]["simulacion_trafico"][trafico]
    grafo_ajustado = gr.simular_trafico(estado["grafo"], factor)

    resultado = resolver_ruta(grafo_ajustado, origen["id"], destino["id"], algoritmo, peso)
    estado["ultima_ruta"] = resultado
    guardar_estado_resultados(estado)
    me.mostrar_resultado_ruta(resultado)


def opcion_simular_recorrido(estado: dict[str, Any]) -> None:
    origen = seleccionar_nodo(estado, "Seleccione el origen del recorrido")
    destino = seleccionar_nodo(estado, "Seleccione el destino del recorrido")

    if origen["id"] == destino["id"]:
        print("El origen y el destino no pueden ser iguales. Intente nuevamente.")
        return

    vehiculo = seleccionar_vehiculo(estado)
    algoritmo = me.seleccionar_algoritmo()
    peso = me.seleccionar_peso()
    trafico = me.seleccionar_trafico()
    cantidad_recorridos = int(me.solicitar_numero("Cantidad de recorridos", minimo=1, maximo=100))
    bateria_inicial = me.solicitar_numero("Bateria inicial (%)", minimo=10, maximo=100)

    factor = estado["datos"]["configuracion"]["simulacion_trafico"][trafico]
    grafo_ajustado = gr.simular_trafico(estado["grafo"], factor)
    simulacion = simular_varios_recorridos(
        grafo_ajustado,
        origen["id"],
        destino["id"],
        vehiculo,
        algoritmo,
        peso,
        cantidad_recorridos=cantidad_recorridos,
        bateria_inicial_pct=bateria_inicial,
        bateria_minima_pct=float(estado["datos"]["configuracion"]["bateria_minima_pct"]),
        recarga_objetivo_pct=float(estado["datos"]["configuracion"]["recarga_objetivo_pct"]),
    )

    simulacion["origen_id"] = origen["id"]
    simulacion["destino_id"] = destino["id"]
    simulacion["vehiculo"] = vehiculo["nombre"]
    simulacion["trafico"] = trafico

    for recorrido in simulacion.get("simulaciones", []):
        recorrido["origen_id"] = origen["id"]
        recorrido["destino_id"] = destino["id"]
        recorrido["vehiculo"] = vehiculo["nombre"]
        recorrido["trafico"] = trafico

    estado["ultima_simulacion"] = simulacion
    estado["historico_simulaciones"].extend(simulacion.get("simulaciones", []))
    guardar_estado_resultados(estado)
    me.mostrar_simulacion(simulacion)


def opcion_estadisticas_electrolineras(estado: dict[str, Any]) -> None:
    estadisticas = est.calcular_estadisticas_electrolineras(
        estado["grafo"],
        estado["historico_simulaciones"]
    )
    me.mostrar_estadisticas_electrolineras(estadisticas)


def opcion_entrenar_ml(estado: dict[str, Any]) -> None:
    resumen = entrenar_modelos(estado["grafo"], estado["datos"]["configuracion"])
    estado["metricas_ml"] = resumen["metricas"]
    guardar_estado_resultados(estado)
    me.mostrar_metricas_ml(resumen["metricas"])
    me.informar("Modelos entrenados y guardados en la carpeta models.")


def opcion_ver_metricas_ml(estado: dict[str, Any]) -> None:
    if not estado["metricas_ml"]:
        me.advertir("Aun no hay metricas guardadas. Primero entrene los modelos.")
        return

    me.mostrar_metricas_ml(estado["metricas_ml"])


def opcion_probar_prediccion_ml(estado: dict[str, Any]) -> None:
    if not estado["metricas_ml"]:
        me.advertir("Aun no hay modelos entrenados. Primero use la opcion de entrenar.")
        return

    origen = seleccionar_nodo(estado, "Seleccione el origen para la prediccion")
    destino = seleccionar_nodo(estado, "Seleccione el destino para la prediccion")

    if origen["id"] == destino["id"]:
        me.advertir("El origen y el destino no pueden ser iguales.")
        return

    vehiculo = seleccionar_vehiculo(estado)
    trafico = me.seleccionar_trafico()
    bateria_inicial = me.solicitar_numero("Bateria inicial (%)", minimo=10, maximo=100)

    factor = estado["datos"]["configuracion"]["simulacion_trafico"][trafico]
    grafo_ajustado = gr.simular_trafico(estado["grafo"], factor)
    ruta = resolver_ruta(grafo_ajustado, origen["id"], destino["id"], "dijkstra", "distancia_km")
    me.mostrar_resultado_ruta(ruta)

    predicciones = predecir_escenario(
        {
            "bateria_inicial_pct": bateria_inicial,
            "distancia_ruta_km": ruta["distancia_km"],
            "tiempo_ruta_min": ruta["tiempo_min"],
            "consumo_ruta_kwh": ruta["consumo_kwh"],
        }
    )

    resumen_ia = {
        "vehiculo": vehiculo["nombre"],
        "trafico": trafico,
        "bateria_inicial_pct": round(bateria_inicial, 2),
        "consumo_estimado_ia_kwh": predicciones.get("consumo_estimado_kwh", "N/A"),
        "requiere_recarga_ia": "Si" if predicciones.get("requiere_recarga", 0) == 1 else "No",
    }

    if predicciones.get("requiere_recarga", 0) == 1:
        estacion = buscar_electrolinera_cercana(grafo_ajustado, origen["id"])
        if estacion:
            resumen_ia["electrolinera_sugerida"] = estacion["estacion_nombre"]

    me.mostrar_resumen_grafo(resumen_ia)


def opcion_menu_ml(estado: dict[str, Any]) -> None:
    is_active = True

    while is_active:
        opcion = me.mostrar_menu_ml()
        borrar_pantalla()

        match opcion:
            case 1:
                opcion_entrenar_ml(estado)
            case 2:
                opcion_ver_metricas_ml(estado)
            case 3:
                opcion_probar_prediccion_ml(estado)
            case 4:
                is_active = False
                continue
            case _:
                me.advertir("Opcion no valida")

        pausar()
        borrar_pantalla()


def opcion_generar_mapas_reportes(estado: dict[str, Any]) -> None:
    ruta_visual = None
    if estado["ultima_simulacion"]:
        ruta_visual = estado["ultima_simulacion"]["ruta_final"]
    elif estado["ultima_ruta"]:
        ruta_visual = estado["ultima_ruta"]["ruta"]

    archivos = exportar_visualizaciones(estado["grafo"], ruta_visual, "analisis_actual")
    comparacion = estado.get("ultima_comparacion", [])
    reporte_json = exportar_reporte_json(
        "resultados.json",
        {
            "ultima_ruta": estado["ultima_ruta"],
            "ultima_simulacion": estado["ultima_simulacion"],
            "metricas_ml": estado["metricas_ml"],
            "comparacion_algoritmos": comparacion,
            "simulaciones": estado["historico_simulaciones"],
            "comparaciones": estado["historico_comparaciones"],
        },
    )
    archivos["reporte_json"] = str(reporte_json)

    me.mostrar_archivos_generados(archivos)
    me.informar("Mapas, imagenes y reportes generados correctamente.")


def opcion_comparar_algoritmos_vs_ia(estado: dict[str, Any]) -> None:
    origen = seleccionar_nodo(estado, "Origen para la comparacion")
    destino = seleccionar_nodo(estado, "Destino para la comparacion")
    trafico = me.seleccionar_trafico()
    factor = estado["datos"]["configuracion"]["simulacion_trafico"][trafico]
    grafo_ajustado = gr.simular_trafico(estado["grafo"], factor)

    comparacion = comparar_algoritmos(grafo_ajustado, origen["id"], destino["id"])
    estado["ultima_comparacion"] = comparacion
    estado["historico_comparaciones"].append(
        {
            "origen_id": origen["id"],
            "destino_id": destino["id"],
            "trafico": trafico,
            "resultados": comparacion,
        }
    )
    guardar_estado_resultados(estado)
    me.mostrar_comparacion_algoritmos(comparacion)

    if estado["metricas_ml"]:
        vehiculo = estado["datos"]["configuracion"]["vehiculos"][0]
        ruta_referencia = resolver_ruta(grafo_ajustado, origen["id"], destino["id"], "dijkstra", "distancia_km")
        estacion = buscar_electrolinera_cercana(grafo_ajustado, origen["id"]) or {
            "estacion_id": "sin_estacion",
            "distancia_km": 0.0,
        }
        datos_estacion = estado["grafo"].nodes.get(estacion["estacion_id"], {})
        escenario = {
            "origen": origen["id"],
            "destino": destino["id"],
            "vehiculo": vehiculo["nombre"],
            "trafico": trafico,
            "peso_referencia": "distancia_km",
            "bateria_inicial_pct": 80.0,
            "distancia_ruta_km": ruta_referencia["distancia_km"],
            "tiempo_ruta_min": ruta_referencia["tiempo_min"],
            "consumo_ruta_kwh": ruta_referencia["consumo_kwh"],
            "trafico_factor": float(factor),
            "disponibilidad_promedio": _ratio_disponibilidad(datos_estacion),
            "capacidad_estacion_objetivo": int(datos_estacion.get("capacidad", 0)),
            "potencia_estacion_objetivo": float(datos_estacion.get("potencia", 0)),
            "distancia_estacion_objetivo_km": float(estacion.get("distancia_km", 0.0)),
            "demanda_estimada": 3.0,
        }
        predicciones = predecir_escenario(escenario)
        if predicciones:
            me.mostrar_resumen_grafo({f"IA {clave}": valor for clave, valor in predicciones.items()})
    else:
        me.advertir("Aun no hay modelos entrenados. Entrene la opcion de ML para comparar con IA.")


def _ratio_disponibilidad(datos_estacion: dict[str, Any]) -> float:
    capacidad = float(datos_estacion.get("capacidad", 0))
    if capacidad <= 0:
        return 0.0
    return round(float(datos_estacion.get("disponibilidad", 0)) / capacidad, 4)


def _normalizar_historico_simulaciones(simulaciones: list[Any]) -> list[dict[str, Any]]:
    simulaciones_planas: list[dict[str, Any]] = []
    for simulacion in simulaciones or []:
        if isinstance(simulacion, dict) and simulacion.get("simulaciones"):
            simulaciones_planas.extend(simulacion["simulaciones"])
        elif isinstance(simulacion, dict):
            simulaciones_planas.append(simulacion)
    return simulaciones_planas


def guardar_estado_resultados(estado: dict[str, Any]) -> None:
    ini.guardar_resultados(
        {
            "ultima_ruta": estado["ultima_ruta"],
            "ultima_simulacion": estado["ultima_simulacion"],
            "metricas_ml": estado["metricas_ml"],
            "comparacion_algoritmos": estado["ultima_comparacion"],
            "simulaciones": estado["historico_simulaciones"],
            "comparaciones": estado["historico_comparaciones"],
        }
    )


def main() -> None:
    ini.inicializar_archivos_base()
    estado = cargar_estado()

    is_active = True
    while is_active:
        borrar_pantalla()
        renderizar_titulo(me.console)
        opcion = me.mostrar_menu_principal()
        borrar_pantalla()

        try:
            match opcion:
                case 1:
                    opcion_cargar_datos(estado)
                case 2:
                    opcion_gestionar_infraestructura(estado)
                case 3:
                    opcion_calcular_ruta(estado)
                case 4:
                    opcion_simular_recorrido(estado)
                case 5:
                    opcion_estadisticas_electrolineras(estado)
                case 6:
                    opcion_menu_ml(estado)
                case 7:
                    opcion_generar_mapas_reportes(estado)
                case 8:
                    opcion_comparar_algoritmos_vs_ia(estado)
                case 9:
                    salir = confirmar_salida("Desea salir del sistema? (S/N): ")
                    if salir:
                        guardar_estado_resultados(estado)
                        me.informar("Sesion guardada. Hasta pronto.")
                        is_active = False
                case _:
                    me.advertir("Opcion no valida")
                    break
        except Exception as exc:  # pragma: no cover - control defensivo de consola
            me.error(f"Ocurrio un error: {exc}")

        pausar()


if __name__ == "__main__":
    main()
