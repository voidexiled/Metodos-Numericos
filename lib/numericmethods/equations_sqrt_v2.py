from os import system
import numpy as np
import sympy as sp
from matplotlib import pyplot as plt
from rich.console import Console
from rich.table import Table
from time import sleep

console = Console()

DEFAULT_EQUATIONS = ["x**2 - 4", "sin(x)", "exp(x) - 2", "x**3 - 2*x + 2"]


def determinar_intervalo(
    equation_str: str, x_min: float = -10, x_max: float = 10, delta_x: float = 0.1
) -> tuple[float | None, float | None]:
    """
    Determina un intervalo [a, b] donde la función cambia de signo.

    Args:
        equation_str: La ecuación como una cadena.
        x_min: Valor mínimo de x.
        x_max: Valor máximo de x.
        delta_x: Incremento en x.

    Returns:
        Una tupla (a, b) con el intervalo, o (None, None) si no se encuentra.
    """
    x = sp.symbols("x")

    try:
        equation = sp.sympify(equation_str)
    except (sp.SympifyError, TypeError):
        console.print("[red bold]Error: Ecuación inválida.[/red bold]")
        return None, None

    f = sp.lambdify(x, equation, "numpy")

    a: float | None = None
    b: float | None = None
    x_current = x_min
    max_iterations = int((x_max - x_min) / delta_x) + 1  # Limite de iteraciones

    for _ in range(max_iterations):
        try:  # Manejo de errores al evaluar f(x)
            f_x_current = f(x_current)
            f_x_next = f(x_current + delta_x)
        except (TypeError, ValueError):  # Ej: log(-1) o sqrt(-1)
            x_current += delta_x
            continue

        if np.isclose(f_x_current, 0.0):  # Si la función evalúa a 0
            a, b = x_current, x_current
            break
        if np.isclose(f_x_next, 0.0):
            a, b = x_current + delta_x, x_current + delta_x
            break
        if f_x_current * f_x_next < 0:
            a, b = x_current, x_current + delta_x
            break

        x_current += delta_x

    if a is not None and b is not None:
        console.print(
            f"[bold green]Intervalo Encontrado:[/bold green] [blue]a = {a}[/blue][green],[/green] [red]b = {b}[/red]"
        )
        return a, b
    else:
        console.print(
            "[bold red]No se encontró un intervalo con cambio de signo en el rango especificado.[/bold red]"
        )
        return None, None


class BaseMethod:
    """Clase base abstracta para los métodos numéricos."""

    x_min: float = -10
    x_max: float = 10
    delta_x: float = 0.1
    equation_str: str = ""
    ep: float = 0.0
    last_equation_str: str = ""
    _console: Console  # Protected, para que las subclases la usen
    _data_text: str  # Protected, para almacenar el output a ser mostrado en pantalla

    def __init__(self) -> None:
        """Constructor común."""
        self._console = Console(record=True)
        self._data_text = ""
        self.update_screen()  # Initialize screen

    def show_equation_plot(self) -> None:
        """Muestra la ecuación como una gráfica de matplotlib."""
        if self.last_equation_str != self.equation_str:
            if self.equation_str != "":
                plt.close("all")
                try:
                    equation = sp.sympify(self.equation_str)
                    latex_str = sp.latex(equation)
                    plt.figure(figsize=(6, 2))
                    plt.text(0.1, 0.5, f"${latex_str}$").set_fontsize(20)
                    plt.axis("off")
                    plt.show(block=False)
                    self.last_equation_str = self.equation_str
                except (sp.SympifyError, TypeError):
                    self._console.print(
                        "[red bold]Error: Ecuación inválida para graficar.[/red bold]"
                    )

    def update_screen(
        self, should_wait: bool = False, wait_seconds: float | int = 0.5
    ) -> None:
        """Actualiza la pantalla de la consola."""
        self.redefine_data_in_screen()  # Actualiza _data_text
        if should_wait:
            max_ms_sleep: float | int = 10.0
            ms_to_sleep = wait_seconds if wait_seconds <= max_ms_sleep else max_ms_sleep
            sleep(ms_to_sleep)
        system("cls")
        self._console.print(self._data_text)
        self.show_equation_plot()

    def redefine_data_in_screen(self) -> None:
        """Actualiza la variable _data_text con los datos actuales.  Debe ser implementado por subclases."""
        raise NotImplementedError("Subclasses must implement redefine_data_in_screen.")

    def print_equation_empty(self, try_to_define: bool = False) -> None:
        """Maneja el caso cuando no hay una ecuación definida."""
        self._console.print(
            "\n[red bold][u]No hay una ecuación definida.[/u][/red bold]"
        )
        if try_to_define:
            self.define_equation()

    def _plot_results(self, *args, **kwargs) -> None:
        """
        Grafica los resultados.  Debe ser implementado por cada subclase.
        """
        raise NotImplementedError("Subclasses must implement _plot_results.")

    def start(self) -> None:
        """Método principal para iniciar el proceso. Debe ser implementado por las subclases."""
        raise NotImplementedError("Subclasses must implement start.")

    def _get_float_input(self, prompt: str, min_value: float | None = None) -> float:
        """Obtiene un input de tipo float del usuario, con validación."""
        while True:
            try:
                value = float(self._console.input(prompt))
                if min_value is not None and value <= min_value:
                    self._console.print(
                        f"[red bold]El valor debe ser mayor que {min_value}.[/red bold]"
                    )
                else:
                    return value
            except ValueError:
                self._console.print(
                    "[red bold]Entrada inválida.  Ingrese un número.[/red bold]"
                )

    def _get_int_input(self, prompt: str, min_value: int | None = None) -> int:
        """Obtiene un input de tipo int del usuario, con validación."""
        while True:
            try:
                value = int(self._console.input(prompt))
                if min_value is not None and value <= min_value:
                    self._console.print(
                        f"[red bold]El valor debe ser mayor que {min_value}.[/red bold]"
                    )
                else:
                    return value
            except ValueError:
                self._console.print(
                    "[red bold]Entrada inválida. Ingrese un número entero.[/red bold]"
                )

    def _select_equation(self) -> None:
        """Permite al usuario seleccionar una ecuación predefinida o ingresar una nueva."""
        self._console.print("[cyan]Ecuaciones predefinidas:[/cyan]")
        for i, eq in enumerate(DEFAULT_EQUATIONS):
            self._console.print(f"[blue]{i + 1}.[/blue] {eq}")
        self._console.print("[blue]0.[/blue] Ingresar ecuación manualmente")

        while True:
            choice = self._get_int_input(
                "[purple italic]Seleccione una opción <--- [/purple italic]",
                min_value=-1,
            )
            if choice == 0:
                self.define_equation()
                break
            elif 1 <= choice <= len(DEFAULT_EQUATIONS):
                self.equation_str = DEFAULT_EQUATIONS[choice - 1]
                self.update_screen()
                break
            else:
                self._console.print("[red bold]Opción inválida.[/red bold]")

    def define_equation(
        self, equation_str: str = "", then_find_ab: bool = False
    ) -> bool:
        """Define la ecuación a utilizar."""
        raise NotImplementedError("Subclasses must define define_equation.")


