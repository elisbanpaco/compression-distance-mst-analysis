import os
import shutil
import subprocess
import sys

def clean_directory(path, exclude_files=None):
    if not os.path.exists(path):
        return
    for item in os.listdir(path):
        if exclude_files and item in exclude_files:
            continue
        item_path = os.path.join(path, item)
        if os.path.isdir(item_path):
            shutil.rmtree(item_path)
        else:
            os.remove(item_path)

def run_step(command, cwd=None):
    cmd_str = ' '.join(command) if isinstance(command, list) else command
    print(f"\n[ORCHESTRATOR] Ejecutando: {cmd_str}")
    result = subprocess.run(command, cwd=cwd, shell=isinstance(command, str))
    if result.returncode != 0:
        print(f"[ERROR] Falló la ejecución del paso: {cmd_str}")
        sys.exit(result.returncode)

def main():
    print("=== INICIANDO ORQUESTADOR DEL PIPELINE NCD + MST ===")
    
    # 1. Limpieza
    print("\n[1/4] Limpiando directorios residuales...")
    # Solo limpiamos carpetas data/ y output/. Mantenemos intacto el dataset base.
    clean_directory("data", exclude_files=["dataset_estudiantes.csv", ".gitkeep"])
    clean_directory("output", exclude_files=[".gitkeep"])
    print("Limpieza completada.")

    # 2. Preprocesamiento (Python)
    print("\n[2/4] Ejecutando preprocesadores (Extracción de características)...")
    run_step(["uv", "run", "src_python/02b_hierarchical_preprocessor.py"])

    # 3. Compilación y Ejecución del Motor Matemático (C++)
    print("\n[3/4] Compilando y ejecutando algoritmos C++ (NCD, Prim, Kruskal)...")
    build_dir = "src_cpp/build"
    os.makedirs(build_dir, exist_ok=True)
    
    # Compilar código en C++ (garantiza que siempre esté actualizado)
    run_step(["cmake", ".."], cwd=build_dir)
    run_step(["make"], cwd=build_dir)
    
    # Ejecutar binarios C++
    run_step(["./ncd_mst_hierarchical"], cwd=build_dir)

    # 4. Visualización y Comparación (Python)
    print("\n[4/4] Ejecutando visualizadores y análisis comparativo...")
    run_step(["uv", "run", "src_python/04b_hierarchical_visualizer.py"])
    run_step(["uv", "run", "src_python/05b_topology_comparator.py"])

    print("\n=== PIPELINE COMPLETADO EXITOSAMENTE ===")
    print("Puede revisar todos los resultados y el reporte en la carpeta 'output/'.")

if __name__ == "__main__":
    main()
