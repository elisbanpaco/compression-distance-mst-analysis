import pandas as pd
import os
import gzip
import itertools
import numpy as np
import argparse

def process_chunk(df_chunk, chunk_name, base_dir="data/hierarchical_comprimidas", combined_dir="data/hierarchical_combinadas", data_dir="data"):
    print(f"[*] Procesando partición: {chunk_name} (Tamaño: {len(df_chunk)} registros)")
    
    chunk_base_dir = os.path.join(base_dir, chunk_name)
    chunk_combined_dir = os.path.join(combined_dir, chunk_name)
    os.makedirs(chunk_base_dir, exist_ok=True)
    os.makedirs(chunk_combined_dir, exist_ok=True)
    
    col_data = {}
    c_x_sizes = {}
    
    # 1. Comprimir variables individuales (C_X)
    for col in df_chunk.columns:
        col_dir = os.path.join(chunk_base_dir, col)
        os.makedirs(col_dir, exist_ok=True)
        file_path = os.path.join(col_dir, col)
        
        data_str = '\n'.join(df_chunk[col].astype(str).tolist())
        data_bytes = data_str.encode('utf-8')
        col_data[col] = data_bytes
        
        with open(file_path, 'wb') as f:
            f.write(data_bytes)
            
        compressed_data = gzip.compress(data_bytes)
        c_x_sizes[col] = len(compressed_data)
        
        with gzip.open(file_path + '.gz', 'wb') as f_out:
            f_out.write(data_bytes)
            
    # 2. Comprimir combinaciones (C_XY)
    weights_records = []
    for col1, col2 in itertools.combinations(df_chunk.columns, 2):
        combined_bytes = col_data[col1] + b'\n' + col_data[col2]
        pair_name = f"{col1}_{col2}"
        pair_dir = os.path.join(chunk_combined_dir, pair_name)
        os.makedirs(pair_dir, exist_ok=True)
        
        pair_file_path = os.path.join(pair_dir, pair_name)
        with open(pair_file_path, 'wb') as f:
            f.write(combined_bytes)
            
        compressed_combined = gzip.compress(combined_bytes)
        c_xy = len(compressed_combined)
        
        with gzip.open(pair_file_path + '.gz', 'wb') as f_out:
            f_out.write(combined_bytes)
            
        weights_records.append({
            'Var1': col1,
            'Var2': col2,
            'C_X': c_x_sizes[col1] / 1024.0, # En KB
            'C_Y': c_x_sizes[col2] / 1024.0, # En KB
            'C_XY': c_xy / 1024.0 # En KB
        })
        
    weights_df = pd.DataFrame(weights_records)
    weights_csv = os.path.join(data_dir, f"weights_{chunk_name}.csv")
    weights_df.to_csv(weights_csv, index=False)
    print(f" -> Exportado pesos para {chunk_name} en: {weights_csv}")

def preprocess_and_split(input_path="data/dataset_estudiantes.csv", target_col="Notas", num_partitions=2):
    import glob
    import shutil
    
    print("[*] Limpiando archivos temporales y resultados previos del pipeline jerárquico...")
    for path in ["data/hierarchical_comprimidas", "data/hierarchical_combinadas"]:
        if os.path.exists(path):
            shutil.rmtree(path)
            
    for f in glob.glob("data/weights_*.csv"):
        try:
            os.remove(f)
        except OSError:
            pass
            
    for pattern in ["output/mst_edges_prim_*.csv", "output/mst_edges_kruskal_*.csv", "output/ncd_distances_*.csv"]:
        for f in glob.glob(pattern):
            try:
                os.remove(f)
            except OSError:
                pass

    print(f"\n[*] Leyendo dataset desde {input_path}...")
    if not os.path.exists(input_path):
        print(f"[ERROR] No se encontró el dataset original en {input_path}")
        return

    df = pd.read_csv(input_path)
    
    if target_col not in df.columns:
        print(f"[ERROR] La columna objetivo '{target_col}' no existe en el dataset.")
        return

    if num_partitions % 2 != 0:
        raise ValueError("El número de particiones (N) debe ser par para tener igual cantidad de Best y Worst.")
    
    print(f"[*] Ordenando dataset por '{target_col}' de mayor a menor...")
    df = df.sort_values(by=target_col, ascending=False).reset_index(drop=True)
    
    print(f"[*] Dividiendo en {num_partitions} particiones iguales...")
    
    chunk_size = len(df) // num_partitions
    chunks = [df.iloc[i*chunk_size : (i+1)*chunk_size] if i < num_partitions - 1 else df.iloc[i*chunk_size:] for i in range(num_partitions)]
    
    half = num_partitions // 2
    for i, chunk in enumerate(chunks):
        if i < half:
            chunk_name = f"B{num_partitions}C{i+1}"
        else:
            chunk_name = f"W{num_partitions}C{i - half + 1}"
            
        process_chunk(chunk, chunk_name)
        
    print("\n[+] Preprocesamiento jerárquico finalizado con éxito.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Preprocesador Jerárquico basado en Clustering Top-Down')
    parser.add_argument('--target', type=str, default='Notas', help='Columna objetivo para el ordenamiento (ej. Notas)')
    parser.add_argument('--partitions', type=int, default=4, help='Número par total de particiones (N)') # cambia el default a N para el numero de particiones
    args = parser.parse_args()
    
    preprocess_and_split(target_col=args.target, num_partitions=args.partitions)