class BisectMethod(BaseMethod):
    a: float = 0.0
    b: float = 0.0

    def redefine_data_in_screen(self) -> None:
        self._data_text = f"""
                                [cyan bold underline]-----Raíces de ecuaciones-----[/cyan bold underline]
                                [cyan bold frame]  ---Método de Bisección---  [/cyan bold frame]
                                [yellow italic]{sp.pretty(self.equation_str)}[/yellow italic]
                                [blue italic]a = {self.a}[/blue italic]
                                [red italic]b = {self.b}[/red italic]
                                [red uu]error permitido = {self.ep}[/red uu]
                                """

    def _plot_results(
        self,
        column_i: list[int],
        column_a: list[float],
        column_b: list[float],
        column_f_a: list[float],
        column_f_b: list[float],
        column_xi: list[float],
        column_f_xi: list[float],
        column_abs_f_xi: list[float],
        column_eactual_less_eallowed: list[str],
    ) -> None:
        x = sp.symbols("x")
        equation = sp.sympify(self.equation_str)
        f = sp.lambdify(x, equation, "numpy")

        # Puntos para graficar la función
        x_vals = np.linspace(self.a - 0.5, self.b + 0.5, 400)
        y_vals = f(x_vals)

        # Crear la gráfica
        plt.figure(figsize=(8, 6))
        plt.plot(x_vals, y_vals, "b-", label="f(x)")  # Función
        plt.axhline(0, color="black", linewidth=0.8)  # Eje x
        plt.axvline(0, color="black", linewidth=0.8)  # Eje y

        # Marcar los puntos a, b, y xm
        plt.plot(column_a, column_f_a, "ro", label="a")
        plt.plot(column_b, column_f_b, "bo", label="b")
        plt.plot(column_xi, column_f_xi, "go", label="xi")

        # Última iteracion
        plt.axvline(
            column_a[-1], color="red", linestyle="--", label=f"a={column_a[-1]:.4f}"
        )
        plt.axvline(
            column_b[-1], color="blue", linestyle="--", label=f"b={column_b[-1]:.4f}"
        )
        plt.axvline(
            column_xi[-1],
            color="green",
            linestyle="--",
            label=f"xi={column_xi[-1]:.4f}",
        )

        # Etiquetas y título
        plt.xlabel("x")
        plt.ylabel("f(x)")
        plt.title("Método de Bisección")
        plt.legend()
        plt.grid(True)

        # Mostrar la gráfica
        plt.show()

    def start(self) -> None:
        if not self.equation_str:
            self._select_equation()

        while self.ep == 0.0:
            self.ep = self._get_float_input(
                "[purple italic]Error permitido <--- [/]", min_value=0.0
            )

        x = sp.symbols("x")
        try:
            equation = sp.sympify(self.equation_str)
        except (sp.SympifyError, TypeError):
            self._console.print("[red bold]Error: Ecuación inválida.[/red bold]")
            return
        f = sp.lambdify(x, equation, "numpy")

        next_iteration = True

        i_column: list[int] = []
        a_column: list[float] = []
        b_column: list[float] = []
        fa_column: list[float] = []
        fb_column: list[float] = []
        xi_column: list[float] = []
        f_xi_column: list[float] = []
        abs_f_xi_column: list[float] = []
        e_actual_less_e_allowed_column: list[str] = []

        i = 1
        a = self.a
        b = self.b
        try:
            fa = f(a)
            fb = f(b)
        except (TypeError, ValueError) as e:
            self._console.print(
                f"[red bold]Error al evaluar la función: {e}[/red bold]"
            )
            return

        table = Table(title="Bisección")
        table.add_column("Iteración")
        table.add_column("a")
        table.add_column("b")
        table.add_column("f(a)")
        table.add_column("f(b)")
        table.add_column("xi")
        table.add_column("f(xi)")
        table.add_column("abs(f(xi))")
        table.add_column("ea <= ep")

        while next_iteration:
            self.update_screen()

            if i >= 2:
                last_f_xi_is_negative = f_xi_column[i - 2] < 0

                last_fa_is_negative = fa_column[i - 2] < 0
                last_fb_is_negative = fb_column[i - 2] < 0

                if last_f_xi_is_negative:
                    if last_fa_is_negative:
                        a = xi_column[i - 2]
                        fa = f(a)
                    elif last_fb_is_negative:
                        b = xi_column[i - 2]
                        fb = f(b)
                else:
                    if not last_fa_is_negative:
                        a = xi_column[i - 2]
                        fa = f(a)
                    elif not last_fb_is_negative:
                        b = xi_column[i - 2]
                        fb = f(b)

            i_column.append(i)
            a_column.append(a)
            b_column.append(b)
            fa_column.append(fa)
            fb_column.append(fb)
            xi_column.append((a_column[i - 1] + b_column[i - 1]) / 2)
            f_xi_column.append(f(xi_column[i - 1]))
            abs_f_xi_column.append(np.abs(f_xi_column[i - 1]))
            if abs_f_xi_column[i - 1] <= self.ep:
                e_actual_less_e_allowed_column.append("si")
            else:
                e_actual_less_e_allowed_column.append("no")

            table.add_row(
                str(i_column[i - 1]),
                str(a_column[i - 1]),
                str(b_column[i - 1]),
                str(fa_column[i - 1]),
                str(fb_column[i - 1]),
                str(xi_column[i - 1]),
                str(f_xi_column[i - 1]),
                str(abs_f_xi_column[i - 1]),
                str(e_actual_less_e_allowed_column[i - 1]),
            )

            self._console.print(table)
            i += 1

            answer = self._console.input(
                '[purple italic]Siguiente Iteración? y/n ("." to run until "sí") <--- '
            )

            if answer.lower() == "n":
                next_iteration = False

            if answer.lower() == ".":
                while e_actual_less_e_allowed_column[-1] == "no":
                    if i >= 2:
                        last_f_xi_is_negative = f_xi_column[i - 2] < 0
                        last_fa_is_negative = fa_column[i - 2] < 0
                        last_fb_is_negative = fb_column[i - 2] < 0

                        if last_f_xi_is_negative:
                            if last_fa_is_negative:
                                a = xi_column[i - 2]
                                fa = f(a)
                            else:
                                b = xi_column[i - 2]
                                fb = f(b)
                        else:
                            if not last_fa_is_negative:
                                a = xi_column[i - 2]
                                fa = f(a)
                            else:
                                b = xi_column[i - 2]
                                fb = f(b)

                    i_column.append(i)
                    a_column.append(a)
                    b_column.append(b)
                    fa_column.append(fa)
                    fb_column.append(fb)
                    xi_column.append((a + b) / 2)  # Use current a and b
                    f_xi_column.append(f(xi_column[i - 1]))
                    abs_f_xi_column.append(np.abs(f_xi_column[i - 1]))

                    if abs_f_xi_column[i - 1] <= self.ep:
                        e_actual_less_e_allowed_column.append("si")
                        table.add_row(
                            str(i_column[i - 1]),
                            str(a_column[i - 1]),
                            str(b_column[i - 1]),
                            str(fa_column[i - 1]),
                            str(fb_column[i - 1]),
                            str(xi_column[i - 1]),
                            str(f_xi_column[i - 1]),
                            str(abs_f_xi_column[i - 1]),
                            str(e_actual_less_e_allowed_column[i - 1]),
                        )
                        self.update_screen()
                        self._console.print(table)
                        break  # Exit the loop
                    else:
                        e_actual_less_e_allowed_column.append("no")
                        table.add_row(
                            str(i_column[i - 1]),
                            str(a_column[i - 1]),
                            str(b_column[i - 1]),
                            str(fa_column[i - 1]),
                            str(fb_column[i - 1]),
                            str(xi_column[i - 1]),
                            str(f_xi_column[i - 1]),
                            str(abs_f_xi_column[i - 1]),
                            str(e_actual_less_e_allowed_column[i - 1]),
                        )

                    i += 1

        self._console.save_html("table.html")
        self._plot_results(
            i_column,
            a_column,
            b_column,
            fa_column,
            fb_column,
            xi_column,
            f_xi_column,
            abs_f_xi_column,
            e_actual_less_e_allowed_column,
        )
        self._console.print(
            "[blink cyan]All output was saved to table.html.[/blink cyan]",
            justify="center",
        )
        should_restart = self._console.input(
            "[purple italic]Restart? (y/n): [/purple italic]"
        )
        if should_restart.lower() == "y":
            next_bisect = BisectMethod()
            next_bisect.start()

    def find_ab(
        self, x_min: float = 0.0, x_max: float = 0.0, delta_x: float = 0.1
    ) -> bool:
        """Encuentra los valores iniciales de 'a' y 'b'."""
        if delta_x <= 0:
            self._console.print(
                "[bold red][u]delta_x[/u][/bold red][red] debe ser mayor que [bold][u]0[/u][/bold][/red] "
            )
            return False
        if self.equation_str == "":
            self.print_equation_empty()
            self.x_min, self.x_max, self.delta_x = x_min, x_max, delta_x
            return self.define_equation(then_find_ab=True)

        if x_min == 0.0 and x_max == 0.0:  # Use 0.0 for float comparison
            self._console.print(
                "[purple italic]Buscar intervalos desde: [/purple italic]"
            )
            x_min = self._get_float_input(
                "[purple italic]Limite inferior <--- [/purple italic]"
            )
            x_max = self._get_float_input(
                "[purple italic]Limite superior <--- [/purple italic]"
            )

        a, b = determinar_intervalo(
            self.equation_str, x_min, x_max, delta_x
        )  # Pasamos los argumentos
        if a is not None and b is not None:
            self.a = a
            self.b = b
            self.update_screen(should_wait=True)
            return True  # Indica que se encontraron a y b
        else:
            self._console.print(
                "[bold red]Error: 'a' or 'b' could not be determined[/bold red]"
            )
            return False

    def define_equation(
        self, equation_str: str = "", then_find_ab: bool = False
    ) -> bool:

        if not equation_str:
            equation_str = self._console.input(
                "[purple italic]Ecuación --- [/purple italic]"
            )
        try:
            sp.sympify(equation_str)  # Check for valid equation
            self.equation_str = equation_str
            self.update_screen()
        except (sp.SympifyError, TypeError):
            self._console.print("[red bold]Error: Ecuación inválida.[/red bold]")
            return False  # Indicate failure

        if not then_find_ab:
            answer = self._console.input(
                "[purple italic]Deseas que busque 'a' y 'b' automáticamente? y/n <--- [/purple italic]"
            )
            if answer.lower() == "y":
                then_find_ab = True

        if then_find_ab:
            return self.find_ab()
        else:
            self.a = self._get_float_input("[purple italic]A <--- [/purple italic]")
            self.b = self._get_float_input("[purple italic]B <--- [/purple italic]")
            self.update_screen()
            return True  # Indicate success


