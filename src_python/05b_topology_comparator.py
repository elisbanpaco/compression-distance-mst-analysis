import os
import glob
import csv
import itertools

OUTPUT_DIR = "output"

def load_topologies():
    # Load all Kruskal MST edge files to compare
    # We can also compare Prim, but Kruskal is a standard representation here
    pattern = os.path.join(OUTPUT_DIR, "mst_edges_kruskal*.csv")
    files = glob.glob(pattern)
    
    topologies = {}
    all_nodes = set()
    
    for file_path in files:
        # Extract topology name from filename
        filename = os.path.basename(file_path)
        name = filename.replace("mst_edges_kruskal", "Top").replace(".csv", "")
        if name == "Top":
            name = "Top_Base"
        else:
            name = name.replace("Top_", "Top_")
        
        edges = []
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                u = row['Source']
                v = row['Target']
                w = float(row['Weight'])
                edges.append((u, v, w))
                all_nodes.add(u)
                all_nodes.add(v)
                
        topologies[name] = edges
        
    return topologies, sorted(list(all_nodes))

def compute_upper_triangular_sums(topologies, nodes):
    # This computes the row sums of the upper triangular matrix
    # based on the alphabetical order of nodes (X1, X2, ... Xn)
    
    topo_sums = {}
    for name, edges in topologies.items():
        # Initialize sums to 0 for all nodes
        sums = {node: 0.0 for node in nodes}
        
        for u, v, w in edges:
            # Ensure u comes before v in our sorted nodes list
            # to simulate the upper triangular matrix
            if nodes.index(u) > nodes.index(v):
                u, v = v, u
            
            # Add weight to the "row" node (the one that comes first)
            sums[u] += w
            
        topo_sums[name] = sums
        
    return topo_sums

def compare_topologies(topo_sums, nodes):
    comparisons = []
    
    # Compare all pairs (A, B)
    names = sorted(list(topo_sums.keys()))
    for topA, topB in itertools.combinations(names, 2):
        sumsA = topo_sums[topA]
        sumsB = topo_sums[topB]
        
        diffs = {}
        for node in nodes:
            diffs[node] = sumsB[node] - sumsA[node]
            
        max_node = max(diffs, key=diffs.get)
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
    print("--- Comparador de Topologías MST ---")
    topologies, nodes = load_topologies()
    
    if not topologies:
        print("No se encontraron archivos de topología (mst_edges_kruskal*.csv) en la carpeta output/.")
        return
        
    print(f"Nodos detectados ({len(nodes)}): {', '.join(nodes)}")
    print(f"Topologías cargadas ({len(topologies)}): {', '.join(topologies.keys())}")
    print()
    
    # 1. Calcular sumas triangulares superiores
    topo_sums = compute_upper_triangular_sums(topologies, nodes)
    
    # Imprimir las sumas por topología
    for name in sorted(topo_sums.keys()):
        print(f"Sumas de Matriz Triangular para {name}:")
        for node in nodes:
            val = topo_sums[name][node]
            if val > 0:
                print(f"  Row {node}: {val:.4f}")
            else:
                print(f"  Row {node}: 0")
        print()
        
    # 2. Comparar pares de topologías
    comparisons = compare_topologies(topo_sums, nodes)
    
    # 3. Reportar los resultados
    print("--- Resultados de Comparación (Todos contra Todos) ---")
    report_path = os.path.join(OUTPUT_DIR, "topology_comparison_report.txt")
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("REPORTE DE COMPARACIÓN DE TOPOLOGÍAS\n")
        f.write("====================================\n\n")
        
        for comp in comparisons:
            topA = comp['TopA']
            topB = comp['TopB']
            max_node = comp['MaxNode']
            max_val = comp['MaxVal']
            min_node = comp['MinNode']
            min_val = comp['MinVal']
            
            header = f"Comparación: {topB} vs {topA} ({topB} - {topA})"
            print(header)
            f.write(header + "\n")
            
            print(f"  -> MAX (Mayor incremento): {max_node} con una diferencia de {max_val:+.4f}")
            f.write(f"  -> MAX (Mayor incremento): {max_node} con una diferencia de {max_val:+.4f}\n")
            
            print(f"  -> MIN (Mayor disminución): {min_node} con una diferencia de {min_val:+.4f}")
            f.write(f"  -> MIN (Mayor disminución): {min_node} con una diferencia de {min_val:+.4f}\n")
            
            print("  Detalle de diferencias por nodo:")
            f.write("  Detalle de diferencias por nodo:\n")
            for node in nodes:
                val = comp['Diffs'][node]
                print(f"     {node}: {val:+.4f}")
                f.write(f"     {node}: {val:+.4f}\n")
            
            print()
            f.write("\n")
            
    print(f"Proceso completado. Reporte guardado en: {report_path}")

if __name__ == "__main__":
    main()
