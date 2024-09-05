from os import system
import numpy as np
import sympy as sp
from matplotlib import pyplot as plt
from rich.console import Console
from rich.table import Table

console = Console()

def determinar_intervalo(equation_str: str, x_min:int=-10, x_max:int=10, delta_x=0.1):
    
    x = sp.symbols('x')
    
    equation = sp.sympify(equation_str)
    
    f = sp.lambdify(x, equation, 'numpy')
    
    a, b = None, None
    x_current = x_min
    
    while x_current < x_max:
        f_x_current = f(x_current)
        f_x_next = f(x_current + delta_x)
        
        if f_x_current * f_x_next < 0:
            a, b = x_current, x_current + delta_x
            break
        
        x_current += delta_x
        
    if a is not None and b is not None:
        console.print(f"[bold green]Intervalo Encontrado:[/bold green] [blue]a = {a}[/blue][green],[/green] [red]b = {b}[/red]")
        #print(f"Intervalo encontrado: a = {a}, b = {b}")
        return a, b
    else:
        console.print("[bold red] no se encontró un intervalo con cambio de signo en el rango especificado.[/bold red]")
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
                plt.close('all')
                equation = sp.sympify(self.equation_str)
                latex_str = sp.latex(equation)
                plt.figure(figsize=(6,2))
                plt.text(0.1,0.5,f"${latex_str}$").set_fontsize(20)
                plt.axis('off')
                plt.show(block=False)
                self.last_equation_str = self.equation_str
    
    def __init__(self):
        self.__console = Console(record=True)
        self.__data_text = ""
        self.updateScreen()
    
    def updateScreen(self):
        self.redefineDataInScreen()
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
        self.__console.print(f"\n[red bold][u]No hay una ecuación definida.[/u][/red bold]")
        if try_to_define:
            self.defineEquation()
            
    def __plotResults(self, column_i: list, column_a: list, column_b: list, column_f_a: list, column_f_b: list, column_xi: list, column_f_xi: list, column_abs_f_xi: list, column_eactual_less_eallowed: list):
        x = sp.symbols('x')
        equation = sp.sympify(self.equation_str)
        f = sp.lambdify(x, equation, 'numpy')
        
        
        # Puntos para graficar la función
        x = np.linspace(self.a - 0.5, self.b + 0.5, 400)
        y = f(x)

        # Crear la gráfica
        plt.figure(figsize=(8, 6))
        plt.plot(x, y, 'b-', label='f(x)')  # Función
        plt.axhline(0, color='black', linewidth=0.8)  # Eje x
        plt.axvline(0, color='black', linewidth=0.8)  # Eje y

        # Marcar los puntos a, b, y xm
        plt.plot(column_a, column_f_a, 'ro', label='f(a)')
        plt.plot(column_b, column_f_b, 'ro', label='f(b)')
        plt.plot(column_xi, column_f_xi, 'ro', label='f(xi)')
        plt.axvline(column_a[-1], color='red', linestyle='--')
        plt.axvline(column_b[-1], color='red', linestyle='--')
        plt.axvline(column_xi[-1], color='black', linestyle='--')
        
        plt.axhline(column_f_a[-1], color='red', linestyle='--')  # Último valor de 'f(a)'
        plt.axhline(column_f_b[-1], color='red', linestyle='--')  # Último valor de 'f(b)'

        # Etiquetas y título
        plt.xlabel('x')
        plt.ylabel('f(x)')
        plt.title('Método de Bisección')
        plt.legend()
        plt.grid(True)

        # Mostrar la gráfica
        plt.show()
                
        

    def start(self):
        while self.equation_str == "":
            self.printEquationEmpty(try_to_define=True)
        while self.ep == None or type(self.ep) is not float or self.ep <= 0:
            try:
                self.ep = float(self.__console.input("[purple italic]Error permitido <--- [/]"))
            except ValueError as e:
                self.__console.print(e)
            
        x = sp.symbols('x')
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
        table.add_column("a")
        table.add_column("b")
        table.add_column("f(a)")
        table.add_column("f(b)")
        table.add_column("xi")
        table.add_column("f(xi)")
        table.add_column("abs(f(xi))")
        table.add_column("ea <= ep")
        
        while nextIteration:
            self.updateScreen()
            
            if i >= 2:
                last_f_xi_is_negative = f_xi_column[i-2] < 0
                
                last_fa_is_negative = fa_column[i-2] < 0
                last_fb_is_negative = fb_column[i-2] < 0
                
                if last_f_xi_is_negative:
                    if last_fa_is_negative:
                        a = xi_column[i-2]
                        fa = f(a)
                    elif last_fb_is_negative:
                        b = xi_column[i-2]
                        fb = f(b)
                else:
                    if not last_fa_is_negative:
                        a = xi_column[i-2]
                        fa = f(a)
                    elif not last_fb_is_negative:
                        b = xi_column[i-2]
                        fb = f(b)
            
            i_column.append(i)
            a_column.append(a)
            b_column.append(b)
            fa_column.append(fa)
            fb_column.append(fb)
            xi_column.append((a_column[i-1] + b_column[i-1]) / 2)
            f_xi_column.append(f(xi_column[i-1]))
            abs_f_xi_column.append(np.abs(f_xi_column[i-1]))
            if abs_f_xi_column[i-1] <= self.ep:
                e_actual_less_e_allowed_column.append('si')
            else: 
                e_actual_less_e_allowed_column.append('no')
                
            table.add_row(str(i_column[i-1]), str(a_column[i-1]), str(b_column[i-1]), str(fa_column[i-1]), str(fb_column[i-1]), str(xi_column[i-1]), str(f_xi_column[i-1]), str(abs_f_xi_column[i-1]), str(e_actual_less_e_allowed_column[i-1]))
            
            self.__console.print(table)
                
            i += 1
            
            answer = console.input("[purple italic]Siguiente Iteración? y/n <--- ")
            if answer.lower() == "n":
                nextIteration = False
            
        self.__console.save_html("table.html")
        self.__plotResults(i_column,a_column,b_column,fa_column,fb_column,xi_column,f_xi_column,abs_f_xi_column,e_actual_less_e_allowed_column)
                
    def findAB(self, x_min: int = x_min, x_max: int = x_max, delta_x: int = delta_x):
        if delta_x <= 0:
            self.__console.print("[bold red][u]delta_x[/u][/bold red][red] debe ser mayor que [bold][u]0[/u][/bold][/red] ")
            return None
        if x_min > x_max:
            self.__console.print("[bold red][u]x_min[/u][/bold red][red] debe ser menor que [bold][u]x_max[/u][/bold][/red] ")
            return None
        if self.equation_str == "":
            self.printEquationEmpty()
            self.x_min, self.x_max, self.delta_x = x_min, x_max, delta_x
            return self.defineEquation(thenFindAB=True)

        a, b = determinar_intervalo(self.equation_str)
        self.a = a
        self.b = b
        self.updateScreen()
        return True
    
    def defineEquation(self, equation_str: str = "", thenFindAB: bool = False):
        while equation_str == "" or type(equation_str) is not str:
            equation_str = console.input("[purple italic]Ecuación --- [/purple italic]")
        self.equation_str = equation_str
        self.updateScreen()
        if not thenFindAB:
            answer = console.input("[purple italic]Deseas que busque 'a' y 'b' automáticamente? y/n <--- [/purple italic]")
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
    ## Learning
    pass            
        
            
        