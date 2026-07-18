import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import os
import glob
import math
import argparse

def visualize_comparison_grid(mst_files, output_png):
    num_files = len(mst_files)
    if num_files == 0:
        return
        
    cols = 2
    rows = math.ceil(num_files / cols)
    
    fig, axes = plt.subplots(rows, cols, figsize=(10 * cols, 8 * rows))
    if num_files == 1:
        axes = [axes]
    else:
        axes = axes.flatten()
        
    for i, file_path in enumerate(mst_files):
        chunk_name = os.path.basename(file_path).replace("mst_edges_prim_", "").replace("mst_edges_kruskal_", "").replace(".csv", "")
        df_edges = pd.read_csv(file_path)
        G = nx.Graph()
        for _, row in df_edges.iterrows():
            G.add_edge(str(row['Source']), str(row['Target']), weight=row['Weight'])
            
        pos = nx.kamada_kawai_layout(G)
        ax = axes[i]
        
        # Diferenciar colores si es Best (B) o Worst (W)
        node_color = '#00b4d8' # Celeste para Best
        if chunk_name.startswith('W'):
            node_color = '#e07a5f' # Rojo/Naranja para Worst
            
        ax.set_title(f"Partición: {chunk_name}", fontsize=16, fontweight='bold')
        
        nx.draw_networkx_edges(G, pos, ax=ax, alpha=0.5, edge_color='#555555', width=2)
        
        edge_labels = {(str(row['Source']), str(row['Target'])): f"{row['Weight']:.3f}" for _, row in df_edges.iterrows()}
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, ax=ax, font_size=8, font_color='red')
        
        nx.draw_networkx_nodes(G, pos, ax=ax, node_size=600, node_color=node_color, alpha=0.9, edgecolors='white', linewidths=2)
        nx.draw_networkx_labels(G, pos, ax=ax, font_size=10, font_family="sans-serif", font_weight='bold')
        ax.axis('off')
        
    # Ocultar subplots no utilizados
    for j in range(num_files, len(axes)):
        axes[j].axis('off')
        
    plt.tight_layout()
    os.makedirs(os.path.dirname(output_png), exist_ok=True)
    plt.savefig(output_png, format='png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[+] Gráfico comparativo jerárquico guardado en: {output_png}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Visualizador de Grafos Jerárquicos')
    parser.add_argument('--algo', type=str, default='kruskal', choices=['prim', 'kruskal'], help='Algoritmo a visualizar')
    args = parser.parse_args()

    pattern = f"output/mst_edges_{args.algo}_*.csv"
    mst_files = sorted(glob.glob(pattern))
    
    # Filtrar el "mst_edges_prim.csv" del pipeline original si estuviera ahí.
    mst_files = [f for f in mst_files if "mst_edges_prim.csv" not in f and "mst_edges_kruskal.csv" not in f]

    if not mst_files:
        print(f"[!] No se encontraron archivos de particiones ({pattern}).")
        print("[!] Asegúrate de ejecutar el core C++ jerárquico primero.")
    else:
        print(f"[*] Encontradas {len(mst_files)} particiones jerárquicas. Generando visualización conjunta...")
        visualize_comparison_grid(mst_files, "output/mst_hierarchical_comparison.png")
