import os
import glob
import csv
import itertools
import networkx as nx
import json

OUTPUT_DIR = "output"

def load_topologies():
    pattern = os.path.join(OUTPUT_DIR, "mst_edges_kruskal*.csv")
    files = glob.glob(pattern)
    
    topologies = {}
    all_nodes = set()
    
    for file_path in files:
        filename = os.path.basename(file_path)
        name = filename.replace("mst_edges_kruskal_", "").replace(".csv", "")
        if name == "mst_edges_kruskal" or name == "":
            name = "Base"
        
        G = nx.Graph()
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                u = row['Source']
                v = row['Target']
                w = float(row['Weight'])
                G.add_edge(u, v, weight=w)
                all_nodes.add(u)
                all_nodes.add(v)
                
        topologies[name] = G
        
    return topologies, sorted(list(all_nodes))

def compute_all_pairs_distances(topologies, nodes):
    """Calcula la distancia de ruta en el MST entre cada par de nodos."""
    topo_distances = {}
    for name, G in topologies.items():
        distances = {}
        path_lengths = dict(nx.all_pairs_dijkstra_path_length(G, weight='weight'))
        for u, v in itertools.combinations(nodes, 2):
            pair = tuple(sorted([u, v]))
            try:
                dist = path_lengths[pair[0]][pair[1]]
            except KeyError:
                dist = float('inf')
            distances[pair] = dist
        topo_distances[name] = distances
    return topo_distances

def compute_row_sums(topo_distances, nodes):
    """
    Simula la matriz simétrica completa y suma los valores por fila (por nodo).
    Retorna un diccionario con la suma total de distancias para cada nodo.
    """
    topo_sums = {}
    for name, distances in topo_distances.items():
        sums = {node: 0.0 for node in nodes}
        for u, v in itertools.combinations(nodes, 2):
            pair = tuple(sorted([u, v]))
            dist = distances[pair]
            # Como es matriz simétrica, la distancia aporta a la fila de 'u' y a la fila de 'v'
            sums[u] += dist
            sums[v] += dist
        topo_sums[name] = sums
    return topo_sums

def compare_topologies(topo_sums):
    comparisons = []
    
    names = sorted(list(topo_sums.keys()))
    for topA, topB in itertools.combinations(names, 2):
        sumsA = topo_sums[topA]
        sumsB = topo_sums[topB]
        
        diffs = {}
        for node in sumsA.keys():
            diffs[node] = abs(sumsB[node] - sumsA[node])
            
        # Mayor cambio (absoluto)
        max_node = max(diffs, key=diffs.get)

        # Menor cambio (absoluto)
        min_node = min(diffs, key=diffs.get)
            
        comparisons.append({
            'TopA': topA,
            'TopB': topB,
            'Diffs': diffs,
            'MaxNode': max_node,
            'MaxVal': diffs[max_node],
            'MinNode': min_node,
            'MinVal': diffs[min_node]
        })
        
    return comparisons

def main():
    print("--- Comparador Analítico de Topologías MST (Suma de Filas) ---")
    topologies, nodes = load_topologies()
    
    if not topologies:
        print("No se encontraron archivos de topología en output/.")
        return
        
    print(f"Nodos detectados ({len(nodes)}): {', '.join(nodes)}")
    print(f"Topologías cargadas ({len(topologies)}): {', '.join(topologies.keys())}")
    print()
    
    # 1. Distancias reales de rutas
    topo_distances = compute_all_pairs_distances(topologies, nodes)
    
    # 2. Suma por filas de la matriz simétrica completa
    print("[*] Calculando matriz completa y sumando por filas (nodos)...")
    topo_sums = compute_row_sums(topo_distances, nodes)
        
    # 3. Comparar las sumas
    print("[*] Comparando sumas totales por nodo entre topologías...")
    comparisons = compare_topologies(topo_sums)
    
    # 4. Reporte
    print("--- Resultados de Comparación (Todos contra Todos) ---")
    report_path = os.path.join(OUTPUT_DIR, "topology_comparison_report.txt")
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("REPORTE DE COMPARACIÓN DE DISTANCIAS TOTALES POR NODO (MST)\n")
        f.write("===========================================================\n")
        f.write("Basado en la suma por filas de la matriz simétrica completa.\n\n")
        
        for comp in comparisons:
            topA = comp['TopA']
            topB = comp['TopB']
            
            header = f"Comparación: {topB} vs {topA} (Diferencia = {topB} - {topA})"
            print(header)
            f.write(header + "\n")
            
            # Imprimir MÁXIMO
            msg_max = f"  -> MAYOR CAMBIO (ABS): Nodo '{comp['MaxNode']}' con una diferencia de {comp['MaxVal']:.4f}"
            print(msg_max)
            f.write(msg_max + "\n")
            
            # Imprimir MÍNIMO
            msg_min = f"  -> MENOR CAMBIO (ABS): Nodo '{comp['MinNode']}' con una diferencia de {comp['MinVal']:.4f}"
            print(msg_min)
            f.write(msg_min + "\n")
            
            print("  Detalle de diferencias por nodo (todas las filas):")
            f.write("  Detalle de diferencias por nodo:\n")
            
            sorted_diffs = sorted(comp['Diffs'].items(), key=lambda item: item[1], reverse=True)
            
            for node, val in sorted_diffs:
                print(f"     {node:<20} : {val:.4f}")
                f.write(f"     {node:<20} : {val:.4f}\n")
            
            print()
            f.write("\n")
            
    # Exportar JSON para que otros scripts (como 06b_insights) lo lean fácilmente
    json_path = os.path.join(OUTPUT_DIR, "topology_comparisons.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(comparisons, f, indent=4)
            
    print(f"Proceso completado. Reporte detallado guardado en: {report_path}")
    print(f"Datos exportados en JSON para insights: {json_path}")

if __name__ == "__main__":
    main()