class FakePositionMethod(BaseMethod):
    # NUEVO CÓDIGO: Implementación del Método de Falsa Posición
    a: float = 0.0
    b: float = 0.0

    def redefine_data_in_screen(self) -> None:
        self._data_text = f"""
                                [cyan bold underline]-----Raíces de ecuaciones-----[/cyan bold underline]
                                [cyan bold frame]  ---Método de Falsa Posición---  [/cyan bold frame]
                                [yellow italic]{sp.pretty(self.equation_str)}[/yellow italic]
                                [blue italic]a = {self.a}[/blue italic]
                                [red italic]b = {self.b}[/red italic]
                                [red uu]error permitido = {self.ep}[/red uu]
                                """

    def _plot_results(
        self,
        column_i: list[int],
        column_a: list[float],
        column_b: list[float],
        column_f_a: list[float],
        column_f_b: list[float],
        column_xi: list[float],
        column_f_xi: list[float],
        column_abs_f_xi: list[float],
        column_eactual_less_eallowed: list[str],
    ) -> None:
        x = sp.symbols("x")
        equation = sp.sympify(self.equation_str)
        f = sp.lambdify(x, equation, "numpy")

        # Puntos para graficar la función
        x_vals = np.linspace(self.a - 0.5, self.b + 0.5, 400)
        y_vals = f(x_vals)

        # Crear la gráfica
        plt.figure(figsize=(8, 6))
        plt.plot(x_vals, y_vals, "b-", label="f(x)")  # Función
        plt.axhline(0, color="black", linewidth=0.8)  # Eje x
        plt.axvline(0, color="black", linewidth=0.8)  # Eje y

        # Marcar los puntos a, b, y xi
        plt.plot(column_a, column_f_a, "ro", label="a")
        plt.plot(column_b, column_f_b, "bo", label="b")
        plt.plot(column_xi, column_f_xi, "go", label="xi")

        # Última iteración
        plt.axvline(
            column_a[-1], color="red", linestyle="--", label=f"a={column_a[-1]:.4f}"
        )
        plt.axvline(
            column_b[-1], color="blue", linestyle="--", label=f"b={column_b[-1]:.4f}"
        )
        plt.axvline(
            column_xi[-1],
            color="green",
            linestyle="--",
            label=f"xi={column_xi[-1]:.4f}",
        )

        # Etiquetas y título
        plt.xlabel("x")
        plt.ylabel("f(x)")
        plt.title("Método de Falsa Posición")
        plt.legend()
        plt.grid(True)

        # Mostrar la gráfica
        plt.show()

    def start(self) -> None:
        # NUEVO CÓDIGO: Algoritmo de Falsa Posición
        if not self.equation_str:
            self._select_equation()

        while self.ep == 0.0:
            self.ep = self._get_float_input(
                "[purple italic]Error permitido <--- [/]", min_value=0
            )

        x = sp.symbols("x")

        try:
            equation = sp.sympify(self.equation_str)
        except (sp.SympifyError, TypeError):
            self._console.print("[red bold]Error: Ecuación inválida.[/red bold]")
            return
        f = sp.lambdify(x, equation, "numpy")

        next_iteration = True

        i_column: list[int] = []
        a_column: list[float] = []
        b_column: list[float] = []
        fa_column: list[float] = []
        fb_column: list[float] = []
        xi_column: list[float] = []
        f_xi_column: list[float] = []
        abs_f_xi_column: list[float] = []
        e_actual_less_e_allowed_column: list[str] = []

        i = 1
        a = self.a
        b = self.b
        try:
            fa = f(a)
            fb = f(b)
        except (TypeError, ValueError) as e:
            self._console.print(
                f"[red bold]Error al evaluar la función: {e}[/red bold]"
            )
            return

        table = Table(title="Falsa Posición")
        table.add_column("Iteración")
        table.add_column("a")
        table.add_column("b")
        table.add_column("f(a)")
        table.add_column("f(b)")
        table.add_column("xi")
        table.add_column("f(xi)")
        table.add_column("abs(f(xi))")
        table.add_column("ea <= ep")

        while next_iteration:
            self.update_screen()

            # Calcular xi usando la fórmula de falsa posición
            # xi = a - (f(a) * (b - a)) / (f(b) - f(a))
            if i >= 2:

                # Determinar qué intervalo preservar
                if f_xi_column[i - 2] * fa_column[i - 2] < 0:
                    b = xi_column[i - 2]
                    fb = f(b)
                else:
                    a = xi_column[i - 2]
                    fa = f(a)

            i_column.append(i)
            a_column.append(a)
            b_column.append(b)
            fa_column.append(fa)
            fb_column.append(fb)

            # Evitar división por cero
            if fb - fa == 0:
                self._console.print(
                    "[bold red]Error: División por cero. fb - fa es cero.[/bold red]"
                )
                return

            # Fórmula de falsa posición
            xi = a - (fa * (b - a)) / (fb - fa)
            xi_column.append(xi)
            f_xi_column.append(f(xi_column[i - 1]))
            abs_f_xi_column.append(np.abs(f_xi_column[i - 1]))

            if abs_f_xi_column[i - 1] <= self.ep:
                e_actual_less_e_allowed_column.append("sí")
            else:
                e_actual_less_e_allowed_column.append("no")

            table.add_row(
                str(i_column[i - 1]),
                str(a_column[i - 1]),
                str(b_column[i - 1]),
                str(fa_column[i - 1]),
                str(fb_column[i - 1]),
                str(xi_column[i - 1]),
                str(f_xi_column[i - 1]),
                str(abs_f_xi_column[i - 1]),
                str(e_actual_less_e_allowed_column[i - 1]),
            )

            self._console.print(table)
            i += 1

            answer = self._console.input(
                '[purple italic]Siguiente Iteración? y/n ("." to run until "sí") <--- '
            )

            if answer.lower() == "n":
                next_iteration = False

            if answer.lower() == ".":
                while e_actual_less_e_allowed_column[-1] == "no":
                    if i >= 2:
                        # Determinar qué intervalo preservar
                        if (
                            f_xi_column[-1] * fa < 0
                        ):  # Usar valores actuales, no de la iteracion anterior
                            b = xi_column[-1]
                            fb = f(b)
                        else:
                            a = xi_column[-1]
                            fa = f(a)
                    i_column.append(i)
                    a_column.append(a)
                    b_column.append(b)
                    fa_column.append(fa)
                    fb_column.append(fb)

                    # Evitar división por cero
                    if fb - fa == 0:
                        self._console.print(
                            "[bold red]Error: División por cero. fb - fa es cero.[/bold red]"
                        )
                        return

                    xi = a - (fa * (b - a)) / (fb - fa)  # Formula correcta
                    xi_column.append(xi)
                    f_xi_column.append(f(xi))
                    abs_f_xi_column.append(np.abs(f_xi_column[-1]))

                    if abs_f_xi_column[-1] <= self.ep:
                        e_actual_less_e_allowed_column.append("sí")
                        table.add_row(
                            str(i_column[-1]),
                            str(a_column[-1]),
                            str(b_column[-1]),
                            str(fa_column[-1]),
                            str(fb_column[-1]),
                            str(xi_column[-1]),
                            str(f_xi_column[-1]),
                            str(abs_f_xi_column[-1]),
                            str(e_actual_less_e_allowed_column[-1]),
                        )
                        self.update_screen()
                        self._console.print(table)
                        next_iteration = False
                        break  # Exit the loop
                    else:
                        e_actual_less_e_allowed_column.append("no")
                        table.add_row(
                            str(i_column[-1]),
                            str(a_column[-1]),
                            str(b_column[-1]),
                            str(fa_column[-1]),
                            str(fb_column[-1]),
                            str(xi_column[-1]),
                            str(f_xi_column[-1]),
                            str(abs_f_xi_column[-1]),
                            str(e_actual_less_e_allowed_column[-1]),
                        )

                    i += 1

        self._console.save_html("table.html")
        self._plot_results(
            i_column,
            a_column,
            b_column,
            fa_column,
            fb_column,
            xi_column,
            f_xi_column,
            abs_f_xi_column,
            e_actual_less_e_allowed_column,
        )
        self._console.print(
            "[blink cyan]All output was saved to table.html.[/blink cyan]",
            justify="center",
        )
        should_restart = self._console.input(
            "[purple italic]Restart? (y/n): [/purple italic]"
        )
        if should_restart.lower() == "y":
            next_method = FakePositionMethod()
            next_method.start()

    def find_ab(
        self, x_min: float = 0.0, x_max: float = 0.0, delta_x: float = 0.1
    ) -> bool:
        """Encuentra los valores iniciales de 'a' y 'b'."""
        if delta_x <= 0:
            self._console.print(
                "[bold red][u]delta_x[/u][/bold red][red] debe ser mayor que [bold][u]0[/u][/bold][/red] "
            )
            return False
        if self.equation_str == "":
            self.print_equation_empty()
            self.x_min, self.x_max, self.delta_x = x_min, x_max, delta_x
            return self.define_equation(then_find_ab=True)

        if x_min == 0.0 and x_max == 0.0:  # Use 0.0 for float comparison
            self._console.print(
                "[purple italic]Buscar intervalos desde: [/purple italic]"
            )
            x_min = self._get_float_input(
                "[purple italic]Limite inferior <--- [/purple italic]"
            )
            x_max = self._get_float_input(
                "[purple italic]Limite superior <--- [/purple italic]"
            )

        a, b = determinar_intervalo(
            self.equation_str, x_min, x_max, delta_x
        )  # Pasamos los argumentos
        if a is not None and b is not None:
            self.a = a
            self.b = b
            self.update_screen(should_wait=True)
            return True  # Indica que se encontraron a y b
        else:
            self._console.print(
                "[bold red]Error: 'a' or 'b' could not be determined[/bold red]"
            )
            return False

    def define_equation(
        self, equation_str: str = "", then_find_ab: bool = False
    ) -> bool:
        """Define la ecuación a utilizar."""
        if not equation_str:
            equation_str = self._console.input(
                "[purple italic]Ecuación --- [/purple italic]"
            )
        try:
            sp.sympify(equation_str)
            self.equation_str = equation_str
            self.update_screen()
        except (sp.SympifyError, TypeError):
            self._console.print("[red bold]Error: Ecuación inválida.[/red bold]")
            return False

        if not then_find_ab:
            answer = self._console.input(
                "[purple italic]Deseas que busque 'a' y 'b' automáticamente? y/n <--- [/purple italic]"
            )
            if answer.lower() == "y":
                then_find_ab = True

        if then_find_ab:
            return self.find_ab()
        else:
            self.a = self._get_float_input("[purple italic]a <--- [/purple italic]")
            self.b = self._get_float_input("[purple italic]b <--- [/purple italic]")
            self.update_screen()
            return True


