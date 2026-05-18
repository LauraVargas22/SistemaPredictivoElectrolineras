import json
import time

import joblib
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import accuracy_score

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestClassifier

from modules.rutas import calcular_ruta_dijkstra
from utils.archivos import (
    MODELS_DIR,
    crear_directorio,
    obtener_ruta_modelo
)


# Columnas numéricas
NUMERICAS = [
    "bateria_inicial_pct",
    "distancia_ruta_km",
    "tiempo_ruta_min",
    "consumo_ruta_kwh"
]

# Columnas categóricas
CATEGORICAS = [
    "origen",
    "destino",
    "vehiculo"
]


# Generar dataset de entrenamiento
def generar_dataset_entrenamiento( grafo, configuracion, muestras=200):

    puntos = []
    electrolineras = []

    # Separar nodos
    for nodo, datos in grafo.nodes(data=True):

        if datos.get("tipo") == "punto_fijo":
            puntos.append(nodo)

        elif datos.get("tipo") == "electrolinera":
            electrolineras.append(nodo)

    vehiculos = configuracion.get("vehiculos", [])

    registros = []

    # Crear muestras
    while len(registros) < muestras:

        # numpy.random.choice es una función de la librería que permite seleccionar elementos de forma aleatoria de un arreglo o lista
        origen = np.random.choice(puntos)
        destino = np.random.choice(puntos)

        if origen == destino:
            continue

        vehiculo = np.random.choice(vehiculos)

        try:
            ruta = calcular_ruta_dijkstra(
                grafo,
                origen,
                destino,
                "distancia_km"
            )

        except:
            continue

        if len(ruta["ruta"]) < 2:
            continue

        # np.random.randint genera números aleatorios entre un rango específico
        # Se inicializa la bateria en un porcentaje aletario entre 20 y 100
        bateria = np.random.randint(20, 101)

        # np.random.normal se busca añadir un variación a las estimaciones para no tomar siempre los mismos valores
        # Desviación estándar de 1kWh
        consumo_estimado = (ruta["consumo_kwh"] + np.random.normal(0, 1))
        # Desviación estándar de 2 minutos
        tiempo_estimado = (ruta["tiempo_min"] + np.random.normal(0, 2))

        requiere_recarga = 0

        if consumo_estimado > (vehiculo["capacidad_bateria_kwh"] * (bateria / 100)):
            requiere_recarga = 1

        registros.append({
            "origen": origen,
            "destino": destino,
            "vehiculo": vehiculo["nombre"],
            "bateria_inicial_pct": bateria,
            "distancia_ruta_km": ruta["distancia_km"],
            "tiempo_ruta_min": ruta["tiempo_min"],
            "consumo_ruta_kwh": ruta["consumo_kwh"],
            "consumo_estimado_kwh": round(consumo_estimado, 2),
            "tiempo_estimado_min": round(tiempo_estimado, 2),
            "requiere_recarga": requiere_recarga
        })

    dataset = pd.DataFrame(registros)

    ruta_dataset = obtener_ruta_modelo("dataset_entrenamiento.csv")

    dataset.to_csv(ruta_dataset, index=False)

    return dataset


# Entrenar modelos
def entrenar_modelos(grafo, configuracion):

    # PREPARACIÓN DE DATOS
    crear_directorio(MODELS_DIR)

    dataset = generar_dataset_entrenamiento(grafo, configuracion)

    metricas = []

    # Variables de entrada
    X = dataset[[
        "bateria_inicial_pct",
        "distancia_ruta_km",
        "tiempo_ruta_min",
        "consumo_ruta_kwh"
    ]]

    # -------------------------
    # MODELO DE CONSUMO (Regresión)
    # -------------------------

    # Predecir el consumo estimado en kWh
    y_consumo = dataset[
        "consumo_estimado_kwh"
    ]

    # División de datos se deben separar los datos 80% para entrenar (X_train, y_train)
    # Y se evalúa el 20% (X_test, y_test)
    X_train, X_test, y_train, y_test = train_test_split(X, y_consumo, test_size=0.2)

    modelo_consumo = LinearRegression()

    # Obtener el tiempo actual del sistema
    inicio = time.time()

    # Procesamiento de datos, se determina cuanto tarda en aprender
    modelo_consumo.fit(X_train, y_train)

    # Aplica lo aprendido y realiza prediciones
    predicciones = modelo_consumo.predict(X_test)

    fin = time.time()

    # Métrica fundamental para evaluar el rendimiento de modelos de regresión
    mae = mean_absolute_error(y_test,predicciones)

    # Exportación modelo entrenado como archivo .jotlib
    ruta_modelo = obtener_ruta_modelo("modelo_consumo.joblib")
    joblib.dump(modelo_consumo, ruta_modelo)

    metricas.append({
        "modelo": "LinearRegression",
        "mae": round(mae, 2),
        "tiempo": round(fin - inicio, 2)
    })

    # -------------------------
    # MODELO DE RECARGA
    # -------------------------

    y_recarga = dataset[
        "requiere_recarga"
    ]

    X_train, X_test, y_train, y_test = train_test_split(X, y_recarga, test_size=0.2)

    # Uso de árboles de decisión
    modelo_recarga = RandomForestClassifier()

    inicio = time.time()

    modelo_recarga.fit(X_train,y_train)

    predicciones = modelo_recarga.predict(X_test)

    fin = time.time()

    # Métrica más utilizada para evaluar modelos de clasificación
    # Se mide el procentaje de respuestas correctas
    accuracy = accuracy_score(y_test,predicciones)

    ruta_modelo = obtener_ruta_modelo(
        "modelo_recarga.joblib"
    )

    joblib.dump(modelo_recarga, ruta_modelo)

    metricas.append({
        "modelo": "RandomForest",
        "accuracy": round(accuracy, 2),
        "tiempo": round(fin - inicio, 2)
    })

    # Guardar métricas
    resumen = {
        "metricas": metricas
    }

    ruta_metricas = obtener_ruta_modelo(
        "metricas_modelos.json"
    )

    # json.dump convierte objeto Python a formato JSON
    with open(ruta_metricas,"w",encoding="utf-8") as archivo:
        json.dump(resumen,archivo,indent=4,ensure_ascii=False)

    return resumen


# Cargar métricas guardadas
def cargar_metricas_modelos():

    ruta = obtener_ruta_modelo(
        "metricas_modelos.json"
    )

    if not ruta.exists():
        return []

    # json.load leer datos almacenados en archivos JSON 
    with open(ruta,"r",encoding="utf-8") as archivo:
        datos = json.load(archivo)

    return datos.get("metricas", [])


# Hacer predicciones
def predecir_escenario(escenario):

    datos = pd.DataFrame([escenario])

    X = datos[[
        "bateria_inicial_pct",
        "distancia_ruta_km",
        "tiempo_ruta_min",
        "consumo_ruta_kwh"
    ]]

    resultados = {}

    # Predicción consumo
    ruta_consumo = obtener_ruta_modelo(
        "modelo_consumo.joblib"
    )

    if ruta_consumo.exists():
        #jotlib.load carga modelo entrenado 
        modelo = joblib.load(
            ruta_consumo
        )

        pred = modelo.predict(X)[0]

        resultados[
            "consumo_estimado_kwh"
        ] = round(float(pred), 2)

    # Predicción recarga
    ruta_recarga = obtener_ruta_modelo(
        "modelo_recarga.joblib"
    )

    if ruta_recarga.exists():

        modelo = joblib.load(
            ruta_recarga
        )

        pred = modelo.predict(X)[0]

        resultados[
            "requiere_recarga"
        ] = int(pred)

    return resultados