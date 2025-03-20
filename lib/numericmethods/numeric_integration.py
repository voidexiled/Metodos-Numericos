from rich.console import Console
from rich.table import Table
from os import system
import sympy as sp
import numpy as np
from matplotlib import pyplot as plt
from time import sleep

console = Console()


class TrapezoidalRule:
    # NUEVO CÓDIGO: Atributos para la Regla del Trapecio
    equation_str: str = ""
    a: float = 0  # Límite inferior
    b: float = 0  # Límite superior
    n: int = 0    # Número de subintervalos
    
    last_equation_str: str = equation_str

    def showEcuationPlot(self):
        # NUEVO CÓDIGO: Mostrar gráfica de la ecuación
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
        # NUEVO CÓDIGO: Inicialización
        self.__console = Console(record=True)
        self.__data_text = ""
        self.updateScreen()

    def updateScreen(self, shouldWait: bool = False, waitSeconds: float | int = 0.5):
        # NUEVO CÓDIGO: Actualizar pantalla
        self.redefineDataInScreen()
        if shouldWait:
            max_ms_sleep: float | int = 10.0
            ms_to_sleep = waitSeconds > max_ms_sleep and max_ms_sleep or waitSeconds
            sleep(ms_to_sleep)
        system("cls")
        self.__console.print(self.__data_text)
        self.showEcuationPlot()

    def redefineDataInScreen(self):
        # NUEVO CÓDIGO: Redefinir datos en pantalla
        self.__data_text = f"""
                                [cyan bold underline]-----Integración Numérica-----[/cyan bold underline]
                                [cyan bold frame]  ---Regla del Trapecio---  [/cyan bold frame]
                                [yellow italic]{sp.pretty(self.equation_str)}[/yellow italic]
                                [blue italic]a = {self.a}[/blue italic]
                                [blue italic]b = {self.b}[/blue italic]
                                [red italic]n = {self.n}[/red italic]
                                """

    def printEquationEmpty(self, try_to_define=False):
        # NUEVO CÓDIGO: Manejar ecuación vacía
        self.__console.print(
            f"\n[red bold][u]No hay una ecuación definida.[/u][/red bold]"
        )
        if try_to_define:
            self.defineEquation()
            
    def __plotResults(self, x_values, y_values, trapezoid_x, trapezoid_y):
        # NUEVO CÓDIGO: Graficar resultados
        plt.figure(figsize=(10, 6))
        
        # Graficar la función
        plt.plot(x_values, y_values, 'b-', label='f(x)')
        
        # Graficar los trapecios
        for i in range(len(trapezoid_x)):
            if i < len(trapezoid_x) - 1:
                # Graficar cada trapecio
                plt.fill([trapezoid_x[i], trapezoid_x[i], trapezoid_x[i+1], trapezoid_x[i+1]], 
                         [0, trapezoid_y[i], trapezoid_y[i+1], 0], 
                         'r', alpha=0.2)
                
        # Marcar los puntos de evaluación
        plt.plot(trapezoid_x, trapezoid_y, 'ro', label='Puntos de evaluación')
        
        # Etiquetas y título
        plt.xlabel('x')
        plt.ylabel('f(x)')
        plt.title('Regla del Trapecio')
        plt.grid(True)
        plt.legend()
        
        # Mostrar la gráfica
        plt.show()

    def defineEquation(self, equation_str: str = "", a: float = None, b: float = None, n: int = None):
        # NUEVO CÓDIGO: Definir la ecuación y parámetros
        while equation_str == "" or type(equation_str) is not str:
            equation_str = console.input("[purple italic]Ecuación --- [/purple italic]")
        self.equation_str = equation_str
        self.updateScreen()
        
        # Solicitar límites de integración si no se proporcionaron
        if a is None:
            try:
                self.a = float(console.input("[purple italic]Límite inferior (a) <--- [/purple italic]"))
            except ValueError:
                self.__console.print("[bold red]Error: El valor ingresado no es un número válido[/bold red]")
                return self.defineEquation(equation_str)
        else:
            self.a = a
            
        if b is None:
            try:
                self.b = float(console.input("[purple italic]Límite superior (b) <--- [/purple italic]"))
            except ValueError:
                self.__console.print("[bold red]Error: El valor ingresado no es un número válido[/bold red]")
                return self.defineEquation(equation_str, a)
        else:
            self.b = b
            
        # Solicitar número de subintervalos
        if n is None:
            try:
                self.n = int(console.input("[purple italic]Número de subintervalos (n) <--- [/purple italic]"))
                if self.n <= 0:
                    self.__console.print("[bold red]Error: El número de subintervalos debe ser positivo[/bold red]")
                    return self.defineEquation(equation_str, a, b)
            except ValueError:
                self.__console.print("[bold red]Error: El valor ingresado no es un número válido[/bold red]")
                return self.defineEquation(equation_str, a, b)
        else:
            self.n = n
            
        self.updateScreen(shouldWait=True)
        return True

    def start(self):
        # NUEVO CÓDIGO: Algoritmo de la Regla del Trapecio
        while self.equation_str == "":
            self.printEquationEmpty(try_to_define=True)
            
        # Verificar que los límites de integración y número de subintervalos estén definidos
        if self.a == self.b:
            self.__console.print("[bold red]Error: Los límites de integración son iguales[/bold red]")
            self.defineEquation(self.equation_str)
            
        if self.n <= 0:
            self.__console.print("[bold red]Error: El número de subintervalos debe ser positivo[/bold red]")
            self.defineEquation(self.equation_str, self.a, self.b)
            
        # Crear la tabla para mostrar resultados
        table = Table(title="Regla del Trapecio")
        table.add_column("i")
        table.add_column("x_i")
        table.add_column("f(x_i)")
        table.add_column("Coeficiente")
        table.add_column("Término")
        
        # Definir la función a integrar
        x = sp.symbols('x')
        expr = sp.sympify(self.equation_str)
        f = sp.lambdify(x, expr, "numpy")
        
        # Calcular el tamaño de cada subintervalo
        h = (self.b - self.a) / self.n
        
        # Inicializar la suma
        integral_value = 0
        
        # Crear listas para la gráfica
        x_values = np.linspace(self.a, self.b, 1000)
        y_values = f(x_values)
        trapezoid_x = []
        trapezoid_y = []
        
        # Aplicar la regla del trapecio
        for i in range(self.n + 1):
            x_i = self.a + i * h
            f_x_i = f(x_i)
            
            trapezoid_x.append(x_i)
            trapezoid_y.append(f_x_i)
            
            # Determinar el coeficiente
            if i == 0 or i == self.n:
                coef = 1
            else:
                coef = 2
                
            term = coef * f_x_i
            
            # Agregar a la tabla
            table.add_row(
                str(i),
                str(x_i),
                str(f_x_i),
                str(coef),
                str(term)
            )
            
            # Agregar a la suma
            integral_value += term
            
        # Multiplicar por h/2
        integral_value *= (h / 2)
        
        # Mostrar la tabla
        self.updateScreen()
        self.__console.print(table)
        
        # Mostrar el resultado
        self.__console.print(f"\n[bold green]Valor de la integral por Regla del Trapecio:[/bold green] {integral_value}")
        
        # Calcular el valor exacto de la integral si es posible
        try:
            exact_value = float(sp.integrate(expr, (x, self.a, self.b)))
            error = abs(exact_value - integral_value)
            self.__console.print(f"[bold blue]Valor exacto de la integral:[/bold blue] {exact_value}")
            self.__console.print(f"[bold red]Error absoluto:[/bold red] {error}")
            self.__console.print(f"[bold yellow]Error relativo:[/bold yellow] {(error/abs(exact_value))*100}%")
        except Exception as e:
            self.__console.print(f"[bold red]No se pudo calcular el valor exacto: {e}[/bold red]")
        
        # Guardar resultados
        self.__console.save_html("tabla_trapecio.html")
        self.__console.print(
            "[blink cyan]La tabla se guardó en tabla_trapecio.html.[/blink cyan]",
            justify="center",
        )
        
        # Graficar los resultados
        self.__plotResults(x_values, y_values, trapezoid_x, trapezoid_y)
        
        # Preguntar si se desea reiniciar
        should_restart = self.__console.input(
            "[purple italic]¿Reiniciar? (y/n): [/purple italic]"
        )
        if should_restart.lower() == "y":
            next_method = TrapezoidalRule()
            next_method.start()


