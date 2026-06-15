import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import os

def visualize_mst(input_csv, output_png, title):
    """
    Lee las aristas del Árbol de Expansión Mínima generadas por C++ 
    y renderiza un grafo visual donde los nodos son las variables.
    """
    print(f"[*] Leyendo aristas del MST desde: {input_csv}...")
    if not os.path.exists(input_csv):
        print(f"[ERROR] El archivo MST no existe: {input_csv}")
        return
        
    df_edges = pd.read_csv(input_csv)
    
    print("[*] Construyendo el grafo NetworkX...")
    G = nx.Graph()
    
    for idx, row in df_edges.iterrows():
        # Añadir arista con nombres de variables
        G.add_edge(str(row['Source']), str(row['Target']), weight=row['Weight'])
        
    print(f"[+] Grafo creado con {G.number_of_nodes()} nodos y {G.number_of_edges()} aristas.")
    
    print("[*] Calculando disposición (Layout) para el renderizado...")
    # Usamos kamada_kawai_layout que es determinista y excelente para árboles (MST), 
    # garantizando que ambas gráficas se vean idénticas y bien distribuidas.
    pos = nx.kamada_kawai_layout(G)
    
    plt.figure(figsize=(14, 10))
    plt.title(title, fontsize=20, fontweight='bold')
    
    # Dibujar las aristas con una transparencia sutil y añadir los pesos como etiquetas
    nx.draw_networkx_edges(G, pos, alpha=0.5, edge_color='#555555', width=2)
    
    # Etiquetas de los pesos de las aristas
    edge_labels = {(str(row['Source']), str(row['Target'])): f"{row['Weight']:.3f}" for idx, row in df_edges.iterrows()}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=9, font_color='red')
    
    # Dibujar los nodos
    nx.draw_networkx_nodes(G, pos, node_size=800, node_color='#00b4d8', alpha=0.9, edgecolors='white', linewidths=2)
    
    # Dibujar las etiquetas (nombres de las variables)
    nx.draw_networkx_labels(G, pos, font_size=11, font_family="sans-serif", font_weight='bold')
    
    plt.axis('off')
    
    os.makedirs(os.path.dirname(output_png), exist_ok=True)
    plt.savefig(output_png, format='png', dpi=300, bbox_inches='tight')
    print(f"[+] Visualización guardada exitosamente en: {output_png}")
    plt.close()

if __name__ == "__main__":
    visualize_mst(
        input_csv="output/mst_edges_prim.csv", 
        output_png="output/mst_graph_prim.png",
        title="Árbol de Expansión Mínima (NCD - Prim)"
    )
    visualize_mst(
        input_csv="output/mst_edges_kruskal.csv", 
        output_png="output/mst_graph_kruskal.png",
        title="Árbol de Expansión Mínima (NCD - Kruskal)"
    )
