import os
import pandas as pd

def main():
    base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    ruta_bronze = os.path.join(base_dir, "data", "bronze", "transacciones_bronze.csv")
    ruta_silver = os.path.join(base_dir, "data", "silver", "transacciones_silver.csv")
    ruta_gold = os.path.join(base_dir, "data", "gold", "transacciones_gold.csv")

    print("===================================")
    print("INICIANDO PIPELINE BATCH (SILVER & GOLD)")
    print("===================================")

    # --- CAPA SILVER (LIMPIEZA) ---
    print("\n[1/2] PROCESANDO CAPA SILVER (LIMPIEZA)...")
    if not os.path.exists(ruta_bronze):
        print("Error: No se encuentra la capa Bronze para procesar. Corre primero pipeline_bronze.py")
        return
        
    bronze_df = pd.read_csv(ruta_bronze)
    
    # Limpieza de duplicados y nulos
    silver_df = bronze_df.drop_duplicates(subset=["transaccion_id"])
    silver_df = silver_df.dropna(subset=["usuario_id", "monto"])
    silver_df["timestamp"] = pd.to_datetime(silver_df["timestamp"])
    
    os.makedirs(os.path.dirname(ruta_silver), exist_ok=True)
    silver_df.to_csv(ruta_silver, index=False)
    print(f"-> Capa Silver exportada con éxito ({len(silver_df)} registros).")

    # --- CAPA GOLD (INGENIERÍA DE FEATURES) ---
    print("\n[2/2] PROCESANDO CAPA GOLD (INGENIERÍA DE FEATURES)...")
    gold_df = silver_df.copy()
    
    # Agregamos los patrones lógicos de fraude
    gold_df["es_madrugada"] = gold_df["timestamp"].dt.hour.between(1, 5).astype(int)
    gold_df["yape_plin_alto"] = ((gold_df["metodo_pago"].isin(["Yape", "Plin"])) & (gold_df["monto"] > 400)).astype(int)
    gold_df["fin_de_semana"] = gold_df["timestamp"].dt.dayofweek.isin([5, 6]).astype(int)
    
    os.makedirs(os.path.dirname(ruta_gold), exist_ok=True)
    gold_df.to_csv(ruta_gold, index=False)
    print("-> Capa Gold exportada con éxito.")

    print("\n===================================")
    print("¡PIPELINE BATCH COMPLETADO CON ÉXITO!")
    print("===================================")

if __name__ == "__main__":
    main()