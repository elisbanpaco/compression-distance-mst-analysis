#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <algorithm>
#include <sstream>
#include <map>
#include "prim.h"
#include "kruskal.h"

using namespace std;

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

// ---------------------------------------------------------
// 2. MAIN ENTRY POINT
// ---------------------------------------------------------
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

int main(int argc, char** argv) {
    cout << "===============================================\n";
    cout << "  NCD & MST CORE (VARIABLES CORRELATION) \n";
    cout << "===============================================\n\n";

    // Deteccion robusta del directorio base
    string data_dir = "../../data/";
    string out_dir = "../../output/";
    
    ifstream test_file("../../data/compression_weights.csv");
    if (!test_file.is_open()) {
        data_dir = "../data/";
        out_dir = "../output/";
    } else {
        test_file.close();
    }

    string input_file = data_dir + "compression_weights.csv";
    ifstream file(input_file);
    if (!file.is_open()) {
        cerr << "[ERROR] No se pudo abrir " << input_file << "\n";
        return 1;
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
    
    string ncd_out_file = out_dir + "ncd_distances.csv";
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
    cout << "\n--- RUTA 1: ALGORITMO PRIM ---\n";
    auto mst_prim = compute_mst_prim(matrix);
    string prim_out = out_dir + "mst_edges_prim.csv";
    save_mst_to_csv(mst_prim, prim_out, var_names);
    if(ifstream(prim_out)) {
        cout << "[EXITO] Aristas PRIM exportadas en " << prim_out << "\n";
    }

    // 3. Kruskal
    cout << "\n--- RUTA 2: ALGORITMO KRUSKAL ---\n";
    auto mst_kruskal = compute_mst_kruskal(matrix);
    string kruskal_out = out_dir + "mst_edges_kruskal.csv";
    save_mst_to_csv(mst_kruskal, kruskal_out, var_names);
    if(ifstream(kruskal_out)) {
        cout << "[EXITO] Aristas KRUSKAL exportadas en " << kruskal_out << "\n";
    }

    cout << "\n[EXITO] Ejecucion completada satisfactoriamente.\n";
    return 0;
}
