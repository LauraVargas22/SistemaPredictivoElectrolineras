"""Interfaz de consola basada en Rich."""

from __future__ import annotations
from typing import Any, Iterable
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
import modules.mensajes as mensajes
console = Console()

def informar(texto: str) -> None:
    console.print(f"[bold green]{texto}[/bold green]")


def advertir(texto: str) -> None:
    console.print(f"[bold yellow]{texto}[/bold yellow]")


def error(texto: str) -> None:
    console.print(f"[bold red]{texto}[/bold red]")


def mostrar_menu_principal() -> int:
    return seleccionar_opcion("Menu principal", mensajes.MENU_PRINCIPAL)


def mostrar_menu_gestion() -> int:
    return seleccionar_opcion("Gestion de infraestructura", mensajes.MENU_GESTION)


def mostrar_menu_ml() -> int:
    return seleccionar_opcion("Herramientas basicas de IA", mensajes.MENU_ML)


def seleccionar_opcion(titulo: str, opciones: Iterable[str]) -> int:
    opciones = list(opciones)
    tabla = Table(title=titulo, box=box.ROUNDED, header_style="bold cyan")
    tabla.add_column("Opcion", justify="center", style="bold yellow", no_wrap=True)
    tabla.add_column("Descripcion", style="white")

    for indice, opcion in enumerate(opciones, start=1):
        tabla.add_row(str(indice), opcion)

    console.print(Panel.fit(tabla, border_style="cyan"))

    while True:
        valor = Prompt.ask("Seleccione una opcion").strip()
        if valor.isdigit():
            numero = int(valor)
            if 1 <= numero <= len(opciones):
                return numero
        error("Seleccione un numero valido del menu.")


def seleccionar_item(titulo: str, items: list[dict[str, Any]], campo: str = "nombre") -> dict[str, Any]:
    opciones = [item.get(campo, item.get("id", "Sin nombre")) for item in items]
    indice = seleccionar_opcion(titulo, opciones)
    return items[indice - 1]


def seleccionar_algoritmo() -> str:
    claves = list(mensajes.ALGORITMOS.keys())
    indice = seleccionar_opcion("Algoritmos disponibles", mensajes.ALGORITMOS.values())
    return claves[indice - 1]


def seleccionar_peso() -> str:
    claves = list(mensajes.PESOS_RUTA.keys())
    indice = seleccionar_opcion("Criterio de optimizacion", mensajes.PESOS_RUTA.values())
    return claves[indice - 1]


def seleccionar_trafico() -> str:
    claves = list(mensajes.NIVELES_TRAFICO.keys())
    indice = seleccionar_opcion("Nivel de trafico", mensajes.NIVELES_TRAFICO.values())
    return claves[indice - 1]


def solicitar_numero(mensaje: str, minimo: float | None = None, maximo: float | None = None) -> float:
    while True:
        valor = Prompt.ask(mensaje).strip().replace(",", ".")
        try:
            numero = float(valor)
        except ValueError:
            error("Ingrese un numero valido.")
            continue

        if minimo is not None and numero < minimo:
            error(f"El valor debe ser mayor o igual a {minimo}.")
            continue
        if maximo is not None and numero > maximo:
            error(f"El valor debe ser menor o igual a {maximo}.")
            continue
        return numero


def solicitar_texto(mensaje: str, permitir_vacio: bool = False) -> str:
    while True:
        valor = Prompt.ask(mensaje).strip()
        if valor or permitir_vacio:
            return valor
        error("El texto no puede estar vacio.")


def solicitar_confirmacion(mensaje: str) -> bool:
    respuesta = Prompt.ask(f"{mensaje} [s/n]", default="n").strip().lower()
    return respuesta in {"s", "si", "y", "yes"}


def mostrar_resumen_grafo(resumen: dict[str, Any]) -> None:
    tabla = Table(title="Resumen del grafo", box=box.SIMPLE_HEAVY)
    tabla.add_column("Indicador", style="bold white")
    tabla.add_column("Valor", style="cyan")
    for clave, valor in resumen.items():
        tabla.add_row(clave.replace("_", " ").title(), str(valor))
    console.print(tabla)


def mostrar_nodos(items: list[dict[str, Any]], titulo: str) -> None:
    tabla = Table(title=titulo, box=box.SIMPLE)
    tabla.add_column("ID", style="bold yellow")
    tabla.add_column("Nombre", style="white")
    tabla.add_column("Tipo", style="cyan")
    for item in items:
        tabla.add_row(item.get("id", "-"), item.get("nombre", "-"), item.get("tipo", "electrolinera"))
    console.print(tabla)


