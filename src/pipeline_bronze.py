import os
import pandas as pd

def main():
    base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    ruta_csv_origen = os.path.join(base_dir, "data", "sample", "transacciones_sample.csv")
    ruta_bronze = os.path.join(base_dir, "data", "bronze", "transacciones_bronze.csv")

    print("===================================")
    print("INICIANDO PIPELINE - CAPA BRONZE (SAFE MODE)")
    print("===================================")
    
    if not os.path.exists(ruta_csv_origen):
        print(f"Error: No se encontró el archivo original en {ruta_csv_origen}")
        return

    print("LEYENDO DATOS RAW CON PANDAS...")
    df_bronze = pd.read_csv(ruta_csv_origen)
    print(f"Cantidad de registros leídos con éxito: {len(df_bronze)}")

    print("\nGUARDANDO CAPA BRONZE...")
    os.makedirs(os.path.dirname(ruta_bronze), exist_ok=True)
    df_bronze.to_csv(ruta_bronze, index=False)
    
    print("===================================")
    print("¡BRONZE GENERADA CORRECTAMENTE!")
    print(f"Ubicación: {ruta_bronze}")
    print("===================================")

if __name__ == "__main__":
    main()