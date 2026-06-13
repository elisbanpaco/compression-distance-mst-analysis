import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import os

def visualize_mst(input_csv="../../output/mst_edges.csv", output_png="../../output/mst_graph.png"):
    """
    Lee las aristas del Árbol de Expansión Mínima generadas por C++ 
    y renderiza un grafo visual.
    """
    print(f"[*] Leyendo aristas del MST desde: {input_csv}...")
    if not os.path.exists(input_csv):
        print("[ERROR] El archivo MST no existe. Corre el ejecutable de C++ primero.")
        return
        
    df_edges = pd.read_csv(input_csv)
    
    print("[*] Construyendo el grafo NetworkX...")
    G = nx.Graph()
    
    for idx, row in df_edges.iterrows():
        # Añadir arista. En networkx, weight más bajo significa más "cercano".
        G.add_edge(int(row['Source']), int(row['Target']), weight=row['Weight'])
        
    print(f"[+] Grafo creado con {G.number_of_nodes()} nodos y {G.number_of_edges()} aristas.")
    
    print("[*] Calculando disposición (Layout) para el renderizado (puede tomar unos segundos)...")
    # Usamos spring_layout que agrupa nodos conectados por pesos (distancias) cortos
    # K ajusta la distancia óptima entre nodos.
    pos = nx.spring_layout(G, k=0.15, iterations=50, seed=42)
    
    plt.figure(figsize=(16, 12))
    plt.title("Árbol de Expansión Mínima (NCD - Rendimiento Escolar)", fontsize=20, fontweight='bold')
    
    # Dibujar las aristas con una transparencia sutil
    nx.draw_networkx_edges(G, pos, alpha=0.3, edge_color='#555555')
    
    # Dibujar los nodos con un color llamativo
    nx.draw_networkx_nodes(G, pos, node_size=30, node_color='#00b4d8', alpha=0.8, edgecolors='white')
    
    plt.axis('off')
    
    os.makedirs(os.path.dirname(output_png), exist_ok=True)
    plt.savefig(output_png, format='png', dpi=300, bbox_inches='tight')
    print(f"[+] Visualización guardada exitosamente en: {output_png}")
    plt.close()

if __name__ == "__main__":
    # Ajustar rutas si el script se corre desde la raíz del proyecto
    if os.path.exists("output/mst_edges.csv"):
        visualize_mst("output/mst_edges.csv", "output/mst_graph.png")
    else:
        visualize_mst()