class SimpsonRule:
    # NUEVO CÓDIGO: Implementación de la Regla de Simpson 1/3
    equation_str: str = ""
    a: float = 0  # Límite inferior
    b: float = 0  # Límite superior
    n: int = 0    # Número de subintervalos (debe ser par)
    
    last_equation_str: str = equation_str

    def showEcuationPlot(self):
        # NUEVO CÓDIGO: Mostrar gráfica de la ecuación
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
        # NUEVO CÓDIGO: Inicialización
        self.__console = Console(record=True)
        self.__data_text = ""
        self.updateScreen()

    def updateScreen(self, shouldWait: bool = False, waitSeconds: float | int = 0.5):
        # NUEVO CÓDIGO: Actualizar pantalla
        self.redefineDataInScreen()
        if shouldWait:
            max_ms_sleep: float | int = 10.0
            ms_to_sleep = waitSeconds > max_ms_sleep and max_ms_sleep or waitSeconds
            sleep(ms_to_sleep)
        system("cls")
        self.__console.print(self.__data_text)
        self.showEcuationPlot()

    def redefineDataInScreen(self):
        # NUEVO CÓDIGO: Redefinir datos en pantalla
        self.__data_text = f"""
                                [cyan bold underline]-----Integración Numérica-----[/cyan bold underline]
                                [cyan bold frame]  ---Regla de Simpson 1/3---  [/cyan bold frame]
                                [yellow italic]{sp.pretty(self.equation_str)}[/yellow italic]
                                [blue italic]a = {self.a}[/blue italic]
                                [blue italic]b = {self.b}[/blue italic]
                                [red italic]n = {self.n}[/red italic]
                                """

    def printEquationEmpty(self, try_to_define=False):
        # NUEVO CÓDIGO: Manejar ecuación vacía
        self.__console.print(
            f"\n[red bold][u]No hay una ecuación definida.[/u][/red bold]"
        )
        if try_to_define:
            self.defineEquation()
            
    def __plotResults(self, x_values, y_values, points_x, points_y):
        # NUEVO CÓDIGO: Graficar resultados
        plt.figure(figsize=(10, 6))
        
        # Graficar la función
        plt.plot(x_values, y_values, 'b-', label='f(x)')
        
        # Graficar las parábolas de Simpson
        for i in range(0, len(points_x) - 2, 2):
            # Tomar tres puntos consecutivos para cada parábola
            x_parabola = [points_x[i], points_x[i+1], points_x[i+2]]
            y_parabola = [points_y[i], points_y[i+1], points_y[i+2]]
            
            # NUEVO CÓDIGO: Crear puntos intermedios para la parábola
            x_interp = np.linspace(x_parabola[0], x_parabola[2], 100)
            
            # NUEVO CÓDIGO: Calcular coeficientes de la parábola (interpolación de Lagrange)
            def lagrange_interpolation(x, x_points, y_points):
                n = len(x_points)
                result = 0
                for i in range(n):
                    term = y_points[i]
                    for j in range(n):
                        if i != j:
                            term *= (x - x_points[j]) / (x_points[i] - x_points[j])
                    result += term
                return result
            
            # NUEVO CÓDIGO: Calcular valores de la parábola
            y_interp = [lagrange_interpolation(xi, x_parabola, y_parabola) for xi in x_interp]
            
            # NUEVO CÓDIGO: Graficar la parábola y rellenar el área bajo la curva
            plt.plot(x_interp, y_interp, 'g-', alpha=0.5)
            plt.fill_between(x_interp, 0, y_interp, color='g', alpha=0.1)
        
        # NUEVO CÓDIGO: Marcar los puntos de evaluación
        plt.plot(points_x, points_y, 'ro', label='Puntos de evaluación')
        
        # NUEVO CÓDIGO: Etiquetas y título
        plt.xlabel('x')
        plt.ylabel('f(x)')
        plt.title('Regla de Simpson 1/3')
        plt.grid(True)
        plt.legend()
        
        # NUEVO CÓDIGO: Mostrar la gráfica
        plt.show()

    def defineEquation(self, equation_str: str = "", a: float = None, b: float = None, n: int = None):
        # NUEVO CÓDIGO: Definir la ecuación y parámetros
        while equation_str == "" or type(equation_str) is not str:
            equation_str = console.input("[purple italic]Ecuación --- [/purple italic]")
        self.equation_str = equation_str
        self.updateScreen()
        
        # NUEVO CÓDIGO: Solicitar límites de integración si no se proporcionaron
        if a is None:
            try:
                self.a = float(console.input("[purple italic]Límite inferior (a) <--- [/purple italic]"))
            except ValueError:
                self.__console.print("[bold red]Error: El valor ingresado no es un número válido[/bold red]")
                return self.defineEquation(equation_str)
        else:
            self.a = a
            
        if b is None:
            try:
                self.b = float(console.input("[purple italic]Límite superior (b) <--- [/purple italic]"))
            except ValueError:
                self.__console.print("[bold red]Error: El valor ingresado no es un número válido[/bold red]")
                return self.defineEquation(equation_str, a)
        else:
            self.b = b
            
        # NUEVO CÓDIGO: Solicitar número de subintervalos (debe ser par para Simpson 1/3)
        if n is None:
            try:
                self.n = int(console.input("[purple italic]Número de subintervalos (n) <--- [/purple italic]"))
                if self.n <= 0:
                    self.__console.print("[bold red]Error: El número de subintervalos debe ser positivo[/bold red]")
                    return self.defineEquation(equation_str, a, b)
                if self.n % 2 != 0:
                    self.__console.print("[bold red]Error: El número de subintervalos debe ser par para la Regla de Simpson 1/3[/bold red]")
                    return self.defineEquation(equation_str, a, b)
            except ValueError:
                self.__console.print("[bold red]Error: El valor ingresado no es un número válido[/bold red]")
                return self.defineEquation(equation_str, a, b)
        else:
            self.n = n
            
        self.updateScreen(shouldWait=True)
        return True

    def start(self):
        # NUEVO CÓDIGO: Algoritmo de la Regla de Simpson 1/3
        while self.equation_str == "":
            self.printEquationEmpty(try_to_define=True)
            
        # NUEVO CÓDIGO: Verificar que los límites de integración y número de subintervalos estén definidos
        if self.a == self.b:
            self.__console.print("[bold red]Error: Los límites de integración son iguales[/bold red]")
            self.defineEquation(self.equation_str)
            
        if self.n <= 0:
            self.__console.print("[bold red]Error: El número de subintervalos debe ser positivo[/bold red]")
            self.defineEquation(self.equation_str, self.a, self.b)
            
        if self.n % 2 != 0:
            self.__console.print("[bold red]Error: El número de subintervalos debe ser par para la Regla de Simpson 1/3[/bold red]")
            self.defineEquation(self.equation_str, self.a, self.b)
            
        # NUEVO CÓDIGO: Crear la tabla para mostrar resultados
        table = Table(title="Regla de Simpson 1/3")
        table.add_column("i")
        table.add_column("x_i")
        table.add_column("f(x_i)")
        table.add_column("Coeficiente")
        table.add_column("Término")
        
        # NUEVO CÓDIGO: Definir la función a integrar
        x = sp.symbols('x')
        expr = sp.sympify(self.equation_str)
        f = sp.lambdify(x, expr, "numpy")
        
        # NUEVO CÓDIGO: Calcular el tamaño de cada subintervalo
        h = (self.b - self.a) / self.n
        
        # NUEVO CÓDIGO: Inicializar la suma
        integral_value = 0
        
        # NUEVO CÓDIGO: Crear listas para la gráfica
        x_values = np.linspace(self.a, self.b, 1000)
        y_values = f(x_values)
        points_x = []
        points_y = []
        
        # NUEVO CÓDIGO: Aplicar la regla de Simpson 1/3
        for i in range(self.n + 1):
            x_i = self.a + i * h
            f_x_i = f(x_i)
            
            points_x.append(x_i)
            points_y.append(f_x_i)
            
            # NUEVO CÓDIGO: Determinar el coeficiente
            if i == 0 or i == self.n:
                coef = 1
            elif i % 2 == 0:  # Si es par (excepto 0 y n)
                coef = 2
            else:  # Si es impar
                coef = 4
                
            term = coef * f_x_i
            
            # NUEVO CÓDIGO: Agregar a la tabla
            table.add_row(
                str(i),
                str(x_i),
                str(f_x_i),
                str(coef),
                str(term)
            )
            
            # NUEVO CÓDIGO: Agregar a la suma
            integral_value += term
            
        # NUEVO CÓDIGO: Multiplicar por h/3
        integral_value *= (h / 3)
        
        # NUEVO CÓDIGO: Mostrar la tabla
        self.updateScreen()
        self.__console.print(table)
        
        # NUEVO CÓDIGO: Mostrar el resultado
        self.__console.print(f"\n[bold green]Valor de la integral por Regla de Simpson 1/3:[/bold green] {integral_value}")
        
        # NUEVO CÓDIGO: Calcular el valor exacto de la integral si es posible
        try:
            exact_value = float(sp.integrate(expr, (x, self.a, self.b)))
            error = abs(exact_value - integral_value)
            self.__console.print(f"[bold blue]Valor exacto de la integral:[/bold blue] {exact_value}")
            self.__console.print(f"[bold red]Error absoluto:[/bold red] {error}")
            self.__console.print(f"[bold yellow]Error relativo:[/bold yellow] {(error/abs(exact_value))*100}%")
        except Exception as e:
            self.__console.print(f"[bold red]No se pudo calcular el valor exacto: {e}[/bold red]")
        
        # NUEVO CÓDIGO: Guardar resultados
        self.__console.save_html("tabla_simpson.html")
        self.__console.print(
            "[blink cyan]La tabla se guardó en tabla_simpson.html.[/blink cyan]",
            justify="center",
        )
        
        # NUEVO CÓDIGO: Graficar los resultados
        self.__plotResults(x_values, y_values, points_x, points_y)
        
        # NUEVO CÓDIGO: Preguntar si se desea reiniciar
        should_restart = self.__console.input(
            "[purple italic]¿Reiniciar? (y/n): [/purple italic]"
        )
        if should_restart.lower() == "y":
            next_method = SimpsonRule()
            next_method.start()


