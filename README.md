# SISTEMA PREDICTIVO PUNTOS DE CARGA EN VEHÍCULOS ELÉCTRICOS

## Descripción del proyecto

Este proyecto consiste en una aplicación de consola desarrollada en Python que permite modelar una red vial urbana utilizando teoría de grafos. El sistema integra algoritmos clásicos de búsqueda de rutas, simulación de batería para vehículos eléctricos y modelos básicos de Machine Learning para analizar escenarios relacionados con movilidad y electrolineras.

El objetivo principal del proyecto es aplicar conceptos vistos en estructuras de datos, grafos, análisis de rutas e inteligencia artificial dentro de un entorno académico y práctico.

## Objetivos
### Objetivo general

Desarrollar un sistema predictivo de análisis vial basado en la teoría de grafos y fundamentos de programación con el propósito de calcular rutas óptimas, gestionar el uso de electrolineras y simular recorridos de vehículos eléctricos.

### Objetivos específicos
- Representar una red vial mediante grafos ponderados.
- Simular consumo de batería en vehículos eléctricos.
- Gestionar electrolineras y puntos fijos desde archivos JSON.
- Comparar resultados entre algoritmos clásicos y modelos de IA.

## Tecnologías utilizadas
- Python
- NetworkX
- Folium
- Pandas
- NumPy
- Scikit-learn
- Pyfiglet -Rich (UI)

## Funcionalidades principales
1. Gestión de infraestructura: 
- Agregar electrolineras
- Eliminar electrolineras
- Actualizar disponibilidad
- Agregar puntos fijos
- Eliminar puntos fijos
- Crear conexiones automáticas entre nodos

2. Almacenamiento de la información en archivos JSON.
3. Construcción del grafo

La red vial se construye mediante un grafo ponderado usando:
- Distancia
- Tiempo
- Consumo energético

Cada nodo representa:

- Electrolineras
- Puntos fijos

Cada arista representa una conexión vial entre nodos.

## Algoritmos implementados

El proyecto implementa diferentes algoritmos de rutas:

- Dijkstra: Buscar la ruta más corta
- Floyd-Warshall	Calcular rutas mínimas globales

Los algoritmos pueden trabajar con distintos pesos:

- distancia_km
- tiempo_min
- consumo_kwh
- Simulación de batería

El sistema puede simular recorridos de vehículos eléctricos teniendo en cuenta:

- Batería inicial
- Consumo energético
- Distancia recorrida
- Tráfico
- Recargas necesarias
- Electrolineras disponibles

Si la batería baja demasiado, el sistema busca automáticamente una estación de carga cercana.

## Machine Learning

El proyecto incluye un módulo básico de inteligencia artificial para:

- Predecir consumo energético
- Estimar tiempos de recorrido
- Detectar necesidad de recarga
- Analizar saturación de estaciones
- Recomendar electrolineras
- Modelos utilizados
- Linear Regression
- Random Forest

## Estructura del proyecto
```bash
Proyecto/
│
├── data/
│   ├── configuracion.json
│   ├── electrolineras.json
│   ├── puntos_fijos.json
│   └── resultados.json
│
├── maps/
│
├── models/
│
├── modules/
│   ├── grafo.py
│   ├── infraestructura.py
│   ├── inicializarData.py
│   ├── mensajes.py
│   ├── menus.py
│   ├── modelos_ml.py
│   ├── reportes.py
│   ├── rutas.py
│   ├── titles.py
│   ├── visualizacion.py
│   └── salir.py
│
├── utils/
│   └── archivos.py
│
├── main.py
├── requirements.txt
└── README.md
```

## Instalación
1. Clonar el proyecto
```
https://github.com/LauraVargas22/SistemaPredictivoElectrolineras.git
```
2. Entrar a la carpeta
```
cd SistemaPredictivoElectrolineras
```
3. Instalar dependencias
```
pip install -r requirements.txt
```
4. Ejecución del sistema

python main.py

## Aplicaciones:

Durante el desarrollo del proyecto se aplicaron temas relacionados con:

- Programación estructurada
- Manejo de archivos JSON
- Teoría de Grafos
- Machine Learning
- Persistencia de datos
- Simulación
- Visualización de datos

## Conclusiones

Este proyecto permitió integrar diferentes áreas de la programación y la ciencia de datos en una sola aplicación. Además de trabajar con grafos y rutas óptimas, también se exploró el uso de inteligencia artificial para apoyar la toma de decisiones en escenarios de movilidad eléctrica.

## Autores

Proyecto académico desarrollado por:
- Laura Vargas
- Nataly Ortega 
- Josman Niño
