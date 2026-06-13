import pandas as pd
import json
import os
import gzip

def preprocess_and_compress(input_path="data/dataset_estudiantes.csv", 
                            base_dir="data/variables_comprimidas",
                            output_cpp="data/students_serialized"):
    """
    1. Lee el dataset y comprime cada columna independientemente, reportando en KB.
    2. Serializa a cada estudiante a un texto base para que el ejecutable de C++ 
       pueda procesar el cálculo NCD y MST.
    """
    print(f"[*] Leyendo dataset desde {input_path}...")
    df = pd.read_csv(input_path)
    
    os.makedirs(base_dir, exist_ok=True)
    print(f"\n--- Comprimiendo cada Variable con GZIP ---")
    
    for col in df.columns:
        col_dir = os.path.join(base_dir, col)
        os.makedirs(col_dir, exist_ok=True)
        
        # Archivo original de la variable sin extensión
        file_path = os.path.join(col_dir, col)
        df[col].astype(str).to_csv(file_path, index=False, header=False)
        
        # Comprimir con GZIP
        with open(file_path, 'rb') as f_in:
            data = f_in.read()
            compressed_data = gzip.compress(data)
            kb_size = len(compressed_data) / 1024
            
            # Guardar el .gz
            with gzip.open(file_path + '.gz', 'wb') as f_out:
                f_out.write(data)
                
        print(f" -> {col:<20} | Tamaño Comprimido: {kb_size:.2f} KB")

    print("\n--- Serializando datos para C++ ---")
    # Convertiremos cada fila (estudiante) a un string minificado JSON 
    # y lo guardaremos línea por línea para que C++ lo consuma.
    with open(output_cpp, 'w', encoding='utf-8') as f:
        for idx, row in df.iterrows():
            row_str = json.dumps(row.to_dict(), separators=(',', ':'))
            f.write(row_str + '\n')
            
    print(f"[+] Archivo serializado creado en: {output_cpp}")
    print("[+] Preprocesamiento finalizado con éxito.")

if __name__ == "__main__":
    preprocess_and_compress()