class SimpsonThreeEighthsRule:
    # NUEVO CÓDIGO: Implementación de la Regla de Simpson 3/8
    equation_str: str = ""
    a: float = 0  # Límite inferior
    b: float = 0  # Límite superior
    n: int = 0    # Número de subintervalos (debe ser múltiplo de 3)
    
    last_equation_str: str = equation_str

    def showEcuationPlot(self):
        # NUEVO CÓDIGO: Mostrar gráfica de la ecuación
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
        # NUEVO CÓDIGO: Inicialización
        self.__console = Console(record=True)
        self.__data_text = ""
        self.updateScreen()

    def updateScreen(self, shouldWait: bool = False, waitSeconds: float | int = 0.5):
        # NUEVO CÓDIGO: Actualizar pantalla
        self.redefineDataInScreen()
        if shouldWait:
            max_ms_sleep: float | int = 10.0
            ms_to_sleep = waitSeconds > max_ms_sleep and max_ms_sleep or waitSeconds
            sleep(ms_to_sleep)
        system("cls")
        self.__console.print(self.__data_text)
        self.showEcuationPlot()

    def redefineDataInScreen(self):
        # NUEVO CÓDIGO: Redefinir datos en pantalla
        self.__data_text = f"""
                                [cyan bold underline]-----Integración Numérica-----[/cyan bold underline]
                                [cyan bold frame]  ---Regla de Simpson 3/8---  [/cyan bold frame]
                                [yellow italic]{sp.pretty(self.equation_str)}[/yellow italic]
                                [blue italic]a = {self.a}[/blue italic]
                                [blue italic]b = {self.b}[/blue italic]
                                [red italic]n = {self.n}[/red italic]
                                """

    def printEquationEmpty(self, try_to_define=False):
        # NUEVO CÓDIGO: Manejar ecuación vacía
        self.__console.print(
            f"\n[red bold][u]No hay una ecuación definida.[/u][/red bold]"
        )
        if try_to_define:
            self.defineEquation()
            
    def __plotResults(self, x_values, y_values, points_x, points_y):
        # NUEVO CÓDIGO: Graficar resultados
        plt.figure(figsize=(10, 6))
        
        # Graficar la función
        plt.plot(x_values, y_values, 'b-', label='f(x)')
        
        # Graficar las curvas cúbicas de Simpson 3/8
        for i in range(0, len(points_x) - 3, 3):
            # Tomar cuatro puntos consecutivos para cada curva cúbica
            x_cubic = [points_x[i], points_x[i+1], points_x[i+2], points_x[i+3]]
            y_cubic = [points_y[i], points_y[i+1], points_y[i+2], points_y[i+3]]
            
            # Crear puntos intermedios para la curva cúbica
            x_interp = np.linspace(x_cubic[0], x_cubic[3], 100)
            
            # Calcular coeficientes de la interpolación cúbica (interpolación de Lagrange)
            def lagrange_interpolation(x, x_points, y_points):
                n = len(x_points)
                result = 0
                for i in range(n):
                    term = y_points[i]
                    for j in range(n):
                        if i != j:
                            term *= (x - x_points[j]) / (x_points[i] - x_points[j])
                    result += term
                return result
            
            # Calcular valores de la curva cúbica
            y_interp = [lagrange_interpolation(xi, x_cubic, y_cubic) for xi in x_interp]
            
            # Graficar la curva cúbica y rellenar el área bajo la curva
            plt.plot(x_interp, y_interp, 'r-', alpha=0.5)
            plt.fill_between(x_interp, 0, y_interp, color='r', alpha=0.1)
        
        # Marcar los puntos de evaluación
        plt.plot(points_x, points_y, 'ro', label='Puntos de evaluación')
        
        # Etiquetas y título
        plt.xlabel('x')
        plt.ylabel('f(x)')
        plt.title('Regla de Simpson 3/8')
        plt.grid(True)
        plt.legend()
        
        # Mostrar la gráfica
        plt.show()

    def defineEquation(self, equation_str: str = "", a: float = None, b: float = None, n: int = None):
        # NUEVO CÓDIGO: Definir la ecuación y parámetros
        while equation_str == "" or type(equation_str) is not str:
            equation_str = console.input("[purple italic]Ecuación --- [/purple italic]")
        self.equation_str = equation_str
        self.updateScreen()
        
        # Solicitar límites de integración si no se proporcionaron
        if a is None:
            try:
                self.a = float(console.input("[purple italic]Límite inferior (a) <--- [/purple italic]"))
            except ValueError:
                self.__console.print("[bold red]Error: El valor ingresado no es un número válido[/bold red]")
                return self.defineEquation(equation_str)
        else:
            self.a = a
            
        if b is None:
            try:
                self.b = float(console.input("[purple italic]Límite superior (b) <--- [/purple italic]"))
            except ValueError:
                self.__console.print("[bold red]Error: El valor ingresado no es un número válido[/bold red]")
                return self.defineEquation(equation_str, a)
        else:
            self.b = b
            
        # Solicitar número de subintervalos (debe ser múltiplo de 3 para Simpson 3/8)
        if n is None:
            try:
                self.n = int(console.input("[purple italic]Número de subintervalos (n) <--- [/purple italic]"))
                if self.n <= 0:
                    self.__console.print("[bold red]Error: El número de subintervalos debe ser positivo[/bold red]")
                    return self.defineEquation(equation_str, a, b)
                if self.n % 3 != 0:
                    self.__console.print("[bold red]Error: El número de subintervalos debe ser múltiplo de 3 para la Regla de Simpson 3/8[/bold red]")
                    return self.defineEquation(equation_str, a, b)
            except ValueError:
                self.__console.print("[bold red]Error: El valor ingresado no es un número válido[/bold red]")
                return self.defineEquation(equation_str, a, b)
        else:
            self.n = n
            
        self.updateScreen(shouldWait=True)
        return True

    def start(self):
        # NUEVO CÓDIGO: Algoritmo de la Regla de Simpson 3/8
        while self.equation_str == "":
            self.printEquationEmpty(try_to_define=True)
            
        # Verificar que los límites de integración y número de subintervalos estén definidos
        if self.a == self.b:
            self.__console.print("[bold red]Error: Los límites de integración son iguales[/bold red]")
            self.defineEquation(self.equation_str)
            
        if self.n <= 0:
            self.__console.print("[bold red]Error: El número de subintervalos debe ser positivo[/bold red]")
            self.defineEquation(self.equation_str, self.a, self.b)
            
        if self.n % 3 != 0:
            self.__console.print("[bold red]Error: El número de subintervalos debe ser múltiplo de 3 para la Regla de Simpson 3/8[/bold red]")
            self.defineEquation(self.equation_str, self.a, self.b)
            
        # Crear la tabla para mostrar resultados
        table = Table(title="Regla de Simpson 3/8")
        table.add_column("i")
        table.add_column("x_i")
        table.add_column("f(x_i)")
        table.add_column("Coeficiente")
        table.add_column("Término")
        
        # Definir la función a integrar
        x = sp.symbols('x')
        expr = sp.sympify(self.equation_str)
        f = sp.lambdify(x, expr, "numpy")
        
        # Calcular el tamaño de cada subintervalo
        h = (self.b - self.a) / self.n
        
        # Inicializar la suma
        integral_value = 0
        
        # Crear listas para la gráfica
        x_values = np.linspace(self.a, self.b, 1000)
        y_values = f(x_values)
        points_x = []
        points_y = []
        
        # Aplicar la regla de Simpson 3/8
        for i in range(self.n + 1):
            x_i = self.a + i * h
            f_x_i = f(x_i)
            
            points_x.append(x_i)
            points_y.append(f_x_i)
            
            # Determinar el coeficiente según la Regla de Simpson 3/8
            if i == 0 or i == self.n:
                coef = 1
            elif i % 3 == 0:  # Si es múltiplo de 3 (excepto 0 y n)
                coef = 2
            else:  # Para los demás puntos
                coef = 3
                
            term = coef * f_x_i
            
            # Agregar a la tabla
            table.add_row(
                str(i),
                str(x_i),
                str(f_x_i),
                str(coef),
                str(term)
            )
            
            # Agregar a la suma
            integral_value += term
            
        # Multiplicar por (3h/8)
        integral_value *= (3 * h / 8)
        
        # Mostrar la tabla
        self.updateScreen()
        self.__console.print(table)
        
        # Mostrar el resultado
        self.__console.print(f"\n[bold green]Valor de la integral por Regla de Simpson 3/8:[/bold green] {integral_value}")
        
        # Calcular el valor exacto de la integral si es posible
        try:
            exact_value = float(sp.integrate(expr, (x, self.a, self.b)))
            error = abs(exact_value - integral_value)
            self.__console.print(f"[bold blue]Valor exacto de la integral:[/bold blue] {exact_value}")
            self.__console.print(f"[bold red]Error absoluto:[/bold red] {error}")
            self.__console.print(f"[bold yellow]Error relativo:[/bold yellow] {(error/abs(exact_value))*100}%")
        except Exception as e:
            self.__console.print(f"[bold red]No se pudo calcular el valor exacto: {e}[/bold red]")
        
        # Guardar resultados
        self.__console.save_html("tabla_simpson38.html")
        self.__console.print(
            "[blink cyan]La tabla se guardó en tabla_simpson38.html.[/blink cyan]",
            justify="center",
        )
        
        # Graficar los resultados
        self.__plotResults(x_values, y_values, points_x, points_y)
        
        # Preguntar si se desea reiniciar
        should_restart = self.__console.input(
            "[purple italic]¿Reiniciar? (y/n): [/purple italic]"
        )
        if should_restart.lower() == "y":
            next_method = SimpsonThreeEighthsRule()
            next_method.start()
