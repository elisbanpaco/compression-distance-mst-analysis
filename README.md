# Análisis de Rendimiento Estudiantil (NCD + MST)

Este proyecto busca descubrir los patrones ocultos que explican por qué los estudiantes aprueban o desaprueban, utilizando un enfoque matemático vanguardista: La **Distancia de Compresión Normalizada (NCD)** acoplada a la Teoría de Grafos mediante el **Árbol de Expansión Mínima (MST)**.

La arquitectura se divide estratégicamente en dos partes:
- **El Cerebro (Python)**: Genera datos, los preprocesa, extrae métricas de densidad de información y renderiza los resultados.
- **El Músculo (C++)**: Procesa la matemática pesada (paralelizada con OpenMP), comprime cientos de millones de combinaciones de estudiantes con `zlib` en memoria RAM y extrae el MST usando simultáneamente los algoritmos de **Prim** y **Kruskal**.

## Requisitos
- **Python 3.12+** con gestor de paquetes `uv`
- **CMake** y un compilador **C++17** (`g++`)
- Librerías de sistema: `zlib` y `OpenMP`

## Estructura del Proyecto
```text
compression-distance-mst-analysis/
├── data/                       # Dataset inicial y variables (ignorado en Git)
├── output/                     # Matriz CSV final y gráficos PNG (ignorado en Git)
├── src_python/                 # Scripts de orquestación
│   ├── 01_data_generator.py    # Crea 18,000 registros sintéticos (11 variables mixtas)
│   ├── 02_preprocessor.py      # Extrae tamaños independientes de variables y serializa
│   └── 04_visualizer.py        # Dibuja la red MST final
├── src_cpp/                    # Código de Alto Rendimiento
│   ├── edge.h                  # Estructura compartida de aristas
│   ├── prim.h                  # Algoritmo de Prim
│   ├── kruskal.h               # Algoritmo de Kruskal y Disjoint-Set
│   ├── main.cpp                # Orquestador (ZLib, OpenMP)
│   └── CMakeLists.txt          # Reglas de compilación
└── README.md                   # Documentación principal
```

## Instrucciones de Ejecución

### 1. Generación y Preprocesamiento (Python)
Desde la raíz del proyecto, ejecuta:
```bash
uv run src_python/01_data_generator.py
uv run src_python/02_preprocessor.py
```
Esto generará el dataset (`data/dataset_estudiantes.csv`), las carpetas para la densidad en KB de cada variable y `data/students_serialized` (que C++ leerá).

### 2. Cálculos Matemáticos (C++)
Compila y ejecuta el corazón matemático:
```bash
cd src_cpp
mkdir -p build && cd build
cmake ..
make
# Ejecutar prueba rápida de 500 estudiantes:
./ncd_mst_main 500

# Ejecutar el dataset completo de 18,000 estudiantes:
# (Nota: calcular la matriz de 162 millones de aristas tomará varios minutos)
./ncd_mst_main
```
Esto arrojará dos resultados idénticos en peso calculados por distintos caminos: `output/mst_edges_prim.csv` y `output/mst_edges_kruskal.csv`.

### 3. Visualización (Python)
Vuelve a la raíz y corre el visualizador para generar el grafo PNG de la red (por defecto usa las aristas de Prim):
```bash
cd ../../
uv run src_python/04_visualizer.py
```
¡Abre `output/mst_graph.png` y sorpréndete con los clústeres de similitud de los estudiantes!
