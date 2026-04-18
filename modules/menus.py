from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

def show_menu():
    table = Table(
        title="📘 [bold cyan]SISTEMA ELECTROLINERAS[/bold cyan]",
        header_style="bold magenta",
        border_style="bright_blue",
        show_lines=True
    )
    table.add_column("Opción", justify="center", style="bold yellow", no_wrap=True)
    table.add_column("Descripción", style="white")

    table.add_row("1", "Cargar datos              ")
    table.add_row("2", "Simular recorridos        ")
    table.add_row("3", "Calcular rutas            ")
    table.add_row("4", "Visualizar resultados     ")
    table.add_row("5", "Guardar Información       ")
    table.add_row("6", "🚪  Salir  ")

    console.print(Panel.fit(table, border_style="cyan", title="Menú Principal"))
