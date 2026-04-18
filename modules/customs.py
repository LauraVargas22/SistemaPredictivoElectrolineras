import sys
import os

def borrarPantalla ():
    if sys.platform == "Linux" or sys.platform == "darwin":
        os.system("clear")
    else:
        os.system("cls")

def pausarPantalla():
    if  sys.platform == "Linux" or sys.platform == "darwin":
        x = input("Presione una tecla para continuar...")
    else:
        os.system("pause")