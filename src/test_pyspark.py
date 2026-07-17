import os
from pyspark.sql import SparkSession

def main():
    base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    ruta_csv_origen = os.path.join(base_dir, "data", "sample", "transacciones_sample.csv")
    ruta_bronze = os.path.join(base_dir, "data", "bronze", "transacciones_bronze.csv")

    print("===================================")
    print("INICIANDO SPARK - CAPA BRONZE (SAFE MODE)")
    print("===================================")
    
    spark = (
        SparkSession.builder
        .appName("Pipeline-Fraude-Bronze")
        .master("local[*]")
        .config("spark.driver.host", "localhost")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("ERROR")

    print("\nLEYENDO DATOS RAW CON ENGINE PYSPARK...")
    df_bronze = spark.read.csv(ruta_csv_origen, header=True, inferSchema=True)
    print(f"Cantidad de registros leídos con éxito: {df_bronze.count()}")

    print("\nGUARDANDO CAPA BRONZE (PASARELA COMPATIBLE WINDOWS)...")
    # Convertimos a Pandas para escribir en disco saltando el error de Hadoop de Windows
    os.makedirs(os.path.dirname(ruta_bronze), exist_ok=True)
    df_bronze.toPandas().to_csv(ruta_bronze, index=False)
    
    print("===================================")
    print("¡BRONZE GENERADA CORRECTAMENTE!")
    print(f"Ubicación: {ruta_bronze}")
    print("===================================")
    
    spark.stop()

if __name__ == "__main__":
    main()
