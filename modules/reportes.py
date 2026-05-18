import utils.archivos as js

# Guardar reporte en formato JSON
def exportar_reporte_json(nombre_archivo, contenido):
    ruta = js.obtener_ruta_data(nombre_archivo)
    archivo = js.escribir_json(ruta, contenido)
    return archivo
