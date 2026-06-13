import pandas as pd
import numpy as np
import random
import os

def generate_synthetic_data(n=18000, output_path="data/dataset_estudiantes.csv"):
    """
    Genera un dataset sintético de 18,000 estudiantes con exactamente 11 variables 
    heterogéneas (sin variable de estado final o target).
    """
    print(f"[*] Generando {n} registros de estudiantes (11 variables)...")
    np.random.seed(42)
    random.seed(42)
    
    # 1. Edad (Integer)
    edades = np.random.randint(16, 30, n)
    
    # 2. Sexo (Char)
    sexos = np.random.choice(['M', 'F'], n)
    
    # 3. Talla (Float)
    tallas = np.random.uniform(1.50, 1.90, n).round(2)
    
    # 4. Latitud (Float) - Coordenadas geográficas
    latitud = np.random.uniform(-18.0, -0.0, n).round(5)
    
    # 5. Notas (Float) - Rango de 0 a 20
    notas = np.random.uniform(0, 20, n).round(1)
    
    # 6. Horas de Estudio (Integer)
    horas_estudio = np.random.randint(0, 40, n)
    
    # 7. Fecha de Matricula (Date/String) - Añade el tipo de dato Fecha
    base_date = pd.to_datetime('2023-01-01')
    fechas_matricula = (base_date + pd.to_timedelta(np.random.randint(0, 365, n), unit='d')).strftime('%Y-%m-%d')
    
    # 8. Acceso a Internet (Binario)
    internet = np.random.choice([0, 1], n, p=[0.2, 0.8])
    
    # 9. Trabaja (Binario)
    trabaja = np.random.choice([0, 1], n, p=[0.3, 0.7])
    
    # 10. Comentarios del Tutor (String)
    comentarios_opciones = [
        "Alta motivacion", "Problemas familiares", "Dificultad con matematicas", 
        "Falta de tiempo", "Excelente participacion", "Ausencias frecuentes"
    ]
    comentarios_tutor = np.random.choice(comentarios_opciones, n)
    
    # 11. Horas de Sueño (Integer)
    horas_sueno = np.random.randint(4, 10, n)
    
    df = pd.DataFrame({
        'Edad': edades,
        'Sexo': sexos,
        'Talla': tallas,
        'Latitud': latitud,
        'Notas': notas,
        'Horas_Estudio': horas_estudio,
        'Fecha_Matricula': fechas_matricula,
        'Acceso_Internet': internet,
        'Trabaja': trabaja,
        'Comentarios_Tutor': comentarios_tutor,
        'Horas_Sueno': horas_sueno
    })
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"[+] Dataset guardado exitosamente en: {output_path}")

if __name__ == "__main__":
    generate_synthetic_data(18000)
