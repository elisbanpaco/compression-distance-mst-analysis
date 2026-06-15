# 🎓 Análisis de Rendimiento Estudiantil (NCD + MST)

![Python](https://img.shields.io/badge/Python-3.12%2B-blue?logo=python)
![C++](https://img.shields.io/badge/C%2B%2B-17-00599C?logo=c%2B%2B)
![CMake](https://img.shields.io/badge/CMake-Ready-green?logo=cmake)
![License](https://img.shields.io/badge/License-MIT-lightgray)

Este proyecto emplea un enfoque de **Machine Learning No Supervisado** basado en la teoría de la información para descubrir patrones subyacentes y relaciones complejas entre variables del perfil estudiantil. Utiliza la **Distancia de Compresión Normalizada (NCD)** acoplada a la Teoría de Grafos mediante el **Árbol de Expansión Mínima (MST)**.

## 🧠 Arquitectura del Sistema

El proyecto implementa el patrón de diseño "la herramienta adecuada para el trabajo adecuado", dividiéndose en un pipeline de dos capas principales:

1. **La Capa de Orquestación y Datos (Python)**:
   - Generación de datos sintéticos realistas (18,000 registros, 11 variables sin target explícito).
   - Preprocesamiento, particionamiento y serialización de atributos.
   - Renderizado y visualización del grafo final.

2. **El Motor Matemático de Alto Rendimiento (C++)**:
   - Cálculos intensivos de matrices implementados en **C++17**.
   - Cálculo cruzado utilizando los algoritmos de **Prim** y **Kruskal** para asegurar la precisión del Árbol de Expansión Mínima.
   - Preparado para escalar las matrices de correlación basándose en los pesos extraídos.

---

## ⚙️ Requisitos del Sistema

* **Python 3.12+** y el moderno gestor de paquetes `uv`.
* **Compilador compatible con C++17** (Ej. `g++`, `clang++`).
* **CMake** (v3.10 o superior).
* **Librerías de Sistema**: `zlib` y `OpenMP` (disponibles en la mayoría de distros Linux/macOS).

## 📂 Estructura del Proyecto

```text
compression-distance-mst-analysis/
├── data/                       # Dataset inicial y pesos generados (Ignorado en Git)
├── output/                     # Matrices NCD, MST en CSV y gráficos PNG (Ignorado en Git)
├── src_python/                 # Scripts de orquestación y visualización
│   ├── 01_data_generator.py    # Generador de 18,000 registros sintéticos (11 variables mixtas)
│   ├── 02_preprocessor.py      # Serialización y extracción de pesos de compresión
│   └── 04_visualizer.py        # Generador de grafos de correlación (NetworkX + Matplotlib)
├── src_cpp/                    # Motor de Alto Rendimiento (C++ Core)
│   ├── edge.h                  # Estructura de abstracción de aristas
│   ├── prim.h                  # Implementación matemática del Algoritmo de Prim
│   ├── kruskal.h               # Implementación matemática del Algoritmo de Kruskal (Disjoint-Set)
│   ├── main.cpp                # Orquestador del cómputo NCD + extracción del MST
│   └── CMakeLists.txt          # Reglas de construcción para el core
├── pyproject.toml              # Dependencias modernas de Python
└── README.md                   # Documentación principal
```

---

## 🚀 Guía de Ejecución

### 1. Ingesta y Preprocesamiento (Python)
Desde la raíz del proyecto, inicializa el entorno virtual, genera el dataset y prepara los pesos:
```bash
uv run src_python/01_data_generator.py
uv run src_python/02_preprocessor.py
```
*Esto poblará la carpeta `data/` con `dataset_estudiantes.csv` y los archivos de metadatos requeridos por C++.*

### 2. Cálculo de la Matriz NCD y MST (C++)
Construye el núcleo matemático y ejecuta los algoritmos de procesamiento de grafos:
```bash
cd src_cpp
mkdir -p build && cd build
cmake ..
make

# Ejecutar el análisis matemático principal:
./ncd_mst_main
```
*El sistema generará la matriz densa de distancias y exportará las aristas óptimas calculadas por Prim y Kruskal en la carpeta `output/`.*

### 3. Renderizado del Grafo Final (Python)
Regresa a la raíz del proyecto y genera la visualización de los clústeres:
```bash
cd ../../
uv run src_python/04_visualizer.py
```
*Abre `output/mst_graph.png` para visualizar la topología de la información. Verás qué variables del rendimiento estudiantil agrupan características similares de acuerdo a su entropía computacional.*

---

## 📊 Fundamento Teórico

La **Distancia de Compresión Normalizada (NCD)** es una aproximación computable a la incalculable Distancia de Información de Kolmogorov. Se define algorítmicamente como:

```math
NCD(x, y) = \frac{C(x, y) - \min(C(x), C(y))}{\max(C(x), C(y))}
```

Donde `C(x)` representa el tamaño de bytes comprimidos de la variable `x`. A diferencia de la correlación de Pearson o Spearman, NCD permite encontrar la similitud universal entre cualquier tipo de estructura de datos subyacente (texto puro, variables continuas, discretas o binarias) sin requerir normalización estadística previa, dejando que la entropía hable por sí misma. Finalmente, las relaciones óptimas se desentrañan usando la Teoría de Grafos mediante un **Árbol de Expansión Mínima**.
