#ifndef KRUSKAL_H
#define KRUSKAL_H

#include <vector>
#include <iostream>
#include <algorithm>
#include "edge.h"

struct DisjointSet {
    std::vector<int> parent, rank;
    DisjointSet(int n) {
        parent.resize(n);
        rank.resize(n, 0);
        for(int i = 0; i < n; ++i) parent[i] = i;
    }
    int find(int i) {
        if (parent[i] == i) return i;
        return parent[i] = find(parent[i]); 
    }
    bool unite(int i, int j) {
        int root_i = find(i);
        int root_j = find(j);
        if (root_i != root_j) {
            if (rank[root_i] < rank[root_j]) {
                parent[root_i] = root_j;
            } else if (rank[root_i] > rank[root_j]) {
                parent[root_j] = root_i;
            } else {
                parent[root_j] = root_i;
                rank[root_i]++;
            }
            return true;
        }
        return false;
    }
};

inline std::vector<Edge> compute_mst_kruskal(const std::vector<std::vector<float>>& matrix) {
    size_t V = matrix.size();
    std::vector<Edge> all_edges;
    size_t total_edges = (V * (V - 1)) / 2;
    all_edges.reserve(total_edges);

    std::cout << "[MST-KRUSKAL] Extrayendo " << total_edges << " aristas de la matriz...\n";
    for (size_t i = 0; i < V; ++i) {
        for (size_t j = i + 1; j < V; ++j) {
            all_edges.push_back({static_cast<int>(i), static_cast<int>(j), matrix[i][j]});
        }
    }

    std::cout << "[MST-KRUSKAL] Ordenando aristas por peso...\n";
    std::sort(all_edges.begin(), all_edges.end(), [](const Edge& a, const Edge& b) {
        return a.weight < b.weight;
    });

    std::vector<Edge> mst;
    mst.reserve(V - 1);
    DisjointSet ds(V);

    std::cout << "[MST-KRUSKAL] Evaluando aristas con Disjoint-Set...\n";
    for (const auto& edge : all_edges) {
        if (ds.unite(edge.u, edge.v)) {
            mst.push_back(edge);
            if (mst.size() == V - 1) break;
        }
    }
    return mst;
}

#endif // KRUSKAL_H
