#ifndef PRIM_H
#define PRIM_H

#include <vector>
#include <iostream>
#include <limits>
#include "edge.h"

using namespace std;

inline vector<Edge> compute_mst_prim(const vector<vector<float>>& matrix) {
    size_t V = matrix.size();
    vector<Edge> mst;
    mst.reserve(V - 1);
    
    vector<bool> in_mst(V, false);
    vector<float> min_weight(V, numeric_limits<float>::max());
    vector<int> parent(V, -1);
    
    min_weight[0] = 0.0f;
    cout << "[MST-PRIM] Construyendo el Arbol de Expansion Minima (Prim)...\n";
    
    for (size_t count = 0; count < V; ++count) {
        float min_val = numeric_limits<float>::max();
        int u = -1;
        
        for (size_t v = 0; v < V; ++v) {
            if (!in_mst[v] && min_weight[v] < min_val) {
                min_val = min_weight[v];
                u = v;
            }
        }
        
        if (u == -1) break;
        in_mst[u] = true;
        
        if (parent[u] != -1) {
            mst.push_back({parent[u], u, matrix[u][parent[u]]});
        }
        
        for (size_t v = 0; v < V; ++v) {
            if (!in_mst[v] && matrix[u][v] < min_weight[v] && u != v) {
                min_weight[v] = matrix[u][v];
                parent[v] = static_cast<int>(u);
            }
        }
    }
    return mst;
}

#endif // PRIM_H
