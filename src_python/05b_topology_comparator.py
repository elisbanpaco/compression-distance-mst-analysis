import os
import glob
import csv
import itertools
import networkx as nx

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
            diffs[node] = sumsB[node] - sumsA[node]
            
        # Máximo absoluto o máximo incremento
        max_node = max(diffs, key=diffs.get)
        
        # Mínimo de los que son mayores a cero (> 0)
        positive_diffs = {k: v for k, v in diffs.items() if v > 0}
        if positive_diffs:
            min_node = min(positive_diffs, key=positive_diffs.get)
            min_val = positive_diffs[min_node]
        else:
            min_node = None
            min_val = None
            
        comparisons.append({
            'TopA': topA,
            'TopB': topB,
            'Diffs': diffs,
            'MaxNode': max_node,
            'MaxVal': diffs[max_node],
            'MinNode': min_node,
            'MinVal': min_val
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
            msg_max = f"  -> MÁXIMO INCREMENTO: Nodo '{comp['MaxNode']}' con un aumento de +{comp['MaxVal']:.4f}"
            print(msg_max)
            f.write(msg_max + "\n")
            
            # Imprimir MÍNIMO (> 0)
            if comp['MinNode']:
                msg_min = f"  -> MÍNIMO INCREMENTO (> 0): Nodo '{comp['MinNode']}' con un aumento de +{comp['MinVal']:.4f}"
            else:
                msg_min = "  -> MÍNIMO INCREMENTO (> 0): Ningún nodo tuvo un incremento mayor a 0."
            print(msg_min)
            f.write(msg_min + "\n")
            
            print("  Detalle de diferencias por nodo (todas las filas):")
            f.write("  Detalle de diferencias por nodo:\n")
            
            sorted_diffs = sorted(comp['Diffs'].items(), key=lambda item: item[1], reverse=True)
            
            for node, val in sorted_diffs:
                print(f"     {node:<20} : {val:+.4f}")
                f.write(f"     {node:<20} : {val:+.4f}\n")
            
            print()
            f.write("\n")
            
    print(f"Proceso completado. Reporte detallado guardado en: {report_path}")

if __name__ == "__main__":
    main()
