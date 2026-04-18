# SISTEMA PREDICTIVO PUNTOS DE CARGA EN VEHÍCULOS ELÉCTRICOS

El incremento de vehículos eléctricos en el área metropolitana de Bucaramanga ha evidenciado algunas problemáticas como la ubicación y cobertura de los puntos de carga, lo cual obliga a los usuarios a recorrer mayores distancias para recargar sus vehículos.
Lo mencionado anteriormente afecta la eficiencia de la movilidad eléctrica, especialmente cuando los vehículos alcanzan niveles bajos de batería. En los últimos años, los vehículos eléctricos han aumentado como una alternativa amigable con el medio ambiente. Por esta razón, este proyecto busca utilizar conceptos como la Teoría de Grafos, Inteligencia Artificial y Programación en Python para analizar la red vial, con el fin de encontrar rutas más eficientes y mejorar la distribución de las electrolineras.

## Métodología del Problema

La metodología del proyecto consiste en la creación de un sistema para la optimización de electrolineras la cual se realizará mediante la recolección de datos de la red vial mediante herramientas como OpenStreetMap definiendo los puntos de carga y algunos sitios representativos, en base en esto se modelará la red vial como un grafo ponderado. 
A partir de este modelo, se simularán recorridos de vehículos eléctricos, considerando su nivel de batería y su necesidad de recarga. En estos casos, se aplicarán algoritmos de Dijkstra para evaluar los caminos más cortos permitiéndole a los usuarios encontrar la mejor ruta. 
Finalmente, los resultados obtenidos se analizarán y exportarán mediante archivos JSON, donde se visualice la frecuencia de uso de electrolineras y los recorridos realizados.

## Algoritmo

INICIO

1. Cargar datos:
   - Red vial
   - Electrolineras
   - Puntos de referencia
   - Vehículos

2. Construir el grafo

3. Para i desde 1 hasta n recorridos hacer:
   3.1 Seleccionar punto de inicio aleatorio
   3.2 Asignar vehículo
   3.3 Inicializar batería al 100%

   3.4 Mientras el recorrido no termine:
       - Moverse a siguiente nodo
       - Reducir batería según distancia

       SI batería ≤ 20% ENTONCES:
           - Encontrar electrolinera más cercana
           - Calcular ruta óptima (Dijkstra)
           - Registrar recarga
           - Restablecer batería

4. Guardar resultados

5. Generar estadísticas:
   - Uso de electrolineras
   - Frecuencia de recarga

FIN