class NewtonRaphsonMethod(BaseMethod):
    x0: float = 0.0  # Punto inicial

    def redefine_data_in_screen(self) -> None:
        self._data_text = f"""
                                [cyan bold underline]-----Raíces de ecuaciones-----[/cyan bold underline]
                                [cyan bold frame]  ---Método de Newton-Raphson---  [/cyan bold frame]
                                [yellow italic]{sp.pretty(self.equation_str)}[/yellow italic]
                                [blue italic]x0 = {self.x0}[/blue italic]
                                [red uu]error permitido = {self.ep}[/red uu]
                                """

    def _plot_results(
        self,
        column_i: list[int],
        column_xi: list[float],
        column_fxi: list[float],
        column_dxi: list[str],  # Cambiado a str para la representación
        column_dfxi: list[float],
        column_xi1: list[float],
        column_abs_error: list[float],
        column_eactual_less_eallowed: list[str],
    ) -> None:

        x = sp.symbols("x")
        equation = sp.sympify(self.equation_str)
        f = sp.lambdify(x, equation, "numpy")

        # Calcular el rango para la gráfica
        min_x = min(column_xi) - 1
        max_x = max(column_xi) + 1

        # Puntos para graficar la función
        x_vals = np.linspace(min_x, max_x, 400)
        y_vals = f(x_vals)

        # Crear la gráfica
        plt.figure(figsize=(10, 6))
        plt.plot(x_vals, y_vals, "b-", label="f(x)")  # Función
        plt.axhline(0, color="black", linewidth=0.8)  # Eje x
        plt.axvline(0, color="black", linewidth=0.8)  # Eje y

        # Graficar la última iteración
        last_xi = column_xi[-1]

        # Marcar los puntos xi, rectas tangentes
        for i in range(len(column_xi)):
            plt.plot(column_xi[i], column_fxi[i], "ro", label=f"xi" if i == 0 else "")

            # Si no es el último punto, graficar la recta tangente
            if i < len(column_xi) - 1:
                # Graficar un segmento de recta tangente
                x_tangent = np.linspace(column_xi[i] - 0.5, column_xi[i] + 0.5, 2)
                y_tangent = column_dfxi[i] * (x_tangent - column_xi[i]) + column_fxi[i]
                plt.plot(
                    x_tangent,
                    y_tangent,
                    "g--",
                    alpha=0.5,
                    label=f"Tangente en xi" if i == 0 else "",
                )

                # Marcar el punto donde la tangente cruza el eje x
                plt.plot(column_xi1[i], 0, "gx", label=f"xi+1" if i == 0 else "")

        # Marcar el último punto con una línea vertical
        plt.axvline(
            last_xi,
            color="red",
            linestyle="--",
            label=f"Última iteración: {last_xi:.4f}",
        )

        # Etiquetas y título
        plt.xlabel("x")
        plt.ylabel("f(x)")
        plt.title("Método de Newton-Raphson")
        plt.legend()
        plt.grid(True)

        # Mostrar la gráfica
        plt.show()

    def start(self) -> None:

        if not self.equation_str:
            self._select_equation()

        # Solicitar el error permitido
        while self.ep == 0.0:
            self.ep = self._get_float_input(
                "[purple italic]Error permitido <--- [/]", min_value=0
            )

        # Crear el símbolo y la ecuación
        x = sp.symbols("x")
        try:
            equation = sp.sympify(self.equation_str)
        except (sp.SympifyError, TypeError):
            self._console.print("[red bold]Error: Ecuación inválida.[/red bold]")
            return

        f = sp.lambdify(x, equation, "numpy")

        # Calcular la derivada
        try:
            derivative = sp.diff(equation, x)
            df = sp.lambdify(x, derivative, "numpy")
        except (sp.SympifyError, TypeError) as e:
            self._console.print(
                f"[red bold]Error al calcular la derivada: {e}[/red bold]"
            )
            return

        # Mostrar la derivada
        self._console.print(f"[cyan]Derivada: {derivative}[/cyan]")

        next_iteration = True

        # Columnas para almacenar los datos
        i_column: list[int] = []
        xi_column: list[float] = []
        fxi_column: list[float] = []
        dxi_column: list[str] = []  # Derivada en xi, como string
        dfxi_column: list[float] = []  # Valor de la derivada en xi
        xi1_column: list[float] = []  # Siguiente valor de x
        abs_error_column: list[float] = []  # Error absoluto
        e_actual_less_e_allowed_column: list[str] = (
            []
        )  # ¿Error actual <= Error permitido?

        i = 1
        xi = self.x0

        # Crear tabla para mostrar resultados
        table = Table(title="Newton-Raphson")
        table.add_column("Iteración")
        table.add_column("xi")
        table.add_column("f(xi)")
        table.add_column("f'(xi)")
        table.add_column("xi+1")
        table.add_column("|xi+1 - xi|")
        table.add_column("ea <= ep")

        while next_iteration:
            self.update_screen()

            # Calcular los valores para esta iteración
            try:
                fxi = f(xi)
                dfxi = df(xi)
            except (TypeError, ValueError) as e:
                self._console.print(
                    f"[red bold]Error al evaluar la función o su derivada: {e}[/red bold]"
                )
                return

            # Evitar división por cero
            if abs(dfxi) < 1e-10:
                self._console.print(
                    "[bold red]Error: Derivada muy cercana a cero. División por cero.[/bold red]"
                )
                break

            # Fórmula de Newton-Raphson: xi+1 = xi - f(xi)/f'(xi)
            xi1 = xi - fxi / dfxi

            # Calcular el error absoluto
            abs_error = abs(xi1 - xi)

            # Almacenar los valores calculados
            i_column.append(i)
            xi_column.append(xi)
            fxi_column.append(fxi)
            dxi_column.append(str(derivative))  # Guardar la derivada como string
            dfxi_column.append(dfxi)
            xi1_column.append(xi1)
            abs_error_column.append(abs_error)

            # Verificar si el error es menor o igual al permitido
            if abs_error <= self.ep:
                e_actual_less_e_allowed_column.append("sí")
            else:
                e_actual_less_e_allowed_column.append("no")

            # Agregar fila a la tabla
            table.add_row(
                str(i),
                str(xi),
                str(fxi),
                str(dfxi),
                str(xi1),
                str(abs_error),
                e_actual_less_e_allowed_column[-1],
            )

            # Mostrar la tabla
            self._console.print(table)

            # Preparar para la siguiente iteración
            xi = xi1
            i += 1

            # Preguntar si continuar
            answer = self._console.input(
                '[purple italic]Siguiente Iteración? y/n ("." to run until "sí") <--- '
            )

            if answer.lower() == "n":
                next_iteration = False

            if answer.lower() == ".":
                while e_actual_less_e_allowed_column[-1] == "no":
                    # Calcular los valores para esta iteración
                    try:
                        fxi = f(xi)
                        dfxi = df(xi)
                    except (TypeError, ValueError) as e:
                        self._console.print(
                            f"[red bold]Error al evaluar la función o su derivada: {e}[/red bold]"
                        )
                        return

                    # Evitar división por cero
                    if abs(dfxi) < 1e-10:
                        self._console.print(
                            "[bold red]Error: Derivada muy cercana a cero. División por cero.[/bold red]"
                        )
                        break

                    xi1 = xi - fxi / dfxi  # Formula newton-raphson

                    abs_error = abs(xi1 - xi)

                    i_column.append(i)
                    xi_column.append(xi)
                    fxi_column.append(fxi)
                    dxi_column.append(str(derivative))
                    dfxi_column.append(dfxi)
                    xi1_column.append(xi1)
                    abs_error_column.append(abs_error)

                    if abs_error <= self.ep:
                        e_actual_less_e_allowed_column.append("sí")
                        table.add_row(
                            str(i),
                            str(xi),
                            str(fxi),
                            str(dfxi),
                            str(xi1),
                            str(abs_error),
                            e_actual_less_e_allowed_column[-1],
                        )
                        self.update_screen()
                        self._console.print(table)
                        break
                    else:
                        e_actual_less_e_allowed_column.append("no")
                        table.add_row(
                            str(i),
                            str(xi),
                            str(fxi),
                            str(dfxi),
                            str(xi1),
                            str(abs_error),
                            e_actual_less_e_allowed_column[-1],
                        )
                    i += 1
                    xi = xi1

        # Guardar resultados y mostrar gráfica
        self._console.save_html("table.html")
        self._plot_results(
            i_column,
            xi_column,
            fxi_column,
            dxi_column,
            dfxi_column,
            xi1_column,
            abs_error_column,
            e_actual_less_e_allowed_column,
        )
        self._console.print(
            "[blink cyan]All output was saved to table.html.[/blink cyan]",
            justify="center",
        )
        should_restart = self._console.input(
            "[purple italic]Restart? (y/n): [/purple italic]"
        )
        if should_restart.lower() == "y":
            next_method = NewtonRaphsonMethod()
            next_method.start()

    def find_starting_point(self) -> bool:
        # NUEVO CÓDIGO: Buscar un punto inicial adecuado
        if self.equation_str == "":
            self.print_equation_empty()
            return False

        self.x0 = self._get_float_input(
            "[purple italic]Punto inicial x0 <--- [/purple italic]"
        )
        self.update_screen(should_wait=True)
        return True

    def define_equation(
        self, equation_str: str = "", find_starting_point: bool = False
    ) -> bool:
        """Define la ecuación y, opcionalmente, encuentra el punto de inicio."""
        if not equation_str:
            equation_str = self._console.input(
                "[purple italic]Ecuación --- [/purple italic]"
            )
        try:
            sp.sympify(equation_str)
            self.equation_str = equation_str
            self.update_screen()
        except (sp.SympifyError, TypeError):
            self._console.print("[red bold]Error: Ecuación inválida.[/red bold]")
            return False

        if not find_starting_point:
            answer = self._console.input(
                "[purple italic]¿Deseas ingresar un punto inicial? y/n <--- [/purple italic]"
            )
            if answer.lower() == "y":
                find_starting_point = True

        if find_starting_point:
            return self.find_starting_point()
        return True


