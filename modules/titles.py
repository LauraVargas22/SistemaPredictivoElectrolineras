import pyfiglet
from rich.console import Console
from rich.panel import Panel

console = Console()

# Título principal
title1 = pyfiglet.figlet_format("PUNTOS DE CARGA", font="slant",)
subtitle = pyfiglet.figlet_format("EN ELECTROLINERAS", font="digital")

def show_title():
    console.print(Panel.fit(
        f"[bold cyan]{title1}[/bold cyan]\n[bold magenta]{subtitle}[/bold magenta]",
        border_style="bright_blue",
        title="📘 SISTEMA PREDICTIVO",
    ))

# Subtítulos
cargarDatos = pyfiglet.figlet_format("Datos", font="standard")
simulaRecorridos = pyfiglet.figlet_format("Recorridos", font="small")
calcularRutas = pyfiglet.figlet_format("Rutas", font="small")
visualizaResultados = pyfiglet.figlet_format("Resultados", font="small")
guardarInformacion = pyfiglet.figlet_format("Informacion", font="small")


def cargar_datos():
    console.print(Panel.fit(
        f"[green]{cargarDatos}[/green]",
        border_style="green",
        title="Cargar"
    ))

def simular_recorridos():
    console.print(Panel.fit(
        f"[yellow]{simulaRecorridos}[/yellow]",
        border_style="yellow",
        title="Simulación de"
    ))

def calcular_rutas():
    console.print(Panel.fit(
        f"[purple]{calcularRutas}[/purple]",
        border_style="purple",
        title="Calcular"
    ))

def visualizar_resultados():
    console.print(Panel.fit(
        f"[purple]{visualizaResultados}[/purple]",
        border_style="purple",
        title="Visualización de"
    ))

def guardar_informacion():
    console.print(Panel.fit(
        f"[green]{guardarInformacion}[/green]",
        border_style="green",
        title="Guardar"
    ))
