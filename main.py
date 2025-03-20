from os import system
import lib.numericmethods.equations_sqrt_v2 as eq_sqrt
import lib.numericmethods.numeric_integration as num_int
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text

# Nuevo código: Definición de la consola Rich para la interfaz
console = Console()

# Nuevo código: Definición de las categorías de métodos numéricos
CATEGORIES = {
    "1": {
        "name": "Raíces de ecuaciones",
        "methods": {
            "1": {"name": "Método de Bisección", "class": eq_sqrt.BisectMethod},
            "2": {
                "name": "Método de Falsa Posición",
                "class": eq_sqrt.FakePositionMethod,
            },
            "3": {
                "name": "Método de Newton-Raphson",
                "class": eq_sqrt.NewtonRaphsonMethod,
            },
            "4": {
                "name": "Método de la Secante",
                "class": eq_sqrt.SecantMethod,
            },
            "5": {
                "name": "Método de Punto Fijo",
                "class": eq_sqrt.FixedPointMethod,
            },
            # Aquí se pueden agregar más métodos de búsqueda de raíces cuando se implementen
        },
    },
    "2": {
        "name": "Integración numérica",
        "methods": {
            "1": {"name": "Regla del Trapecio", "class": num_int.TrapezoidalRule},
            "2": {"name": "Regla de Simpson 1/3", "class": num_int.SimpsonRule},
            "3": {
                "name": "Regla de Simpson 3/8",
                "class": num_int.SimpsonThreeEighthsRule,
            },
            # Aquí se pueden agregar más métodos de integración cuando se implementen
        },
    },
    # Aquí se pueden agregar más categorías cuando se implementen
}


# Nuevo código: Función para mostrar el menú principal
def show_main_menu():
    """Muestra el menú principal con las categorías disponibles."""
    console.clear()
    console.print(
        Panel.fit(
            Text("MÉTODOS NUMÉRICOS", justify="center", style="bold cyan"),
            subtitle="Selecciona una categoría",
            subtitle_align="center",
            border_style="cyan",
        )
    )

    table = Table(show_header=False, box=None)
    table.add_column("Opción", style="dim")
    table.add_column("Categoría", style="cyan")

    for option, category in CATEGORIES.items():
        table.add_row(option, category["name"])

    table.add_row("q", "Salir")
    console.print(table)

    choice = Prompt.ask(
        "Selecciona una opción", choices=list(CATEGORIES.keys()) + ["q"]
    )
    return choice


# Nuevo código: Función para mostrar el menú de métodos de una categoría
def show_methods_menu(category_id):
    """Muestra el menú de métodos disponibles para una categoría."""
    category = CATEGORIES[category_id]
    console.clear()
    console.print(
        Panel.fit(
            Text(category["name"], justify="center", style="bold cyan"),
            subtitle="Selecciona un método",
            border_style="cyan",
        )
    )

    table = Table(show_header=False, box=None)
    table.add_column("Opción", style="dim")
    table.add_column("Método", style="cyan")

    for option, method in category["methods"].items():
        table.add_row(option, method["name"])

    table.add_row("b", "Volver al menú principal")
    console.print(table)

    choices = list(category["methods"].keys()) + ["b"]
    choice = Prompt.ask("Selecciona una opción", choices=choices)
    return choice


# Nuevo código: Función para solicitar ecuación al usuario
def get_equation():
    """Solicita al usuario ingresar una ecuación."""
    console.print("\n[yellow]Ingresa una ecuación en términos de 'x'[/yellow]")
    console.print("[dim](Ejemplo: exp(x) + 2**(-x) + 2*cos(x) - 6)[/dim]")
    equation_str = Prompt.ask("Ecuación")
    return equation_str


# Nuevo código: Función principal que maneja la navegación del menú
def main():
    """Función principal que maneja la navegación del menú y la ejecución de métodos."""
    while True:
        category_choice = show_main_menu()

        if category_choice == "q":
            console.print("[yellow]¡Hasta pronto![/yellow]")
            break

        while True:
            method_choice = show_methods_menu(category_choice)

            if method_choice == "b":
                break

            method = CATEGORIES[category_choice]["methods"][method_choice]
            console.print(f"\n[bold green]Ejecutando: {method['name']}[/bold green]")

            # Inicializar el método seleccionado
            method_instance = method["class"]()

            # Solicitar ecuación al usuario
            equation_str = get_equation()

            # Configurar y ejecutar el método
            if hasattr(method_instance, "defineEquation"):
                method_instance.defineEquation(equation_str=equation_str)

            # Iniciar el método
            method_instance.start()

            # Preguntar si desea continuar
            continue_choice = Prompt.ask(
                "¿Deseas continuar?", choices=["y", "n"], default="y"
            )

            if continue_choice.lower() == "n":
                return


if __name__ == "__main__":
    system("cls")
    main()