class SecantMethod(BaseMethod):
    x0: float = 0.0  # Primer punto
    x1: float = 0.0  # Segundo punto

    def redefine_data_in_screen(self) -> None:
        self._data_text = f"""
                                [cyan bold underline]-----Raíces de ecuaciones-----[/cyan bold underline]
                                [cyan bold frame]  ---Método de la Secante---  [/cyan bold frame]
                                [yellow italic]{sp.pretty(self.equation_str)}[/yellow italic]
                                [blue italic]x0 = {self.x0}[/blue italic]
                                [blue italic]x1 = {self.x1}[/blue italic]
                                [red uu]error permitido = {self.ep}[/red uu]
                                """

    def _plot_results(
        self,
        column_i: list[int],
        column_xi_1: list[float],
        column_xi: list[float],
        column_fxi_1: list[float],
        column_fxi: list[float],
        column_xi1: list[float],
        column_abs_error: list[float],
        column_eactual_less_eallowed: list[str],
    ) -> None:
        x = sp.symbols("x")
        equation = sp.sympify(self.equation_str)
        f = sp.lambdify(x, equation, "numpy")

        # Calcular el rango para la gráfica
        min_x = min(min(column_xi_1), min(column_xi)) - 1
        max_x = max(max(column_xi_1), max(column_xi)) + 1

        # Puntos para graficar la función
        x_vals = np.linspace(min_x, max_x, 400)
        y_vals = f(x_vals)

        # Crear la gráfica
        plt.figure(figsize=(10, 6))
        plt.plot(x_vals, y_vals, "b-", label="f(x)")  # Función
        plt.axhline(0, color="black", linewidth=0.8)  # Eje x
        plt.axvline(0, color="black", linewidth=0.8)  # Eje y

        # Graficar los puntos y las secantes
        for i in range(len(column_xi)):
            # Graficar los puntos xi-1 y xi
            plt.plot(
                column_xi_1[i],
                column_fxi_1[i],
                "ro",
                label="xi-1, xi" if i == 0 else "",
            )
            plt.plot(column_xi[i], column_fxi[i], "ro")

            # Graficar la secante
            secant_x = np.array([column_xi_1[i], column_xi[i]])
            secant_y = np.array([column_fxi_1[i], column_fxi[i]])
            plt.plot(
                secant_x, secant_y, "g--", alpha=0.5, label="Secante" if i == 0 else ""
            )

            # Marcar el punto donde la secante cruza el eje x
            plt.plot(column_xi1[i], 0, "gx", label="xi+1" if i == 0 else "")

        # Marcar el último punto xi+1 con una línea vertical
        plt.axvline(
            column_xi1[-1],
            color="red",
            linestyle="--",
            label=f"Última iteración: {column_xi1[-1]:.4f}",
        )

        # Etiquetas y título
        plt.xlabel("x")
        plt.ylabel("f(x)")
        plt.title("Método de la Secante")
        plt.legend()
        plt.grid(True)

        # Mostrar la gráfica
        plt.show()

    def start(self) -> None:

        if not self.equation_str:
            self._select_equation()

        while self.ep == 0.0:
            self.ep = self._get_float_input(
                "[purple italic]Error permitido <--- [/]", min_value=0
            )

        x = sp.symbols("x")
        try:
            equation = sp.sympify(self.equation_str)
        except (sp.SympifyError, TypeError):
            self._console.print("[red bold]Error: Ecuación inválida.[/red bold]")
            return
        f = sp.lambdify(x, equation, "numpy")

        next_iteration = True

        # Listas para almacenar los datos
        i_column: list[int] = []
        xi_1_column: list[float] = []
        xi_column: list[float] = []
        fxi_1_column: list[float] = []
        fxi_column: list[float] = []
        xi1_column: list[float] = []
        abs_error_column: list[float] = []
        e_actual_less_e_allowed_column: list[str] = []

        i = 1
        xi_1 = self.x0
        xi = self.x1

        # Crear tabla
        table = Table(title="Método de la Secante")
        table.add_column("Iteración")
        table.add_column("xi-1")
        table.add_column("xi")
        table.add_column("f(xi-1)")
        table.add_column("f(xi)")
        table.add_column("xi+1")
        table.add_column("|xi+1 - xi|")
        table.add_column("ea <= ep")

        while next_iteration:
            self.update_screen()

            try:
                fxi_1 = f(xi_1)
                fxi = f(xi)
            except (TypeError, ValueError) as e:
                self._console.print(
                    f"[red bold]Error al evaluar la función: {e}[/red bold]"
                )
                return

            # Evitar división por cero
            if abs(fxi - fxi_1) < 1e-10:
                self._console.print(
                    "[bold red]Error: Denominador muy cercano a cero. División por cero.[/bold red]"
                )
                break

            # Fórmula del Método de la Secante
            xi1 = xi - fxi * (xi - xi_1) / (fxi - fxi_1)
            abs_error = abs(xi1 - xi)

            i_column.append(i)
            xi_1_column.append(xi_1)
            xi_column.append(xi)
            fxi_1_column.append(fxi_1)
            fxi_column.append(fxi)
            xi1_column.append(xi1)
            abs_error_column.append(abs_error)

            if abs_error <= self.ep:
                e_actual_less_e_allowed_column.append("sí")
            else:
                e_actual_less_e_allowed_column.append("no")

            table.add_row(
                str(i),
                str(xi_1),
                str(xi),
                str(fxi_1),
                str(fxi),
                str(xi1),
                str(abs_error),
                e_actual_less_e_allowed_column[-1],
            )

            self._console.print(table)

            xi_1 = xi
            xi = xi1
            i += 1

            answer = self._console.input(
                '[purple italic]Siguiente Iteración? y/n ("." to run until "sí") <--- '
            )

            if answer.lower() == "n":
                next_iteration = False

            if answer.lower() == ".":
                while e_actual_less_e_allowed_column[-1] == "no":
                    try:
                        fxi_1 = f(xi_1)
                        fxi = f(xi)
                    except (TypeError, ValueError) as e:
                        self._console.print(
                            f"[red bold]Error al evaluar la función: {e}[/red bold]"
                        )
                        return

                    if abs(fxi - fxi_1) < 1e-10:
                        self._console.print(
                            "[bold red]Error: Denominador cercano a cero.  Division por cero.[/bold red]"
                        )
                        break

                    xi1 = xi - (fxi * (xi - xi_1)) / (
                        fxi - fxi_1
                    )  # Formula de la secante
                    abs_error = abs(xi1 - xi)

                    i_column.append(i)
                    xi_1_column.append(xi_1)
                    xi_column.append(xi)
                    fxi_1_column.append(fxi_1)
                    fxi_column.append(fxi)
                    xi1_column.append(xi1)
                    abs_error_column.append(abs_error)

                    if abs_error <= self.ep:
                        e_actual_less_e_allowed_column.append("sí")
                        table.add_row(
                            str(i),
                            str(xi_1),
                            str(xi),
                            str(fxi_1),
                            str(fxi),
                            str(xi1),
                            str(abs_error),
                            e_actual_less_e_allowed_column[-1],
                        )
                        self.update_screen()
                        self._console.print(table)
                        break

                    else:
                        e_actual_less_e_allowed_column.append("no")
                        table.add_row(
                            str(i),
                            str(xi_1),
                            str(xi),
                            str(fxi_1),
                            str(fxi),
                            str(xi1),
                            str(abs_error),
                            e_actual_less_e_allowed_column[-1],
                        )
                    i += 1
                    xi_1 = xi
                    xi = xi1

        self._console.save_html("table.html")
        self._plot_results(
            i_column,
            xi_1_column,
            xi_column,
            fxi_1_column,
            fxi_column,
            xi1_column,
            abs_error_column,
            e_actual_less_e_allowed_column,
        )
        self._console.print(
            "[blink cyan]All output was saved to table.html.[/blink cyan]",
            justify="center",
        )
        should_restart = self._console.input(
            "[purple italic]Restart? (y/n): [/purple italic]"
        )
        if should_restart.lower() == "y":
            next_method = SecantMethod()
            next_method.start()

    def find_starting_points(self) -> bool:
        """Solicita los dos puntos iniciales al usuario."""
        if self.equation_str == "":
            self.print_equation_empty()
            return False

        self.x0 = self._get_float_input(
            "[purple italic]Primer punto x0 <--- [/purple italic]"
        )
        self.x1 = self._get_float_input(
            "[purple italic]Segundo punto x1 <--- [/purple italic]"
        )
        self.update_screen(should_wait=True)
        return True

    def define_equation(
        self, equation_str: str = "", find_starting_points: bool = False
    ) -> bool:
        """Define la ecuación y, opcionalmente, encuentra los puntos iniciales."""
        if not equation_str:
            equation_str = self._console.input(
                "[purple italic]Ecuación --- [/purple italic]"
            )
        try:
            sp.sympify(equation_str)  # Validar la ecuación
            self.equation_str = equation_str
            self.update_screen()
        except (sp.SympifyError, TypeError):
            self._console.print("[red bold]Error: Ecuación inválida.[/red bold]")
            return False

        if not find_starting_points:
            answer = self._console.input(
                "[purple italic]¿Deseas ingresar los puntos iniciales? y/n <--- [/purple italic]"
            )
            if answer.lower() == "y":
                find_starting_points = True

        if find_starting_points:
            return self.find_starting_points()
        return True