def mostrar_resultado_ruta(resultado: dict[str, Any]) -> None:
    tabla = Table(title="Resultado de ruta", box=box.ROUNDED)
    tabla.add_column("Campo", style="bold white")
    tabla.add_column("Valor", style="green")

    tabla.add_row("Ruta", " -> ".join(resultado.get("ruta", [])) or "Sin ruta")
    tabla.add_row("Distancia (km)", f"{resultado.get('distancia_km', 0):.2f}")
    tabla.add_row("Tiempo (min)", f"{resultado.get('tiempo_min', 0):.2f}")
    tabla.add_row("Consumo (kWh)", f"{resultado.get('consumo_kwh', 0):.2f}")
    tabla.add_row("Algoritmo", resultado.get("algoritmo", "-"))
    tabla.add_row("Peso", resultado.get("peso", "-"))

    console.print(tabla)


def mostrar_simulacion(simulacion: dict[str, Any]) -> None:
    tabla = Table(title="Simulacion de recorrido", box=box.ROUNDED)
    tabla.add_column("Campo", style="bold white")
    tabla.add_column("Valor", style="green")

    tabla.add_row("Cantidad de recorridos", str(simulacion.get("cantidad_recorridos", 1)))
    if "cantidad_recorridos_solicitados" in simulacion:
        tabla.add_row(
            "Recorridos solicitados",
            str(simulacion.get("cantidad_recorridos_solicitados", simulacion.get("cantidad_recorridos", 1)))
        )
    if "bateria_inicial_lote_pct" in simulacion:
        tabla.add_row("Bateria inicial lote (%)", f"{simulacion.get('bateria_inicial_lote_pct', 0):.2f}")
    tabla.add_row("Ruta final", " -> ".join(simulacion.get("ruta_final", [])) or "Sin ruta")
    tabla.add_row("Sugerencias de desvio", str(len(simulacion.get("electrolineras_sugeridas", []))))
    tabla.add_row("Alertas de bateria", str(len(simulacion.get("alertas_bateria", []))))
    tabla.add_row("Bateria final (%)", f"{simulacion.get('bateria_final_pct', 0):.2f}")
    if simulacion.get("cantidad_recorridos", 1) > 1:
        tabla.add_row(
            "Bateria promedio final (%)",
            f"{simulacion.get('bateria_promedio_final_pct', 0):.2f}"
        )
    tabla.add_row(
        "Destino alcanzado",
        "Si" if simulacion.get("destino_alcanzado", False) else "No"
    )
    tabla.add_row("Distancia total (km)", f"{simulacion.get('distancia_km', 0):.2f}")
    tabla.add_row("Tiempo total (min)", f"{simulacion.get('tiempo_min', 0):.2f}")
    tabla.add_row("Consumo total (kWh)", f"{simulacion.get('consumo_kwh', 0):.2f}")
    console.print(tabla)

    if simulacion.get("simulacion_interrumpida") and simulacion.get("motivo_interrupcion"):
        advertir(simulacion["motivo_interrupcion"])

    if simulacion.get("alertas_bateria"):
        advertir(
            "Se detectaron niveles de bateria entre 10% y 20%. Revise las electrolineras sugeridas."
        )

    if simulacion.get("alertas_bateria"):
        alertas = Table(title="Alertas de bateria", box=box.SIMPLE)
        alertas.add_column("Recorrido", style="yellow")
        alertas.add_column("Nodo", style="white")
        alertas.add_column("Bateria (%)", style="red")
        alertas.add_column("Nivel", style="magenta")
        alertas.add_column("Electrolinera sugerida", style="cyan")
        for alerta in simulacion["alertas_bateria"]:
            alertas.add_row(
                str(alerta.get("numero_recorrido", 1)),
                alerta.get("nodo", "-"),
                _format_metric(alerta.get("bateria_pct")),
                alerta.get("nivel", "-"),
                alerta.get("estacion_nombre", "-"),
            )
        console.print(alertas)

    if simulacion.get("electrolineras_sugeridas"):
        sugeridas = Table(title="Electrolineras sugeridas", box=box.SIMPLE)
        sugeridas.add_column("Recorrido", style="yellow")
        sugeridas.add_column("Nodo alerta", style="white")
        sugeridas.add_column("Estacion", style="cyan")
        sugeridas.add_column("Ruta sugerida", style="green")
        for estacion in simulacion["electrolineras_sugeridas"]:
            sugeridas.add_row(
                str(estacion.get("numero_recorrido", 1)),
                estacion.get("desde", "-"),
                estacion.get("estacion_nombre", "-"),
                " -> ".join(estacion.get("ruta_estacion", [])),
            )
        console.print(sugeridas)


