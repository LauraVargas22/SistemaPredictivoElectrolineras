"""Mensajes y catalogos reutilizables para la interfaz de consola."""

MENU_PRINCIPAL = [
    "Cargar y resumir datos base",
    "Gestionar electrolineras y puntos fijos",
    "Calcular ruta optima",
    "Simular recorrido con bateria",
    "Ver estadisticas de electrolineras",
    "Herramientas basicas de IA",
    "Generar mapas y reportes",
    "Comparar algoritmos clasicos vs IA",
    "Salir",
]

MENU_GESTION = [
    "Actualizar disponibilidad de electrolinera",
    "Agregar electrolinera",
    "Eliminar electrolinera",
    "Agregar punto fijo",
    "Actualizar punto fijo",
    "Eliminar punto fijo",
    "Volver",
]

MENU_ML = [
    "Entrenar modelos",
    "Ver metricas guardadas",
    "Probar prediccion simple",
    "Volver",
]

ALGORITMOS = {
    "dijkstra": "Dijkstra",
    "floyd_warshall": "Floyd-Warshall"
}

PESOS_RUTA = {
    "distancia_km": "Distancia",
    "tiempo_min": "Tiempo",
    "consumo_kwh": "Consumo energetico",
}

NIVELES_TRAFICO = {
    "leve": "Trafico leve",
    "medio": "Trafico medio",
    "alto": "Trafico alto",
}

MSG_DATOS_CARGADOS = "Datos cargados correctamente."
MSG_GRAFO_CREADO = "Grafo sintetico construido correctamente."
MSG_NO_RUTA = "No existe una ruta disponible entre los nodos seleccionados."
MSG_MODELOS_ENTRENADOS = "Modelos entrenados y almacenados en la carpeta models."
MSG_MAPAS_GENERADOS = "Mapas y reportes generados en la carpeta maps."

msgExcept = "Error en la opción ingresada..."
msgRegresar = "¿Desea regresar al menú anterior S(Si) N(No)?"
msgCase = "La opción ingresada no está permitida"
msgInfo = "¿Desea salir del programa S(Si) N(No)?"