"""Titulos visuales para la consola."""

from __future__ import annotations

import pyfiglet
from rich.panel import Panel


def renderizar_titulo(console) -> None:
    """Muestra el titulo principal del proyecto."""
    titulo = pyfiglet.figlet_format("Electrolineras", font="slant")
    subtitulo = pyfiglet.figlet_format("Grafos + IA", font="small")
    console.print(
        Panel.fit(
            f"[bold cyan]{titulo}[/bold cyan]\n[bold white]{subtitulo}[/bold white]",
            border_style="bright_blue",
            title="Proyecto de Analisis Vial",
        )
    )
