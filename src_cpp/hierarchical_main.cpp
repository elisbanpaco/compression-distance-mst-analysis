#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <algorithm>
#include <sstream>
#include <map>
#include <filesystem>
#include "prim.h"
#include "kruskal.h"

using namespace std;
namespace fs = std::filesystem;

// ---------------------------------------------------------
// 1. HELPERS
// ---------------------------------------------------------
vector<string> split(const string& str, char delim) {
    vector<string> tokens;
    string token;
    istringstream tokenStream(str);
    while (getline(tokenStream, token, delim)) {
        tokens.push_back(token);
    }
    return tokens;
}

void save_mst_to_csv(const vector<Edge>& mst, const string& filename, const vector<string>& var_names) {
    ofstream out_mst(filename);
    if (!out_mst.is_open()) {
        cerr << "[ERROR] Fallo al abrir: " << filename << "\n";
        return;
    }
    out_mst << "Source,Target,Weight\n";
    for (const auto& edge : mst) {
        out_mst << var_names[edge.u] << "," << var_names[edge.v] << "," << edge.weight << "\n";
    }
    out_mst.close();
}

// ---------------------------------------------------------
// 2. CORE PROCESSING FUNCTION
// ---------------------------------------------------------
void process_chunk(const string& input_file, const string& chunk_name, const string& out_dir) {
    ifstream file(input_file);
    if (!file.is_open()) {
        cerr << "[ERROR] No se pudo abrir " << input_file << "\n";
        return;
    }

    string line;
    // Skip header
    getline(file, line);

    vector<string> var_names;
    map<string, int> var_to_idx;
    
    struct Record {
        int u, v;
        float c_x, c_y, c_xy;
    };
    
    vector<Record> records;

    while (getline(file, line)) {
        if (line.empty()) continue;
        auto tokens = split(line, ',');
        if (tokens.size() < 5) continue;
        
        string var1 = tokens[0];
        string var2 = tokens[1];
        float c_x = stof(tokens[2]);
        float c_y = stof(tokens[3]);
        float c_xy = stof(tokens[4]);
        
        if (var_to_idx.find(var1) == var_to_idx.end()) {
            var_to_idx[var1] = var_names.size();
            var_names.push_back(var1);
        }
        if (var_to_idx.find(var2) == var_to_idx.end()) {
            var_to_idx[var2] = var_names.size();
            var_names.push_back(var2);
        }
        
        records.push_back({var_to_idx[var1], var_to_idx[var2], c_x, c_y, c_xy});
    }
    file.close();

    size_t V = var_names.size();
    cout << "[INFO] Se cargaron " << V << " variables y " << records.size() << " combinaciones.\n";

    // 1. Matriz NCD
    vector<vector<float>> matrix(V, vector<float>(V, 0.0f));
    
    string ncd_out_file = out_dir + "ncd_distances_" + chunk_name + ".csv";
    ofstream out_ncd(ncd_out_file);
    if (out_ncd.is_open()) {
        out_ncd << "Var1,Var2,NCD_Weight\n";
    }

    cout << "[NCD] Calculando matriz NCD...\n";
    for (const auto& rec : records) {
        float min_c = min(rec.c_x, rec.c_y);
        float max_c = max(rec.c_x, rec.c_y);
        float ncd = (rec.c_xy - min_c) / max_c;
        matrix[rec.u][rec.v] = ncd;
        matrix[rec.v][rec.u] = ncd;
        
        if (out_ncd.is_open()) {
            out_ncd << var_names[rec.u] << "," << var_names[rec.v] << "," << ncd << "\n";
        }
    }
    
    if (out_ncd.is_open()) {
        out_ncd.close();
        cout << "[EXITO] Distancias NCD exportadas a " << ncd_out_file << "\n";
    }

    // 2. Prim
    cout << "--- RUTA 1: ALGORITMO PRIM ---\n";
    auto mst_prim = compute_mst_prim(matrix);
    string prim_out = out_dir + "mst_edges_prim_" + chunk_name + ".csv";
    save_mst_to_csv(mst_prim, prim_out, var_names);
    cout << "[EXITO] Aristas PRIM exportadas en " << prim_out << "\n";

    // 3. Kruskal
    cout << "--- RUTA 2: ALGORITMO KRUSKAL ---\n";
    auto mst_kruskal = compute_mst_kruskal(matrix);
    string kruskal_out = out_dir + "mst_edges_kruskal_" + chunk_name + ".csv";
    save_mst_to_csv(mst_kruskal, kruskal_out, var_names);
    cout << "[EXITO] Aristas KRUSKAL exportadas en " << kruskal_out << "\n";
}

// ---------------------------------------------------------
// 3. MAIN ENTRY POINT (HIERARCHICAL)
// ---------------------------------------------------------
int main(int argc, char** argv) {
    cout << "===============================================\n";
    cout << "  NCD & MST CORE (CLUSTERING JERÁRQUICO) \n";
    cout << "===============================================\n\n";

    // Deteccion robusta del directorio base
    string data_dir = "../../data/";
    string out_dir = "../../output/";
    
    if (!fs::exists(data_dir)) {
        data_dir = "../data/";
        out_dir = "../output/";
    }

    if (!fs::exists(out_dir)) {
        fs::create_directories(out_dir);
    }

    vector<string> weight_files;
    for (const auto& entry : fs::directory_iterator(data_dir)) {
        if (entry.is_regular_file()) {
            string filename = entry.path().filename().string();
            // Buscar solo los archivos generados por el pipeline jerárquico
            if (filename.find("weights_") == 0 && filename.find(".csv") != string::npos && filename != "compression_weights.csv") {
                weight_files.push_back(filename);
            }
        }
    }

    if (weight_files.empty()) {
        cerr << "[ERROR] No se encontraron archivos weights_*.csv en " << data_dir << "\n";
        return 1;
    }

    for (const string& filename : weight_files) {
        // Extraer chunk_name (ej: "B2C1" de "weights_B2C1.csv")
        size_t pos1 = filename.find('_') + 1;
        size_t pos2 = filename.find(".csv");
        string chunk_name = filename.substr(pos1, pos2 - pos1);
        
        cout << "\n===============================================\n";
        cout << "  PROCESANDO PARTICIÓN: " << chunk_name << "\n";
        cout << "===============================================\n";
        
        process_chunk(data_dir + filename, chunk_name, out_dir);
    }

    cout << "\n[EXITO] Ejecucion completada satisfactoriamente para todas las particiones.\n";
    return 0;
}
