import pandas as pd
import os
import gzip
import itertools

def preprocess_and_compress(input_path="data/dataset_estudiantes.csv", 
                            base_dir="data/variables_comprimidas",
                            combined_dir="data/variables_combinadas",
                            weights_csv="data/compression_weights.csv"):
    """
    1. Lee el dataset (que permanece intacto) y comprime cada columna independientemente (C_X) usando GZIP.
    2. Combina cada par de columnas, las guarda físicamente y las comprime (C_XY) usando GZIP.
    3. Exporta los pesos a un CSV para que C++ pueda calcular la matriz NCD.
    """
    print(f"[*] Leyendo dataset completo desde {input_path}...")
    df = pd.read_csv(input_path)
    
    os.makedirs(base_dir, exist_ok=True)
    os.makedirs(combined_dir, exist_ok=True)
    
    print(f"\n--- Comprimiendo cada Variable con GZIP (C_X) ---")
    
    col_data = {}
    c_x_sizes = {}
    
    for col in df.columns:
        col_dir = os.path.join(base_dir, col)
        os.makedirs(col_dir, exist_ok=True)
        
        file_path = os.path.join(col_dir, col)
        
        # Guardar la variable como texto
        data_str = '\n'.join(df[col].astype(str).tolist())
        data_bytes = data_str.encode('utf-8')
        
        # Almacenar en memoria para combinar luego
        col_data[col] = data_bytes
        
        with open(file_path, 'wb') as f:
            f.write(data_bytes)
            
        # Comprimir C_X
        compressed_data = gzip.compress(data_bytes)
        c_x_sizes[col] = len(compressed_data)
        
        with gzip.open(file_path + '.gz', 'wb') as f_out:
            f_out.write(data_bytes)
            
        print(f" -> {col:<20} | Tamaño Comprimido (C_X): {c_x_sizes[col] / 1024:.2f} KB")

    print("\n--- Comprimiendo Pares de Variables (C_XY) ---")
    
    weights_records = []
    
    # Todas las combinaciones posibles de a 2
    for col1, col2 in itertools.combinations(df.columns, 2):
        combined_bytes = col_data[col1] + b'\n' + col_data[col2]
        
        # Crear carpeta para la combinacion
        pair_name = f"{col1}_{col2}"
        pair_dir = os.path.join(combined_dir, pair_name)
        os.makedirs(pair_dir, exist_ok=True)
        
        pair_file_path = os.path.join(pair_dir, pair_name)
        
        # Guardar archivo de texto combinado
        with open(pair_file_path, 'wb') as f:
            f.write(combined_bytes)
            
        # Comprimir y guardar archivo GZ combinado
        compressed_combined = gzip.compress(combined_bytes)
        c_xy = len(compressed_combined)
        
        with gzip.open(pair_file_path + '.gz', 'wb') as f_out:
            f_out.write(combined_bytes)
        
        weights_records.append({
            'Var1': col1,
            'Var2': col2,
            'C_X': c_x_sizes[col1 ] / 1024, # En KB
            'C_Y': c_x_sizes[col2] / 1024 , # En KB
            'C_XY': c_xy / 1024 # En KB
        })
        
    # Guardar en CSV
    weights_df = pd.DataFrame(weights_records)
    weights_df.to_csv(weights_csv, index=False)
    
    print(f"\n[+] Carpetas combinadas generadas en: {combined_dir}")
    print(f"[+] Pesos de compresión exportados a: {weights_csv}")
    print("[+] Preprocesamiento finalizado con éxito.")

if __name__ == "__main__":
    preprocess_and_compress()
