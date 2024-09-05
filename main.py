from os import system
import lib.numericmethods.equations_sqrt as eq_sqrt
def main():
    equation_str = "exp(x) + 2**(-x) + 2*cos(x) - 6"
    bisect = eq_sqrt.BisectMethod()
    bisect.start()

if __name__ == "__main__":
    system("cls")
    main()