class FixedPointMethod(BaseMethod):
    x0: float = 0.0  # Punto inicial
    g_equation_str: str = ""  # Ecuación g(x)
    last_g_equation_str: str = ""

    def redefine_data_in_screen(self) -> None:
        self._data_text = f"""
                                [cyan bold underline]-----Raíces de ecuaciones-----[/cyan bold underline]
                                [cyan bold frame]  ---Método de Punto Fijo---  [/cyan bold frame]
                                [yellow italic]f(x) = {sp.pretty(self.equation_str)}[/yellow italic]
                                [yellow italic]g(x) = {sp.pretty(self.g_equation_str)}[/yellow italic]
                                [blue italic]x0 = {self.x0}[/blue italic]
                                [red uu]error permitido = {self.ep}[/red uu]
                                """

    def _plot_results(
        self,
        column_i: list[int],
        column_xi: list[float],
        column_gxi: list[float],
        column_abs_error: list[float],
        column_eactual_less_eallowed: list[str],
    ) -> None:

        x = sp.symbols("x")
        equation = sp.sympify(self.equation_str)
        f = sp.lambdify(x, equation, "numpy")

        g_equation = sp.sympify(self.g_equation_str)
        g = sp.lambdify(x, g_equation, "numpy")

        # Calcular el rango para la gráfica, incluyendo margen
        min_x = min(column_xi) - 0.5
        max_x = max(column_xi) + 0.5

        # Puntos para graficar las funciones

        x_vals = np.linspace(min_x, max_x, 400)
        y_vals_f = f(x_vals)
        y_vals_g = g(x_vals)
        y_vals_line = x_vals  # Función identidad y = x

        # Crear la gráfica
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

        # Gráfica de f(x)
        ax1.plot(x_vals, y_vals_f, "b-", label="f(x)")  # Función original
        ax1.axhline(0, color="black", linewidth=0.8)  # Eje x
        ax1.axvline(0, color="black", linewidth=0.8)  # Eje y

        # Marcar los puntos convergentes en f(x)
        ax1.plot([column_xi[-1]], [f(column_xi[-1])], "ro", markersize=8, label="Raíz")
        ax1.axvline(
            column_xi[-1],
            color="red",
            linestyle="--",
            label=f"Raíz: {column_xi[-1]:.4f}",
        )

        ax1.set_xlabel("x")
        ax1.set_ylabel("f(x)")
        ax1.set_title("Función original f(x)")
        ax1.legend()
        ax1.grid(True)

        # Gráfica de g(x) vs y=x
        ax2.plot(x_vals, y_vals_g, "g-", label="g(x)")  # Función g(x)
        ax2.plot(x_vals, y_vals_line, "k--", label="y = x")  # Línea y = x
        ax2.axhline(0, color="black", linewidth=0.8)  # Eje x
        ax2.axvline(0, color="black", linewidth=0.8)  # Eje y

        # Mostrar iteraciones en la gráfica
        for i in range(len(column_xi) - 1):
            # Línea desde (xi, xi) hasta (xi, g(xi))
            ax2.plot(
                [column_xi[i], column_xi[i]],
                [column_xi[i], column_gxi[i]],
                "r-",
                alpha=0.3,
            )
            # Línea desde (xi, g(xi)) hasta (g(xi), g(xi))
            ax2.plot(
                [column_xi[i], column_gxi[i]],
                [column_gxi[i], column_gxi[i]],
                "r-",
                alpha=0.3,
            )
            # Punto (xi, g(xi))
            ax2.plot(
                column_xi[i],
                column_gxi[i],
                "bo",
                markersize=5,
                label="Iteraciones" if i == 0 else "",
            )

        # Marcar el punto de convergencia
        ax2.plot(
            column_xi[-1],
            column_gxi[-1],
            "ro",
            markersize=8,
            label=f"Punto fijo: {column_xi[-1]:.4f}",
        )

        ax2.set_xlabel("x")
        ax2.set_ylabel("g(x)")
        ax2.set_title("Método de Punto Fijo")
        ax2.legend()
        ax2.grid(True)

        plt.tight_layout()
        plt.show()

    def start(self) -> None:
        # NUEVO CÓDIGO: Algoritmo del Método de Punto Fijo
        if not self.equation_str:
            self._select_equation()

        # Solicitar la función g(x) si no está definida
        if self.g_equation_str == "":
            x = sp.symbols("x")
            try:
                equation = sp.sympify(self.equation_str)
            except (sp.SympifyError, TypeError):
                self._console.print(
                    "[red bold]Error: Ecuación f(x) inválida.[/red bold]"
                )
                return

            self._console.print(
                "[yellow]Necesitas definir una función g(x) para el método de punto fijo.[/yellow]"
            )
            self._console.print(
                "[yellow]La ecuación f(x) = 0 debe transformarse a x = g(x).[/yellow]"
            )

            g_equation_str = self._console.input(
                "[purple italic]Función g(x) --- [/purple italic]"
            )
            try:
                sp.sympify(g_equation_str)  # Validar g(x)
                self.g_equation_str = g_equation_str
                self.update_screen()  # Actualiza la pantalla con la nueva g(x)
            except (sp.SympifyError, TypeError):
                self._console.print(
                    "[red bold]Error: Función g(x) inválida.[/red bold]"
                )
                return

        # Solicitar el punto inicial x0
        if self.x0 == 0.0:
            self.x0 = self._get_float_input("[purple italic]Punto inicial x0 <--- [/]")

        # Solicitar el error permitido
        while self.ep == 0.0:
            self.ep = self._get_float_input(
                "[purple italic]Error permitido <--- [/]", min_value=0
            )

        # Crear el símbolo y las funciones
        x = sp.symbols("x")  # Corrección: se había cortado esta línea
        try:
            equation = sp.sympify(self.equation_str)
            f = sp.lambdify(x, equation, "numpy")

            g_equation = sp.sympify(self.g_equation_str)
            g = sp.lambdify(x, g_equation, "numpy")
        except (sp.SympifyError, TypeError) as e:
            self._console.print(
                f"[red bold]Error al procesar las ecuaciones: {e}[/red bold]"
            )
            return

        next_iteration = True

        # Listas para almacenar los datos
        i_column: list[int] = []
        xi_column: list[float] = []
        gxi_column: list[float] = []
        abs_error_column: list[float] = []
        e_actual_less_e_allowed_column: list[str] = []

        i = 1
        xi = self.x0

        # Crear la tabla
        table = Table(title="Método de Punto Fijo")
        table.add_column("Iteración")
        table.add_column("xi")
        table.add_column("g(xi)")
        table.add_column("|xi+1 - xi|")
        table.add_column("ea <= ep")

        while next_iteration:
            self.update_screen()

            # Calcular g(xi)
            try:
                gxi = g(xi)
            except (TypeError, ValueError) as e:
                self._console.print(f"[red bold]Error al evaluar g(x): {e}[/red bold]")
                return

            # Calcular el error absoluto
            if i > 1:
                abs_error = abs(gxi - xi)
            else:
                abs_error = float("inf")  # Primera iteración

            # Almacenar los valores
            i_column.append(i)
            xi_column.append(xi)
            gxi_column.append(gxi)
            abs_error_column.append(abs_error)

            # Verificar si se cumple el criterio de parada
            if abs_error <= self.ep:
                e_actual_less_e_allowed_column.append("sí")
            else:
                e_actual_less_e_allowed_column.append("no")

            # Agregar fila a la tabla
            table.add_row(
                str(i),
                str(xi),
                str(gxi),
                str(abs_error),
                e_actual_less_e_allowed_column[-1],
            )

            self._console.print(table)

            # Preparar la siguiente iteración
            xi = gxi
            i += 1

            # Preguntar si continuar
            answer = self._console.input(
                '[purple italic]Siguiente Iteración? y/n ("." to run until "sí") <--- '
            )
            if answer.lower() == "n":
                next_iteration = False

            if answer.lower() == ".":
                max_iterations = 100  # Evitar bucles infinitos
                while (
                    e_actual_less_e_allowed_column[-1] == "no" and i <= max_iterations
                ):
                    try:
                        gxi = g(xi)
                    except (TypeError, ValueError) as e:
                        self._console.print(
                            f"[red bold]Error al evaluar g(x): {e}[/red bold]"
                        )
                        return

                    abs_error = abs(gxi - xi)

                    i_column.append(i)
                    xi_column.append(xi)
                    gxi_column.append(gxi)
                    abs_error_column.append(abs_error)

                    if abs_error <= self.ep:
                        e_actual_less_e_allowed_column.append("sí")
                        table.add_row(str(i), str(xi), str(gxi), str(abs_error), "sí")
                        self.update_screen()
                        self._console.print(table)
                        break  # Sale del while
                    else:
                        e_actual_less_e_allowed_column.append("no")
                        table.add_row(str(i), str(xi), str(gxi), str(abs_error), "no")

                    if abs_error > 1e5 or np.isnan(abs_error) or np.isinf(abs_error):
                        self._console.print(
                            "[bold red]El método parece estar divergiendo. Se detuvo la ejecución.[/bold red]"
                        )
                        break

                    xi = gxi
                    i += 1
                next_iteration = False

        self._console.save_html("table.html")
        self._plot_results(
            i_column,
            xi_column,
            gxi_column,
            abs_error_column,
            e_actual_less_e_allowed_column,
        )
        self._console.print(
            "[blink cyan]All output was saved to table.html.[/blink cyan]",
            justify="center",
        )
        should_restart = self._console.input(
            "[purple italic]Restart? (y/n): [/purple italic]"
        )
        if should_restart.lower() == "y":
            next_method = FixedPointMethod()
            next_method.start()

    def define_equation(
        self,
        equation_str: str = "",
        g_equation_str: str = "",
        find_starting_point: bool = False,
    ) -> bool:
        """Define la ecuación f(x) y g(x), y opcionalmente el punto inicial."""

        if not equation_str:
            equation_str = self._console.input(
                "[purple italic]Ecuación f(x) = 0 --- [/purple italic]"
            )
        try:
            sp.sympify(equation_str)  # Validar f(x)
            self.equation_str = equation_str
            self.update_screen()
        except (sp.SympifyError, TypeError):
            self._console.print("[red bold]Error: Ecuación f(x) inválida.[/red bold]")
            return False

        if not g_equation_str:
            self._console.print(
                "[yellow]Para el método de punto fijo, debes transformar f(x) = 0 a x = g(x)[/yellow]"
            )
            g_equation_str = self._console.input(
                "[purple italic]Función g(x) --- [/purple italic]"
            )
        try:
            sp.sympify(g_equation_str)  # Validar g(x)
            self.g_equation_str = g_equation_str
            self.update_screen()
        except (sp.SympifyError, TypeError):
            self._console.print("[red bold]Error: Función g(x) inválida.[/red bold]")
            return False

        if not find_starting_point:
            answer = self._console.input(
                "[purple italic]¿Deseas ingresar un punto inicial? y/n <--- [/purple italic]"
            )
            if answer.lower() == "y":
                find_starting_point = True

        if find_starting_point:
            self.x0 = self._get_float_input(
                "[purple italic]Punto inicial x0 <--- [/purple italic]"
            )
            self.update_screen()  # Actualiza para mostrar el x0
        return True
