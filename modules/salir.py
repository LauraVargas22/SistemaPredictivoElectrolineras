# Confirmar salida del sistema
def confirmar_salida(mensaje):

    while True:
        opcion = input(mensaje).upper()
        if opcion == "S":
            return True
        elif opcion == "N":
            return False
        else:
            print("Opción no válida")