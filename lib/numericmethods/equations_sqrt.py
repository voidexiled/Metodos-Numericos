from os import system
import numpy as np
import sympy as sp
from matplotlib import pyplot as plt
from rich.console import Console
from rich.table import Table
from time import sleep

console = Console()


def determinar_intervalo(
    equation_str: str, x_min: int = -10, x_max: int = 10, delta_x=0.1
):

    x = sp.symbols("x")

    equation = sp.sympify(equation_str)

    f = sp.lambdify(x, equation, "numpy")

    a: int | float | None = None
    b: int | float | None = None
    x_current = x_min

    while x_current < x_max:
        f_x_current = f(x_current)
        f_x_next = f(x_current + delta_x)

        if f_x_current * f_x_next < 0:
            a, b = x_current, x_current + delta_x
            break

        x_current += delta_x

    if a is not None and b is not None:
        console.print(
            f"[bold green]Intervalo Encontrado:[/bold green] [blue]a = {a}[/blue][green],[/green] [red]b = {b}[/red]"
        )
        # print(f"Intervalo encontrado: a = {a}, b = {b}")
        return a, b
    else:
        console.print(
            "[bold red] no se encontró un intervalo con cambio de signo en el rango especificado.[/bold red]"
        )
        return None, None


class BisectMethod:
    x_min: float = -10
    x_max: float = 10
    delta_x: float = 0.1
    equation_str: str = ""
    a: float = 0
    b: float = 0
    ep: float = 0

    last_equation_str: str = equation_str

    def showEcuationPlot(self):
        if self.last_equation_str != self.equation_str:
            if self.equation_str != "":
                plt.close("all")
                equation = sp.sympify(self.equation_str)
                latex_str = sp.latex(equation)
                plt.figure(figsize=(6, 2))
                plt.text(0.1, 0.5, f"${latex_str}$").set_fontsize(20)
                plt.axis("off")
                plt.show(block=False)
                self.last_equation_str = self.equation_str

    def __init__(self):
        self.__console = Console(record=True)
        self.__data_text = ""
        self.updateScreen()

    def updateScreen(self, shouldWait: bool = False, waitSeconds: float | int = 0.5):
        self.redefineDataInScreen()
        if shouldWait:
            max_ms_sleep: float | int = 10.0
            ms_to_sleep = waitSeconds > max_ms_sleep and max_ms_sleep or waitSeconds
            sleep(ms_to_sleep)
        system("cls")
        self.__console.print(self.__data_text)
        self.showEcuationPlot()

    def redefineDataInScreen(self):
        self.__data_text = f"""
                                [cyan bold underline]-----Raíces de ecuaciones-----[/cyan bold underline]
                                [cyan bold frame]  ---Método de Bisección---  [/cyan bold frame]
                                [yellow italic]{sp.pretty(self.equation_str)}[/yellow italic]
                                [blue italic]a = {self.a}[/blue italic]
                                [red italic]b = {self.b}[/red italic]
                                [red uu]error permitido = {self.ep}[/red uu]
                                """

    def printEquationEmpty(self, try_to_define=False):
        self.__console.print(
            f"\n[red bold][u]No hay una ecuación definida.[/u][/red bold]"
        )
        if try_to_define:
            self.defineEquation()

    def __plotResults(
        self,
        column_i: list,
        column_a: list,
        column_b: list,
        column_f_a: list,
        column_f_b: list,
        column_xi: list,
        column_f_xi: list,
        column_abs_f_xi: list,
        column_eactual_less_eallowed: list,
    ):
        x = sp.symbols("x")
        equation = sp.sympify(self.equation_str)
        f = sp.lambdify(x, equation, "numpy")

        # Puntos para graficar la función
        x = np.linspace(self.a - 0.5, self.b + 0.5, 400)
        y = f(x)

        # Crear la gráfica
        plt.figure(figsize=(8, 6))
        plt.plot(x, y, "b-", label="f(x)")  # Función
        plt.axhline(0, color="black", linewidth=0.8)  # Eje x
        plt.axvline(0, color="black", linewidth=0.8)  # Eje y

        # Marcar los puntos a, b, y xm
        plt.plot(column_a, column_f_a, "ro", label="f(a)")
        plt.plot(column_b, column_f_b, "ro", label="f(b)")
        plt.plot(column_xi, column_f_xi, "ro", label="f(xi)")
        plt.axvline(column_a[-1], color="red", linestyle="--")
        plt.axvline(column_b[-1], color="red", linestyle="--")
        plt.axvline(column_xi[-1], color="black", linestyle="--")

        plt.axhline(
            column_f_a[-1], color="red", linestyle="--"
        )  # Último valor de 'f(a)'
        plt.axhline(
            column_f_b[-1], color="red", linestyle="--"
        )  # Último valor de 'f(b)'

        # Etiquetas y título
        plt.xlabel("x")
        plt.ylabel("f(x)")
        plt.title("Método de Bisección")
        plt.legend()
        plt.grid(True)

        # Mostrar la gráfica
        plt.show()

    def start(self):
        while self.equation_str == "":
            self.printEquationEmpty(try_to_define=True)
        while self.ep == None or type(self.ep) is not float or self.ep <= 0:
            try:
                self.ep = float(
                    self.__console.input("[purple italic]Error permitido <--- [/]")
                )
            except ValueError as e:
                self.__console.print(e)

        x = sp.symbols("x")
        equation = sp.sympify(self.equation_str)
        f = sp.lambdify(x, equation, "numpy")

        nextIteration = True

        i_column = []
        a_column = []
        b_column = []
        fa_column = []
        fb_column = []
        xi_column = []
        f_xi_column = []
        abs_f_xi_column = []
        e_actual_less_e_allowed_column = []

        i = 1
        a = self.a
        b = self.b
        fa = f(a)
        fb = f(b)

        table = Table(title="Bisección")
        table.add_column("Iteración")
        table.add_column("a", width=100)
        table.add_column("b", width=100)
        table.add_column("f(a)", width=100)
        table.add_column("f(b)", width=100)
        table.add_column("xi", width=100)
        table.add_column("f(xi)", width=100)
        table.add_column("abs(f(xi))", width=100)
        table.add_column("ea <= ep", width=100)

        while nextIteration:
            self.updateScreen()

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

            self.__console.print(table)
            i += 1

            answer = console.input(
                '[purple italic]Siguiente Iteración? y/n ("." to run until "sí") <--- '
            )

            if answer.lower() == "n":
                nextIteration = False

            if answer.lower() == ".":
                pass  # TODO

        self.__console.save_html("table.html")
        self.__plotResults(
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
        self.__console.print(
            "[blink cyan]All output was saved to table.html.[/blink cyan]",
            justify="center",
        )
        should_restart = self.__console.input(
            "[purple italic]Restart? (y/n): [/purple italic]"
        )
        if should_restart:
            next_bisect = BisectMethod()
            next_bisect.start()

    def findAB(self, x_min: int = 0, x_max: int = 0, delta_x: float | int = delta_x):
        if delta_x <= 0:
            self.__console.print(
                "[bold red][u]delta_x[/u][/bold red][red] debe ser mayor que [bold][u]0[/u][/bold][/red] "
            )
            return None
        if self.equation_str == "":
            self.printEquationEmpty()
            self.x_min, self.x_max, self.delta_x = x_min, x_max, delta_x
            return self.defineEquation(thenFindAB=True)

        if x_min == 0 or x_max == 0:
            self.__console.print(
                "[purple italic]Buscar intervalos desde: [/purple italic]"
            )
            x_min = int(
                console.input("[purple italic]Limite inferior <--- [/purple italic]")
            )
            x_max = int(
                console.input("[purple italic]Limite superior <--- [/purple italic]")
            )

        a, b = determinar_intervalo(self.equation_str)
        if a is not None and b is not None:
            self.a = a
            self.b = b
        else:
            self.__console.print(
                "[bold red]Error: 'a' or 'b' could not be determined[/bold red]"
            )
            return None
        self.updateScreen(shouldWait=True)
        return True

    def defineEquation(self, equation_str: str = "", thenFindAB: bool = False):
        while equation_str == "" or type(equation_str) is not str:
            equation_str = console.input("[purple italic]Ecuación --- [/purple italic]")
        self.equation_str = equation_str
        self.updateScreen()
        if not thenFindAB:
            answer = console.input(
                "[purple italic]Deseas que busque 'a' y 'b' automáticamente? y/n <--- [/purple italic]"
            )
            if answer.lower() == "y":
                thenFindAB = True
        if thenFindAB:
            return self.findAB()
        else:
            self.a = int(console.input("[purple italic]A <--- [/purple italic]"))
            self.b = int(console.input("[purple italic]B <--- [/purple italic]"))
            self.updateScreen()
        return True


class FakePositionMethod:
    # NUEVO CÓDIGO: Implementación del Método de Falsa Posición
    x_min: float = -10
    x_max: float = 10
    delta_x: float = 0.1
    equation_str: str = ""
    a: float = 0
    b: float = 0
    ep: float = 0

    last_equation_str: str = equation_str

    def showEcuationPlot(self):
        if self.last_equation_str != self.equation_str:
            if self.equation_str != "":
                plt.close("all")
                equation = sp.sympify(self.equation_str)
                latex_str = sp.latex(equation)
                plt.figure(figsize=(6, 2))
                plt.text(0.1, 0.5, f"${latex_str}$").set_fontsize(20)
                plt.axis("off")
                plt.show(block=False)
                self.last_equation_str = self.equation_str

    def __init__(self):
        self.__console = Console(record=True)
        self.__data_text = ""
        self.updateScreen()

    def updateScreen(self, shouldWait: bool = False, waitSeconds: float | int = 0.5):
        self.redefineDataInScreen()
        if shouldWait:
            max_ms_sleep: float | int = 10.0
            ms_to_sleep = waitSeconds > max_ms_sleep and max_ms_sleep or waitSeconds
            sleep(ms_to_sleep)
        system("cls")
        self.__console.print(self.__data_text)
        self.showEcuationPlot()

    def redefineDataInScreen(self):
        self.__data_text = f"""
                                [cyan bold underline]-----Raíces de ecuaciones-----[/cyan bold underline]
                                [cyan bold frame]  ---Método de Falsa Posición---  [/cyan bold frame]
                                [yellow italic]{sp.pretty(self.equation_str)}[/yellow italic]
                                [blue italic]a = {self.a}[/blue italic]
                                [red italic]b = {self.b}[/red italic]
                                [red uu]error permitido = {self.ep}[/red uu]
                                """

    def printEquationEmpty(self, try_to_define=False):
        self.__console.print(
            f"\n[red bold][u]No hay una ecuación definida.[/u][/red bold]"
        )
        if try_to_define:
            self.defineEquation()

    def __plotResults(
        self,
        column_i: list,
        column_a: list,
        column_b: list,
        column_f_a: list,
        column_f_b: list,
        column_xi: list,
        column_f_xi: list,
        column_abs_f_xi: list,
        column_eactual_less_eallowed: list,
    ):
        x = sp.symbols("x")
        equation = sp.sympify(self.equation_str)
        f = sp.lambdify(x, equation, "numpy")

        # Puntos para graficar la función
        x = np.linspace(self.a - 0.5, self.b + 0.5, 400)
        y = f(x)

        # Crear la gráfica
        plt.figure(figsize=(8, 6))
        plt.plot(x, y, "b-", label="f(x)")  # Función
        plt.axhline(0, color="black", linewidth=0.8)  # Eje x
        plt.axvline(0, color="black", linewidth=0.8)  # Eje y

        # Marcar los puntos a, b, y xi
        plt.plot(column_a, column_f_a, "ro", label="f(a)")
        plt.plot(column_b, column_f_b, "ro", label="f(b)")
        plt.plot(column_xi, column_f_xi, "go", label="f(xi)")
        plt.axvline(column_a[-1], color="red", linestyle="--")
        plt.axvline(column_b[-1], color="red", linestyle="--")
        plt.axvline(column_xi[-1], color="green", linestyle="--")

        plt.axhline(
            column_f_a[-1], color="red", linestyle="--"
        )  # Último valor de 'f(a)'
        plt.axhline(
            column_f_b[-1], color="red", linestyle="--"
        )  # Último valor de 'f(b)'

        # Etiquetas y título
        plt.xlabel("x")
        plt.ylabel("f(x)")
        plt.title("Método de Falsa Posición")
        plt.legend()
        plt.grid(True)

        # Mostrar la gráfica
        plt.show()

    def start(self):
        # NUEVO CÓDIGO: Algoritmo de Falsa Posición
        while self.equation_str == "":
            self.printEquationEmpty(try_to_define=True)
        while self.ep == None or type(self.ep) is not float or self.ep <= 0:
            try:
                self.ep = float(
                    self.__console.input("[purple italic]Error permitido <--- [/]")
                )
            except ValueError as e:
                self.__console.print(e)

        x = sp.symbols("x")
        equation = sp.sympify(self.equation_str)
        f = sp.lambdify(x, equation, "numpy")

        nextIteration = True

        i_column = []
        a_column = []
        b_column = []
        fa_column = []
        fb_column = []
        xi_column = []
        f_xi_column = []
        abs_f_xi_column = []
        e_actual_less_e_allowed_column = []

        i = 1
        a = self.a
        b = self.b
        fa = f(a)
        fb = f(b)

        table = Table(title="Falsa Posición")
        table.add_column("Iteración")
        table.add_column("a", width=100)
        table.add_column("b", width=100)
        table.add_column("f(a)", width=100)
        table.add_column("f(b)", width=100)
        table.add_column("xi", width=100)
        table.add_column("f(xi)", width=100)
        table.add_column("abs(f(xi))", width=100)
        table.add_column("ea <= ep", width=100)

        while nextIteration:
            self.updateScreen()

            # Calcular xi usando la fórmula de falsa posición
            # xi = a - (f(a) * (b - a)) / (f(b) - f(a))
            if i >= 2:
                last_f_xi = f_xi_column[i - 2]
                last_fa = fa_column[i - 2]
                last_fb = fb_column[i - 2]

                # Determinar qué intervalo preservar
                if last_f_xi * last_fa < 0:
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

            self.__console.print(table)
            i += 1

            answer = console.input(
                '[purple italic]Siguiente Iteración? y/n ("." to run until "sí") <--- '
            )

            if answer.lower() == "n":
                nextIteration = False
            
            if answer.lower() == ".":
                # Si el usuario quiere ejecutar hasta encontrar la solución
                while e_actual_less_e_allowed_column[-1] == "no":
                    # Determinar qué intervalo preservar
                    if f_xi_column[-1] * f(a) < 0:
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
                    
                    # Fórmula de falsa posición
                    xi = a - (fa * (b - a)) / (fb - fa)
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
                        self.updateScreen()
                        self.__console.print(table)
                        nextIteration = False
                        break
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
                    
                self.updateScreen()
                self.__console.print(table)

        self.__console.save_html("table.html")
        self.__plotResults(
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
        self.__console.print(
            "[blink cyan]All output was saved to table.html.[/blink cyan]",
            justify="center",
        )
        should_restart = self.__console.input(
            "[purple italic]Restart? (y/n): [/purple italic]"
        )
        if should_restart.lower() == "y":
            next_method = FakePositionMethod()
            next_method.start()

# NUEVO CÓDIGO: Implementación del Método de Newton-Raphson
class NewtonRaphsonMethod:
    x_min: float = -10
    x_max: float = 10
    delta_x: float = 0.1
    equation_str: str = ""
    x0: float = 0  # Punto inicial
    ep: float = 0  # Error permitido
    
    last_equation_str: str = equation_str

    def showEcuationPlot(self):
        if self.last_equation_str != self.equation_str:
            if self.equation_str != "":
                plt.close("all")
                equation = sp.sympify(self.equation_str)
                latex_str = sp.latex(equation)
                plt.figure(figsize=(6, 2))
                plt.text(0.1, 0.5, f"${latex_str}$").set_fontsize(20)
                plt.axis("off")
                plt.show(block=False)
                self.last_equation_str = self.equation_str

    def __init__(self):
        self.__console = Console(record=True)
        self.__data_text = ""
        self.updateScreen()

    def updateScreen(self, shouldWait: bool = False, waitSeconds: float | int = 0.5):
        self.redefineDataInScreen()
        if shouldWait:
            max_ms_sleep: float | int = 10.0
            ms_to_sleep = waitSeconds > max_ms_sleep and max_ms_sleep or waitSeconds
            sleep(ms_to_sleep)
        system("cls")
        self.__console.print(self.__data_text)
        self.showEcuationPlot()

    def redefineDataInScreen(self):
        self.__data_text = f"""
                                [cyan bold underline]-----Raíces de ecuaciones-----[/cyan bold underline]
                                [cyan bold frame]  ---Método de Newton-Raphson---  [/cyan bold frame]
                                [yellow italic]{sp.pretty(self.equation_str)}[/yellow italic]
                                [blue italic]x0 = {self.x0}[/blue italic]
                                [red uu]error permitido = {self.ep}[/red uu]
                                """

    def printEquationEmpty(self, try_to_define=False):
        self.__console.print(
            f"\n[red bold][u]No hay una ecuación definida.[/u][/red bold]"
        )
        if try_to_define:
            self.defineEquation()

    def __plotResults(
        self,
        column_i: list,
        column_xi: list,
        column_fxi: list,
        column_dxi: list,
        column_dfxi: list,
        column_xi1: list,
        column_abs_error: list,
        column_eactual_less_eallowed: list,
    ):
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
        last_fxi = column_fxi[-1]
        
        # Marcar los puntos xi, rectas tangentes
        for i in range(len(column_xi)):
            plt.plot(column_xi[i], column_fxi[i], "ro")
            
            # Si no es el último punto, graficar la recta tangente
            if i < len(column_xi) - 1:
                # Graficar un segmento de recta tangente
                x_tangent = np.linspace(column_xi[i] - 0.5, column_xi[i] + 0.5, 2)
                y_tangent = column_dfxi[i] * (x_tangent - column_xi[i]) + column_fxi[i]
                plt.plot(x_tangent, y_tangent, "g--", alpha=0.5)
                
                # Marcar el punto donde la tangente cruza el eje x
                plt.plot(column_xi1[i], 0, "gx")
                
        # Marcar el último punto con una línea vertical
        plt.axvline(last_xi, color="red", linestyle="--")
        
        # Etiquetas y título
        plt.xlabel("x")
        plt.ylabel("f(x)")
        plt.title("Método de Newton-Raphson")
        plt.legend()
        plt.grid(True)
        
        # Mostrar la gráfica
        plt.show()

    def start(self):
        # NUEVO CÓDIGO: Algoritmo de Newton-Raphson
        while self.equation_str == "":
            self.printEquationEmpty(try_to_define=True)
            
        # Solicitar el punto inicial x0 si no está definido
        if self.x0 == 0:
            try:
                self.x0 = float(
                    self.__console.input("[purple italic]Punto inicial x0 <--- [/]")
                )
            except ValueError as e:
                self.__console.print(e)
                return
                
        # Solicitar el error permitido
        while self.ep == None or type(self.ep) is not float or self.ep <= 0:
            try:
                self.ep = float(
                    self.__console.input("[purple italic]Error permitido <--- [/]")
                )
            except ValueError as e:
                self.__console.print(e)

        # Crear el símbolo y la ecuación
        x = sp.symbols("x")
        equation = sp.sympify(self.equation_str)
        f = sp.lambdify(x, equation, "numpy")
        
        # Calcular la derivada
        derivative = sp.diff(equation, x)
        df = sp.lambdify(x, derivative, "numpy")
        
        # Mostrar la derivada
        self.__console.print(f"[cyan]Derivada: {derivative}[/cyan]")
        
        nextIteration = True
        
        # Columnas para almacenar los datos
        i_column = []
        xi_column = []
        fxi_column = []
        dxi_column = []  # Derivada en xi
        dfxi_column = []  # Valor de la derivada en xi
        xi1_column = []  # Siguiente valor de x
        abs_error_column = []  # Error absoluto
        e_actual_less_e_allowed_column = []  # ¿Error actual <= Error permitido?
        
        i = 1
        xi = self.x0
        
        # Crear tabla para mostrar resultados
        table = Table(title="Newton-Raphson")
        table.add_column("Iteración")
        table.add_column("xi", width=100)
        table.add_column("f(xi)", width=100)
        table.add_column("f'(xi)", width=100)
        table.add_column("xi+1", width=100)
        table.add_column("|xi+1 - xi|", width=100)
        table.add_column("ea <= ep", width=100)
        
        while nextIteration:
            self.updateScreen()
            
            # Calcular los valores para esta iteración
            fxi = f(xi)
            dfxi = df(xi)
            
            # Evitar división por cero
            if abs(dfxi) < 1e-10:
                self.__console.print("[bold red]Error: Derivada muy cercana a cero. División por cero.[/bold red]")
                break
                
            # Fórmula de Newton-Raphson: xi+1 = xi - f(xi)/f'(xi)
            xi1 = xi - fxi / dfxi
            
            # Calcular el error absoluto
            abs_error = abs(xi1 - xi)
            
            # Almacenar los valores calculados
            i_column.append(i)
            xi_column.append(xi)
            fxi_column.append(fxi)
            dxi_column.append(derivative)
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
            self.__console.print(table)
            
            # Preparar para la siguiente iteración
            xi = xi1
            i += 1
            
            # Preguntar si continuar
            answer = console.input(
                '[purple italic]Siguiente Iteración? y/n ("." to run until "sí") <--- '
            )
            
            if answer.lower() == "n":
                nextIteration = False
                
            if answer.lower() == ".":
                # Ejecutar hasta encontrar la solución
                while e_actual_less_e_allowed_column[-1] == "no":
                    # Calcular los valores para esta iteración
                    fxi = f(xi)
                    dfxi = df(xi)
                    
                    # Evitar división por cero
                    if abs(dfxi) < 1e-10:
                        self.__console.print("[bold red]Error: Derivada muy cercana a cero. División por cero.[/bold red]")
                        break
                        
                    # Fórmula de Newton-Raphson: xi+1 = xi - f(xi)/f'(xi)
                    xi1 = xi - fxi / dfxi
                    
                    # Calcular el error absoluto
                    abs_error = abs(xi1 - xi)
                    
                    # Almacenar los valores calculados
                    i_column.append(i)
                    xi_column.append(xi)
                    fxi_column.append(fxi)
                    dxi_column.append(derivative)
                    dfxi_column.append(dfxi)
                    xi1_column.append(xi1)
                    abs_error_column.append(abs_error)
                    
                    # Verificar si el error es menor o igual al permitido
                    if abs_error <= self.ep:
                        e_actual_less_e_allowed_column.append("sí")
                        # Agregar la última fila a la tabla
                        table.add_row(
                            str(i),
                            str(xi),
                            str(fxi),
                            str(dfxi),
                            str(xi1),
                            str(abs_error),
                            e_actual_less_e_allowed_column[-1],
                        )
                        self.updateScreen()
                        self.__console.print(table)
                        break
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
                    
                    # Preparar para la siguiente iteración
                    xi = xi1
                    i += 1
                    
                self.updateScreen()
                self.__console.print(table)
                nextIteration = False
                
        # Guardar resultados y mostrar gráfica
        self.__console.save_html("table.html")
        self.__plotResults(
            i_column,
            xi_column,
            fxi_column,
            dxi_column,
            dfxi_column,
            xi1_column,
            abs_error_column,
            e_actual_less_e_allowed_column,
        )
        self.__console.print(
            "[blink cyan]All output was saved to table.html.[/blink cyan]",
            justify="center",
        )
        should_restart = self.__console.input(
            "[purple italic]Restart? (y/n): [/purple italic]"
        )
        if should_restart.lower() == "y":
            next_method = NewtonRaphsonMethod()
            next_method.start()

    def findStartingPoint(self):
        # NUEVO CÓDIGO: Buscar un punto inicial adecuado
        if self.equation_str == "":
            self.printEquationEmpty()
            return None
            
        try:
            self.x0 = float(
                console.input("[purple italic]Punto inicial x0 <--- [/purple italic]")
            )
            self.updateScreen(shouldWait=True)
            return True
        except ValueError:
            self.__console.print(
                "[bold red]Error: El valor ingresado no es un número válido[/bold red]"
            )
            return None

    def defineEquation(self, equation_str: str = "", findStartingPoint: bool = False):
        # NUEVO CÓDIGO: Definir la ecuación
        while equation_str == "" or type(equation_str) is not str:
            equation_str = console.input("[purple italic]Ecuación --- [/purple italic]")
        self.equation_str = equation_str
        self.updateScreen()
        
        if not findStartingPoint:
            answer = console.input(
                "[purple italic]¿Deseas ingresar un punto inicial? y/n <--- [/purple italic]"
            )
            if answer.lower() == "y":
                findStartingPoint = True
        if findStartingPoint:
            return self.findStartingPoint()
        return True


# NUEVO CÓDIGO: Implementación del Método de la Secante
class SecantMethod:
    x_min: float = -10
    x_max: float = 10
    delta_x: float = 0.1
    equation_str: str = ""
    x0: float = 0  # Primer punto
    x1: float = 0  # Segundo punto
    ep: float = 0  # Error permitido
    
    last_equation_str: str = equation_str

    def showEcuationPlot(self):
        if self.last_equation_str != self.equation_str:
            if self.equation_str != "":
                plt.close("all")
                equation = sp.sympify(self.equation_str)
                latex_str = sp.latex(equation)
                plt.figure(figsize=(6, 2))
                plt.text(0.1, 0.5, f"${latex_str}$").set_fontsize(20)
                plt.axis("off")
                plt.show(block=False)
                self.last_equation_str = self.equation_str

    def __init__(self):
        self.__console = Console(record=True)
        self.__data_text = ""
        self.updateScreen()

    def updateScreen(self, shouldWait: bool = False, waitSeconds: float | int = 0.5):
        self.redefineDataInScreen()
        if shouldWait:
            max_ms_sleep: float | int = 10.0
            ms_to_sleep = waitSeconds > max_ms_sleep and max_ms_sleep or waitSeconds
            sleep(ms_to_sleep)
        system("cls")
        self.__console.print(self.__data_text)
        self.showEcuationPlot()

    def redefineDataInScreen(self):
        self.__data_text = f"""
                                [cyan bold underline]-----Raíces de ecuaciones-----[/cyan bold underline]
                                [cyan bold frame]  ---Método de la Secante---  [/cyan bold frame]
                                [yellow italic]{sp.pretty(self.equation_str)}[/yellow italic]
                                [blue italic]x0 = {self.x0}[/blue italic]
                                [blue italic]x1 = {self.x1}[/blue italic]
                                [red uu]error permitido = {self.ep}[/red uu]
                                """

    def printEquationEmpty(self, try_to_define=False):
        self.__console.print(
            f"\n[red bold][u]No hay una ecuación definida.[/u][/red bold]"
        )
        if try_to_define:
            self.defineEquation()

    def __plotResults(
        self,
        column_i: list,
        column_xi_1: list,
        column_xi: list,
        column_fxi_1: list,
        column_fxi: list,
        column_xi1: list,
        column_abs_error: list,
        column_eactual_less_eallowed: list,
    ):
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
            plt.plot(column_xi_1[i], column_fxi_1[i], "ro")
            plt.plot(column_xi[i], column_fxi[i], "ro")
            
            # Graficar la secante
            secant_x = np.array([column_xi_1[i], column_xi[i]])
            secant_y = np.array([column_fxi_1[i], column_fxi[i]])
            plt.plot(secant_x, secant_y, "g--", alpha=0.5)
            
            # Marcar el punto donde la secante cruza el eje x
            plt.plot(column_xi1[i], 0, "gx")
        
        # Marcar el último punto xi+1 con una línea vertical
        plt.axvline(column_xi1[-1], color="red", linestyle="--")
        
        # Etiquetas y título
        plt.xlabel("x")
        plt.ylabel("f(x)")
        plt.title("Método de la Secante")
        plt.legend()
        plt.grid(True)
        
        # Mostrar la gráfica
        plt.show()

    def __plotResults(
        self,
        column_i: list,
        column_xi: list,
        column_gxi: list,
        column_abs_error: list,
        column_eactual_less_eallowed: list,
    ):
        # NUEVO CÓDIGO: Graficar resultados
        x = sp.symbols("x")
        equation = sp.sympify(self.equation_str)
        f = sp.lambdify(x, equation, "numpy")
        
        g_equation = sp.sympify(self.g_equation_str)
        g = sp.lambdify(x, g_equation, "numpy")
        
        # Calcular el rango para la gráfica
        min_x = min(column_xi) - 1
        max_x = max(column_xi) + 1
        
        # Puntos para graficar la función
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
        ax1.axvline(column_xi[-1], color="red", linestyle="--")
        
        ax1.set_xlabel("x")
        ax1.set_ylabel("f(x)")
        ax1.set_title("Función original f(x)")
        ax1.legend()
        ax1.grid(True)
        
        # Gráfica de g(x) vs y=x
        ax2.plot(x_vals, y_vals_g, "b-", label="g(x)")  # Función de punto fijo
        ax2.plot(x_vals, y_vals_line, "k--", label="y = x")  # Función identidad
        ax2.axhline(0, color="black", linewidth=0.8)  # Eje x
        ax2.axvline(0, color="black", linewidth=0.8)  # Eje y
        
        # Marcar iteraciones
        for i in range(len(column_xi) - 1):
            # Líneas del método gráfico punto fijo
            ax2.plot([column_xi[i], column_xi[i]], [column_xi[i], column_gxi[i]], 'g-', alpha=0.5)
            ax2.plot([column_xi[i], column_gxi[i]], [column_gxi[i], column_gxi[i]], 'g-', alpha=0.5)
            # Puntos
            ax2.plot([column_xi[i]], [column_xi[i]], 'go')
            ax2.plot([column_xi[i]], [column_gxi[i]], 'ro')
        
        # Marcar punto convergente
        ax2.plot([column_xi[-1]], [column_xi[-1]], 'ro', markersize=8, label="Punto fijo")
        
        ax2.set_xlabel("x")
        ax2.set_ylabel("g(x)")
        ax2.set_title("Método de Punto Fijo: g(x) vs y=x")
        ax2.legend()
        ax2.grid(True)
        
        plt.tight_layout()
        plt.show()

    def start(self):
        # NUEVO CÓDIGO: Algoritmo del Método de Punto Fijo
        while self.equation_str == "":
            self.printEquationEmpty(try_to_define=True)
            
        # Solicitar la función g(x) si no está definida
        if self.g_equation_str == "":
            x = sp.symbols("x")
            equation = sp.sympify(self.equation_str)
            
            self.__console.print("[yellow]Necesitas definir una función g(x) para el método de punto fijo.[/yellow]")
            self.__console.print("[yellow]La ecuación f(x) = 0 debe transformarse a x = g(x).[/yellow]")
            
            g_equation_str = console.input("[purple italic]Función g(x) --- [/purple italic]")
            self.g_equation_str = g_equation_str
        
        # Solicitar el punto inicial x0 si no está definido
        if self.x0 == 0:
            try:
                self.x0 = float(
                    self.__console.input("[purple italic]Punto inicial x0 <--- [/]")
                )
            except ValueError as e:
                self.__console.print(e)
                return
                
        # Solicitar el error permitido
        while self.ep == None or type(self.ep) is not float or self.ep <= 0:
            try:
                self.ep = float(
                    self.__console.input("[purple italic]Error permitido <--- [/]")
                )
            except ValueError as e:
                self.__console.print(e)

        # Crear el símbolo y las funciones
        x = sp.symbols("x")
        equation = sp.sympify(self.equation_str)
        f = sp.lambdify(x, equation, "numpy")
        
        g_equation = sp.sympify(self.g_equation_str)
        g = sp.lambdify(x, g_equation, "numpy")
        
        nextIteration = True
        
        # Columnas para almacenar los datos
        i_column = []
        xi_column = []
        gxi_column = []
        abs_error_column = []
        e_actual_less_e_allowed_column = []
        
        i = 1
        xi = self.x0
        
        # Crear tabla para mostrar resultados
        table = Table(title="Método de Punto Fijo")
        table.add_column("Iteración")
        table.add_column("xi", width=100)
        table.add_column("g(xi)", width=100)
        table.add_column("|xi+1 - xi|", width=100)
        table.add_column("ea <= ep", width=100)
        
        while nextIteration:
            self.updateScreen()
            
            # Calcular g(xi)
            gxi = g(xi)
            
            # Calcular el error absoluto
            if i > 1:
                abs_error = abs(gxi - xi)
            else:
                abs_error = float('inf')  # En la primera iteración no hay error previo
            
            # Almacenar los valores calculados
            i_column.append(i)
            xi_column.append(xi)
            gxi_column.append(gxi)
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
                str(gxi),
                str(abs_error),
                e_actual_less_e_allowed_column[-1],
            )
            
            # Mostrar la tabla
            self.__console.print(table)
            
            # Preparar para la siguiente iteración
            xi = gxi
            i += 1
            
            # Preguntar si continuar
            answer = console.input(
                '[purple italic]Siguiente Iteración? y/n ("." to run until "sí") <--- '
            )
            
            if answer.lower() == "n":
                nextIteration = False
                
            if answer.lower() == ".":
                # Ejecutar hasta encontrar la solución o diverger
                max_iterations = 100  # Límite para evitar bucles infinitos
                iterations_count = 0
                
                while e_actual_less_e_allowed_column[-1] == "no" and iterations_count < max_iterations:
                    # Calcular g(xi)
                    gxi = g(xi)
                    
                    # Calcular el error absoluto
                    abs_error = abs(gxi - xi)
                    
                    # Almacenar los valores calculados
                    i_column.append(i)
                    xi_column.append(xi)
                    gxi_column.append(gxi)
                    abs_error_column.append(abs_error)
                    
                    # Verificar si el error es menor o igual al permitido
                    if abs_error <= self.ep:
                        e_actual_less_e_allowed_column.append("sí")
                        # Agregar la última fila a la tabla
                        table.add_row(
                            str(i),
                            str(xi),
                            str(gxi),
                            str(abs_error),
                            e_actual_less_e_allowed_column[-1],
                        )
                        self.updateScreen()
                        self.__console.print(table)
                        break
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
                    
                    # Preparar para la siguiente iteración
                    xi = gxi
                    i += 1
                    iterations_count += 1
                    
                    # Verificar si la secuencia parece diverger
                    if abs_error > 1e5 or np.isnan(abs_error) or np.isinf(abs_error):
                        self.__console.print("[bold red]El método parece estar divergiendo. Se detuvo la ejecución.[/bold red]")
                        break
                    
                self.updateScreen()
                self.__console.print(table)
                nextIteration = False
                
        # Guardar resultados y mostrar gráfica
        self.__console.save_html("table.html")
        self.__plotResults(
            i_column,
            xi_column,
            gxi_column,
            abs_error_column,
            e_actual_less_e_allowed_column,
        )
        self.__console.print(
            "[blink cyan]All output was saved to table.html.[/blink cyan]",
            justify="center",
        )
        should_restart = self.__console.input(
            "[purple italic]Restart? (y/n): [/purple italic]"
        )
        if should_restart.lower() == "y":
            next_method = FixedPointMethod()
            next_method.start()

    def defineEquation(self, equation_str: str = "", g_equation_str: str = "", findStartingPoint: bool = False):
        # NUEVO CÓDIGO: Definir la ecuación y la función g(x)
        while equation_str == "" or type(equation_str) is not str:
            equation_str = console.input("[purple italic]Ecuación f(x) = 0 --- [/purple italic]")
        self.equation_str = equation_str
        self.updateScreen()
        
        # Solicitar la función g(x) para el método de punto fijo
        if g_equation_str == "" or type(g_equation_str) is not str:
            self.__console.print("[yellow]Para el método de punto fijo, debes transformar f(x) = 0 a x = g(x)[/yellow]")
            self.__console.print("[yellow]Por ejemplo, si f(x) = x^2 - 4 =
        abs_error_column = []  # Error absoluto
        e_actual_less_e_allowed_column = []  # ¿Error actual <= Error permitido?
        
        i = 1
        xi_1 = self.x0
        xi = self.x1
        
        # Crear tabla para mostrar resultados
        table = Table(title="Método de la Secante")
        table.add_column("Iteración")
        table.add_column("xi-1", width=100)
        table.add_column("xi", width=100)
        table.add_column("f(xi-1)", width=100)
        table.add_column("f(xi)", width=100)
        table.add_column("xi+1", width=100)
        table.add_column("|xi+1 - xi|", width=100)
        table.add_column("ea <= ep", width=100)
        
        while nextIteration:
            self.updateScreen()
            
            # Calcular los valores para esta iteración
            fxi_1 = f(xi_1)
            fxi = f(xi)
            
            # Evitar división por cero
            if abs(fxi - fxi_1) < 1e-10:
                self.__console.print("[bold red]Error: Denominador muy cercano a cero. División por cero.[/bold red]")
                break
                
            # Fórmula del Método de la Secante: xi+1 = xi - f(xi)(xi - xi-1) / (f(xi) - f(xi-1))
            xi1 = xi - fxi * (xi - xi_1) / (fxi - fxi_1)
            
            # Calcular el error absoluto
            abs_error = abs(xi1 - xi)
            
            # Almacenar los valores calculados
            i_column.append(i)
            xi_1_column.append(xi_1)
            xi_column.append(xi)
            fxi_1_column.append(fxi_1)
            fxi_column.append(fxi)
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
                str(xi_1),
                str(xi),
                str(fxi_1),
                str(fxi),
                str(xi1),
                str(abs_error),
                e_actual_less_e_allowed_column[-1],
            )
            
            # Mostrar la tabla
            self.__console.print(table)
            
            # Preparar para la siguiente iteración
            xi_1 = xi
            xi = xi1
            i += 1
            
            # Preguntar si continuar
            answer = console.input(
                '[purple italic]Siguiente Iteración? y/n ("." to run until "sí") <--- '
            )
            
            if answer.lower() == "n":
                nextIteration = False
                
            if answer.lower() == ".":
                # Ejecutar hasta encontrar la solución
                while e_actual_less_e_allowed_column[-1] == "no":
                    # Calcular los valores para esta iteración
                    fxi_1 = f(xi_1)
                    fxi = f(xi)
                    
                    # Evitar división por cero
                    if abs(fxi - fxi_1) < 1e-10:
                        self.__console.print("[bold red]Error: Denominador muy cercano a cero. División por cero.[/bold red]")
                        break
        ax1.set_xlabel("x")
        ax1.set_ylabel("f(x)")
        ax1.set_title("Función f(x)")
        ax1.legend()
        ax1.grid(True)
        
        # Gráfica de g(x) y y=x para mostrar convergencia
        ax2.plot(x_vals, y_vals_g, "g-", label="g(x)")  # Función g(x)
        ax2.plot(x_vals, y_vals_line, "k--", label="y = x")  # Línea y = x
        ax2.axhline(0, color="black", linewidth=0.8)  # Eje x
        ax2.axvline(0, color="black", linewidth=0.8)  # Eje y
        
        # Mostrar iteraciones en la gráfica
        for i in range(len(column_xi)-1):
            # Línea desde (xi, g(xi)) hasta (g(xi), g(xi))
            ax2.plot([column_xi[i], column_xi[i]], 
                     [column_gxi[i], column_xi[i]], 
                     'r-', alpha=0.3)
            # Línea desde (g(xi), g(xi)) hasta (g(xi), g(g(xi)))
            ax2.plot([column_xi[i], column_gxi[i]], 
                     [column_xi[i], column_xi[i]], 
                     'r-', alpha=0.3)
            # Punto (xi, g(xi))
            ax2.plot(column_xi[i], column_gxi[i], 'bo', markersize=5)
        
        # Marcar el punto de convergencia
        ax2.plot(column_xi[-1], column_gxi[-1], 'ro', markersize=8, label='Punto fijo')
        
        ax2.set_xlabel("x")
        ax2.set_ylabel("g(x)")
        ax2.set_title("Método de Punto Fijo")
        ax2.legend()
        ax2.grid(True)
        
        plt.tight_layout()
        plt.show()
                    
                    # Calcular el error absoluto
                    abs_error = abs(xi1 - xi)
                    
                    # Almacenar los valores calculados
                    i_column.append(i)
                    xi_1_column.append(xi_1)
                    xi_column.append(xi)
                    fxi_1_column.append(fxi_1)
                    fxi_column.append(fxi)
                    xi1_column.append(xi1)
                    abs_error_column.append(abs_error)
                    
                    # Verificar si el error es menor o igual al permitido
                    if abs_error <= self.ep:
                        e_actual_less_e_allowed_column.append("sí")
                        # Agregar la última fila a la tabla
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
                        self.updateScreen()
                        self.__console.print(table)
                        break
                    else:
                        e_actual_less_e_allowed_column.append("no")
                        
                    # Agregar fila a la tabla
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
                    
                    # Preparar para la siguiente iteración
                    xi_1 = xi
                    xi = xi1
                    i += 1
                    
                self.updateScreen()
                self.__console.print(table)
                nextIteration = False
                
        # Guardar resultados y mostrar gráfica
        self.__console.save_html("table.html")
        self.__plotResults(
            i_column,
            xi_1_column,
            xi_column,
            fxi_1_column,
            fxi_column,
            xi1_column,
            abs_error_column,
            e_actual_less_e_allowed_column,
        )
        self.__console.print(
            "[blink cyan]All output was saved to table.html.[/blink cyan]",
            justify="center",
        )
        should_restart = self.__console.input(
            "[purple italic]Restart? (y/n): [/purple italic]"
        )
        if should_restart.lower() == "y":
            next_method = SecantMethod()
            next_method.start()