def mostrar_metricas_ml(metricas: list[dict[str, Any]]) -> None:
    tabla = Table(title="Metricas de Machine Learning", box=box.ROUNDED)
    tabla.add_column("Modelo", style="bold yellow")
    tabla.add_column("Objetivo", style="white")
    tabla.add_column("Accuracy", style="green")
    tabla.add_column("MAE", style="cyan")
    tabla.add_column("RMSE", style="magenta")
    tabla.add_column("Tiempo (s)", style="white")
    tabla.add_column("Validacion", style="blue")

    for metrica in metricas:
        tabla.add_row(
            metrica.get("modelo", "-"),
            metrica.get("objetivo", "-"),
            _format_metric(metrica.get("accuracy")),
            _format_metric(metrica.get("mae")),
            _format_metric(metrica.get("rmse")),
            _format_metric(metrica.get("tiempo_entrenamiento_s")),
            _format_metric(metrica.get("validacion_promedio")),
        )

    console.print(tabla)


def mostrar_comparacion_algoritmos(comparacion: list[dict[str, Any]]) -> None:
    tabla = Table(title="Comparacion de algoritmos", box=box.ROUNDED)
    tabla.add_column("Algoritmo", style="bold yellow")
    tabla.add_column("Peso", style="white")
    tabla.add_column("Distancia", style="green")
    tabla.add_column("Tiempo", style="cyan")
    tabla.add_column("Consumo", style="magenta")
    tabla.add_column("Ejecucion (ms)", style="white")
    tabla.add_column("Ruta", style="blue")

    for fila in comparacion:
        tabla.add_row(
            fila.get("algoritmo", "-"),
            fila.get("peso", "-"),
            _format_metric(fila.get("distancia_km")),
            _format_metric(fila.get("tiempo_min")),
            _format_metric(fila.get("consumo_kwh")),
            _format_metric(fila.get("tiempo_ejecucion_ms")),
            " -> ".join(fila.get("ruta", [])),
        )

    console.print(tabla)


def mostrar_archivos_generados(archivos: dict[str, str]) -> None:
    tabla = Table(title="Archivos generados", box=box.SIMPLE)
    tabla.add_column("Tipo", style="bold white")
    tabla.add_column("Ruta", style="green")
    for clave, valor in archivos.items():
        tabla.add_row(clave, valor)
    console.print(tabla)


def mostrar_estadisticas_electrolineras(estadisticas: dict[str, Any]) -> None:
    tabla = Table(title="Estadisticas de electrolineras", box=box.ROUNDED)
    tabla.add_column("Indicador", style="bold white")
    tabla.add_column("Valor", style="green")

    tabla.add_row("Simulaciones registradas", str(estadisticas.get("total_simulaciones", 0)))
    tabla.add_row("Desvios sugeridos", str(estadisticas.get("total_recargas", 0)))
    tabla.add_row("Alertas de bateria", str(estadisticas.get("total_alertas", 0)))

    mas_usada = estadisticas.get("electrolinera_mas_usada")
    if mas_usada:
        tabla.add_row(
            "Electrolinera mas sugerida",
            f"{mas_usada.get('nombre', '-')} ({mas_usada.get('usos', 0)} usos)"
        )
    else:
        tabla.add_row("Electrolinera mas sugerida", "Aun no hay sugerencias registradas")

    console.print(tabla)

    puntos = estadisticas.get("puntos_estrategicos", [])
    if puntos:
        tabla_puntos = Table(title="Puntos estrategicos sugeridos", box=box.SIMPLE)
        tabla_puntos.add_column("Punto", style="bold yellow")
        tabla_puntos.add_column("Frecuencia", style="white")
        tabla_puntos.add_column("Centralidad", style="cyan")
        tabla_puntos.add_column("Electrolinera cercana", style="green")
        tabla_puntos.add_column("Distancia (km)", style="magenta")
        tabla_puntos.add_column("Puntaje", style="blue")

        for punto in puntos:
            tabla_puntos.add_row(
                punto.get("nombre", "-"),
                str(punto.get("frecuencia_rutas", 0)),
                _format_metric(punto.get("centralidad")),
                punto.get("electrolinera_cercana", "-"),
                _format_metric(punto.get("distancia_electrolinera_km")),
                _format_metric(punto.get("puntaje")),
            )

        console.print(tabla_puntos)


def _format_metric(valor: Any) -> str:
    if valor is None:
        return "N/A"
    if isinstance(valor, float):
        return f"{valor:.4f}"
    return str(valor)