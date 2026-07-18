import json
import os
import argparse

OUTPUT_DIR = "output"

def analyze_insights(top_n=2):
    print(f"--- Topología Insights (TOP {top_n} Nodos) ---")
    json_path = os.path.join(OUTPUT_DIR, "topology_comparisons.json")
    if not os.path.exists(json_path):
        print(f"[ERROR] No se encontró {json_path}. Ejecuta 05b primero.")
        return
        
    with open(json_path, 'r', encoding='utf-8') as f:
        comparisons = json.load(f)
        
    all_top_nodes = []
    
    report_lines = []
    report_lines.append(f"=== TOPOLOGY INSIGHTS (Extracción de Nodos Clave) ===")
    report_lines.append(f"Configuración: TOP {top_n} nodos de mayor cambio (absoluto) por comparación.\n")
    
    for comp in comparisons:
        topA = comp['TopA']
        topB = comp['TopB']
        diffs = comp['Diffs']
        
        # Ordenar nodos por su diferencia (ya viene en valor absoluto desde el JSON)
        sorted_nodes = sorted(diffs.keys(), key=diffs.get, reverse=True)
        
        # Seleccionar los TOP_N
        top_n_nodes = sorted_nodes[:top_n]
        all_top_nodes.append(set(top_n_nodes))
        
        report_lines.append(f"Comparación: {topB} vs {topA}")
        report_lines.append(f"  Top {top_n} nodos con mayor cambio: {', '.join(top_n_nodes)}")
        for idx, n in enumerate(top_n_nodes):
            report_lines.append(f"    - rVP{idx+1}: {n}: {diffs[n]:.4f}")
        report_lines.append("")
        
    if all_top_nodes:
        # Unión: Todos los nodos que aparecieron al menos una vez en el TOP de alguna comparación
        union_nodes = set.union(*all_top_nodes)
        report_lines.append(f"=== ANÁLISIS DE CONJUNTOS ===")
        report_lines.append(f"UNIÓN (Aparecen al menos una vez en el TOP {top_n} de cualquier comparación):")
        report_lines.append(f"  {', '.join(sorted(union_nodes)) if union_nodes else 'Ninguno'}")
        report_lines.append(f"  Total: {len(union_nodes)} nodos\n")
        
        print(f"[*] Se encontraron {len(union_nodes)} nodos en la Unión.")
        
    report_path = os.path.join(OUTPUT_DIR, "topology_insights_report.txt")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(report_lines))
        
    print(f"[+] Insights calculados. Reporte guardado en: {report_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Extractor de Insights Topológicos')
    parser.add_argument('--top', type=int, default=3, help='Cantidad de nodos TOP a extraer por comparación')
    args = parser.parse_args()
    analyze_insights(top_n=args.top)
