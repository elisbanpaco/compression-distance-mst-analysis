# 🎓 Análisis de Relaciones de Variables mediante Distancia de Compresión (NCD + MST)

![Python](https://img.shields.io/badge/Python-3.13%2B-blue?logo=python)
![C++](https://img.shields.io/badge/C%2B%2B-17-00599C?logo=c%2B%2B)
![CMake](https://img.shields.io/badge/CMake-Ready-green?logo=cmake)
![License](https://img.shields.io/badge/License-GPLv3-blue.svg)

Este proyecto implementa un enfoque novedoso y robusto de **Machine Learning No Supervisado** basado en la **Teoría de la Información** y la **Entropía de la Información** para descubrir patrones subyacentes y relaciones complejas (tanto lineales como no lineales) entre variables mixtas (numéricas, categóricas, texto y fechas).

Para lograr esto, el sistema calcula la **Distancia de Compresión Normalizada (NCD)** como métrica de similitud universal y extrae la topología óptima de conexiones mediante el **Árbol de Expansión Mínima (MST)**, aplicando algoritmos de **Prim** y **Kruskal** optimizados en C++.

---

## 🧠 Fundamento Teórico y Algorítmico

### 1. Distancia de Compresión Normalizada (NCD)
La NCD es una métrica de distancia no paramétrica basada en la complejidad algorítmica de Kolmogorov. Dado que la complejidad de Kolmogorov $K(x)$ es una función no computable, se aproxima mediante el tamaño del archivo resultante al procesar la información con un compresor real $C$ como GZip. La NCD entre dos variables $X$ e $Y$ se expresa formalmente como:

$$NCD(X, Y) = \frac{C(XY) - \min(C(X), C(Y))}{\max(C(X), C(Y))}$$

Donde:
* $C(X)$ es el tamaño comprimido en bytes de la variable $X$ serializada individualmente.
* $C(Y)$ es el tamaño comprimido en bytes de la variable $Y$ serializada individualmente.
* $C(XY)$ es el tamaño comprimido en bytes al concatenar y comprimir conjuntamente $X$ e $Y$.
* El valor de NCD está acotado teóricamente entre $0$ (identidad informativa) y $1$ (independencia informativa total).

### 2. Árbol de Expansión Mínima (MST)
Una vez calculada la matriz de distancias NCD de todas las variables contra todas (matriz simétrica de tamaño $V \times V$), representamos las variables como nodos en un grafo completamente conectado donde el peso de cada arista es la distancia NCD. 

Para extraer la estructura vertebral del sistema de variables sin ciclos y de manera óptima, se extrae el MST. Este árbol conecta todos los nodos de forma tal que la suma total de las distancias (pesos) sea mínima. El proyecto implementa dos algoritmos clásicos de grafos:
* **Algoritmo de Prim**: Crece el árbol nodo a nodo a partir de un vértice inicial seleccionando siempre la arista más barata.
* **Algoritmo de Kruskal**: Ordena todas las aristas y las une si no forman ciclos, apoyándose en una estructura de datos eficiente de conjuntos disjuntos (**Union-Find** o **Disjoint-Set**).

---

## ⚙️ Requisitos del Sistema

* **Python 3.13+** y el gestor de paquetes moderno [uv](https://github.com/astral-sh/uv).
* **Compilador compatible con C++17** (ej. `g++`, `clang++`).
* **CMake** (v3.10 o superior) para la compilación del core C++.
* **Librerías del Sistema**: `zlib` para la compresión gzip estándar (por defecto disponible en la mayoría de sistemas Linux/macOS).

---

## 📂 Estructura del Proyecto

El repositorio está organizado de la siguiente manera:

```text
compression-distance-mst-analysis/
├── data/                               # Datos y archivos de pesos intermedios
│   ├── dataset_estudiantes.csv         # Dataset principal (18,000 registros x 11 variables)
│   ├── weights_[PARTICION].csv         # Pesos de compresión (C_X, C_Y, C_XY) por partición
│   └── hierarchical_comprimidas/       # Archivos de texto temporales usados en la compresión
├── output/                             # Resultados del análisis estudiantil
│   ├── ncd_distances_[PARTICION].csv   # Matrices de distancias NCD en CSV
│   ├── mst_edges_prim_[PARTICION].csv  # Aristas del MST usando el algoritmo de Prim
│   ├── mst_edges_kruskal_[PARTICION].csv # Aristas del MST usando el algoritmo de Kruskal
│   ├── mst_hierarchical_comparison.png # Gráfico comparativo de los MSTs de las particiones
│   └── topology_comparison_report.txt  # Análisis de variabilidad de las topologías
├── src_python/                         # Componentes en Python de orquestación y análisis
│   ├── 01_data_generator.py            # Generador de datos sintéticos estudiantiles
│   ├── 02_preprocessor.py              # Preprocesador global (no segmentado)
│   ├── 02b_hierarchical_preprocessor.py # Preprocesador jerárquico segmentado por notas
│   ├── 04_visualizer.py                # Visualizador de grafos globales
│   ├── 04b_hierarchical_visualizer.py  # Visualizador de grafos por partición
│   └── 05b_topology_comparator.py      # Comparador analítico de topologías
├── src_cpp/                            # Core matemático de alto rendimiento en C++17
│   ├── edge.h                          # Estructura y abstracción de aristas
│   ├── prim.h                          # Implementación matemática del algoritmo de Prim
│   ├── kruskal.h                       # Implementación matemática del algoritmo de Kruskal
│   ├── main.cpp                        # Orquestador del cálculo NCD/MST global
│   ├── hierarchical_main.cpp           # Orquestador del cálculo NCD/MST jerárquico
│   └── CMakeLists.txt                  # Configuración de compilación CMake
├── run_pipeline.py                     # Script orquestador principal del análisis estudiantil
├── pyproject.toml                      # Declaración de dependencias del entorno Python
└── README.md                           # Documento de documentación raíz
```

---

## 🚀 Guía de Ejecución

### Pipeline Estudiantil Jerárquico

Este pipeline segmenta a los estudiantes según su rendimiento académico (`Notas`) en $N$ particiones (por defecto, $N = 8$: 4 subgrupos de mejor desempeño "Best" `B8C1` a `B8C4`, y 4 subgrupos de menor desempeño "Worst" `W8C1` a `W8C4`). Esto permite observar cómo muta la topología de relaciones entre variables (como horas de estudio, acceso a internet, horas de sueño, etc.) según el desempeño académico.

#### 1. Generar el Dataset Estudiantil
Si no tienes el archivo `data/dataset_estudiantes.csv` (18,000 registros y 11 variables mixtas), genéralo mediante:
```bash
uv run src_python/01_data_generator.py
```

#### 2. Ejecutar el Pipeline Automatizado
Para compilar automáticamente el motor C++, preprocesar los datos por partición, calcular NCD y MST y generar el reporte comparativo, ejecuta:
```bash
uv run run_pipeline.py
```
Este comando:
1. Limpia los directorios intermedios y de salida (`data/` y `output/`).
2. Ejecuta el preprocesador jerárquico segmentando por cuartiles/octiles (`02b_hierarchical_preprocessor.py`).
3. Compila el motor C++ en `src_cpp/build` usando CMake y ejecuta `./ncd_mst_hierarchical` para procesar todas las particiones con un rendimiento de milisegundos.
4. Genera la visualización del grid de grafos en `output/mst_hierarchical_comparison.png`.
5. Ejecuta el comparador de topologías y produce el informe de diferencias en `output/topology_comparison_report.txt`.

---

## 📊 Interpretación de Resultados y Volatilidad Topológica

El análisis de volatilidad topológica (calculado por `05b_topology_comparator.py` e impreso en `output/topology_comparison_report.txt`) utiliza la **distancia de camino más corto en el MST** entre todas las variables. Para cada nodo (variable), se calcula la suma de distancias a todos los demás nodos.

### Cómo leer las diferencias ($B8C2 - B8C1$):
* **Una diferencia positiva (MÁXIMO)** significa que una variable se ha alejado (está más desconectada o es más independiente) en la segunda topología en comparación con la primera.
* **Una diferencia negativa (MÍNIMO)** indica que la variable se ha acercado (ha ganado relevancia o dependencia informativa) en la red de variables.

**Ejemplo práctico:**
En los resultados estudiantiles, es común notar cómo variables conductuales como `Acceso_Internet` o `Horas_Estudio` cambian drásticamente de posición en el MST de estudiantes de alto rendimiento (donde están estrechamente ligadas a las notas o horas de sueño) vs. estudiantes de bajo rendimiento (donde pueden estar ligadas de forma caótica a la latitud geográfica o edad).

---

## 🛠️ Desarrollo y Compilación Manual (C++)

Si deseas construir el núcleo matemático C++ de forma aislada para pruebas o desarrollos adicionales:

```bash
cd src_cpp
mkdir -p build
cd build
cmake ..
make
```

Esto generará dos binarios ejecutables:
* `./ncd_mst_main`: Procesa el archivo de pesos global `data/compression_weights.csv`.
* `./ncd_mst_hierarchical`: Procesa iterativamente todos los archivos `data/weights_*.csv` generados en el pipeline por partición.

---

## 📄 Licencia
Este proyecto está bajo la Licencia GNU GPL v3.0. Consulta el archivo [LICENSE](LICENSE) para más detalles.
