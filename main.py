'''
Archivo principal para la ejecución del programa
'''
import time

if (__name__=='__main__'):
    #Importación modulos
    import modules.mensajes as msg
    import modules.customs as cu
    import modules.titles as t
    import modules.menus as me
    import modules.salir as sa

isActive = True
t.show_title()
time.sleep(5)
while (isActive):
    try:
        cu.borrarPantalla()
        me.show_menu()
        opcMenu = int(input('Seleccione:__'))
        cu.borrarPantalla()
        
        match opcMenu:
            case 1:
                """Cargar datos"""
                cu.borrarPantalla()
                t.cargar_datos()
                print("Funcionalidad en desarrollo...")
                cu.pausarPantalla()
            case 2:
                """Simular recorridos"""
                cu.borrarPantalla()
                t.simular_recorridos()
                print("Funcionalidad en desarrollo...")
                cu.pausarPantalla()
            case 3: 
                """Calcular rutas"""
                cu.borrarPantalla()
                t.calcular_rutas()
                print("Funcionalidad en desarrollo...")
                cu.pausarPantalla()
            case 4: 
                """Visualizar resultados"""
                cu.borrarPantalla()
                t.visualizar_resultados()
                print("Funcionalidad en desarrollo...")
                cu.pausarPantalla()
            case 5: 
                """Guardar Información"""
                cu.borrarPantalla()
                t.guardar_informacion()
                print("Funcionalidad en desarrollo...")
                cu.pausarPantalla()
            case 6:
                # Opción Salir
                isActive = sa.validateData(msg.msgInfo)
            case _:
                print (msg.msgCase)
                cu.pausarPantalla()
        
    except ValueError:
        print (msg.msgExcept)
        cu.pausarPantalla()
        continue