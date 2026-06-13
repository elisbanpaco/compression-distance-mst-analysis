#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <algorithm>
#include <zlib.h>
#include <omp.h>
#include "prim.h"
#include "kruskal.h"

// ---------------------------------------------------------
// 1. COMPRESSOR (ZLIB WRAPPER)
// ---------------------------------------------------------
size_t get_compressed_size(const std::string& data) {
    uLongf destLen = compressBound(data.size());
    std::vector<Bytef> dest(destLen);
    int res = compress(dest.data(), &destLen, reinterpret_cast<const Bytef*>(data.data()), data.size());
    if (res != Z_OK) {
        std::cerr << "Fallo al comprimir datos con zlib\n";
        exit(1);
    }
    return static_cast<size_t>(destLen);
}

// ---------------------------------------------------------
// 2. NCD MATH (OPENMP PARALLEL)
// ---------------------------------------------------------
std::vector<std::vector<float>> compute_ncd_matrix(const std::vector<std::string>& students) {
    size_t n = students.size();
    std::vector<size_t> c_sizes(n);
    
    std::cout << "[NCD] Pre-calculando tamanos comprimidos independientes...\n";
    #pragma omp parallel for
    for (size_t i = 0; i < n; ++i) {
        c_sizes[i] = get_compressed_size(students[i]);
    }

    std::vector<std::vector<float>> matrix(n, std::vector<float>(n, 0.0f));
    size_t total_pairs = (n * (n - 1)) / 2;
    std::cout << "[NCD] Calculando NCD para " << total_pairs << " pares en paralelo...\n";
    
    #pragma omp parallel for schedule(dynamic, 50)
    for (size_t i = 0; i < n; ++i) {
        if (i % 500 == 0) {
            #pragma omp critical
            std::cout << " -> Procesando estudiante " << i << " de " << n << "\n";
        }
        for (size_t j = i + 1; j < n; ++j) {
            size_t c_xy = get_compressed_size(students[i] + students[j]);
            size_t min_c = std::min(c_sizes[i], c_sizes[j]);
            size_t max_c = std::max(c_sizes[i], c_sizes[j]);
            
            float ncd = static_cast<float>(c_xy - min_c) / static_cast<float>(max_c);
            matrix[i][j] = ncd;
            matrix[j][i] = ncd;
        }
    }
    return matrix;
}

// ---------------------------------------------------------
// 3. MAIN ENTRY POINT
// ---------------------------------------------------------
void save_mst_to_csv(const std::vector<Edge>& mst, const std::string& filename) {
    std::ofstream out_mst(filename);
    if (!out_mst.is_open()) {
        std::cerr << "[ERROR] Fallo al abrir: " << filename << "\n";
        return;
    }
    out_mst << "Source,Target,Weight\n";
    for (const auto& edge : mst) {
        out_mst << edge.u << "," << edge.v << "," << edge.weight << "\n";
    }
    out_mst.close();
}

int main(int argc, char** argv) {
    std::cout << "===============================================\n";
    std::cout << "  NCD & MST CORE (HIGH-PERFORMANCE) \n";
    std::cout << "===============================================\n\n";

    std::string input_file = "../../data/students_serialized";
    std::ifstream file(input_file);
    if (!file.is_open()) {
        input_file = "../data/students_serialized";
        file.open(input_file);
        if(!file.is_open()) {
            std::cerr << "[ERROR] No se pudo abrir students_serialized\n";
            return 1;
        }
    }

    std::vector<std::string> students;
    std::string line;
    while (std::getline(file, line)) {
        if (!line.empty()) students.push_back(line);
    }
    file.close();

    size_t limit = students.size();
    if (argc > 1) {
        limit = std::stoull(argv[1]);
        if (limit < students.size()) students.resize(limit);
    }

    std::cout << "[INFO] Cargados " << limit << " estudiantes exitosamente.\n";
    if(students.size() > limit) students.resize(limit);

    // 1. Matriz NCD
    auto matrix = compute_ncd_matrix(students);

    // 2. Prim
    std::cout << "\n--- RUTA 1: ALGORITMO PRIM ---\n";
    auto mst_prim = compute_mst_prim(matrix);
    std::string prim_out = "../../output/mst_edges_prim.csv";
    save_mst_to_csv(mst_prim, prim_out);
    std::cout << "[EXITO] Aristas PRIM exportadas en " << prim_out << "\n";

    // 3. Kruskal
    std::cout << "\n--- RUTA 2: ALGORITMO KRUSKAL ---\n";
    auto mst_kruskal = compute_mst_kruskal(matrix);
    std::string kruskal_out = "../../output/mst_edges_kruskal.csv";
    save_mst_to_csv(mst_kruskal, kruskal_out);
    std::cout << "[EXITO] Aristas KRUSKAL exportadas en " << kruskal_out << "\n";

    std::cout << "\n[EXITO] Ejecucion completada satisfactoriamente.\n";
    return 0;
}
