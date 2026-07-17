import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix

def main():
    base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    ruta_gold = os.path.join(base_dir, "data", "gold", "transacciones_gold.csv")

    print("==================================================")
    print("INICIANDO ENTRENAMIENTO DEL MODELO DE FRAUDE")
    print("==================================================")

    if not os.path.exists(ruta_gold):
        print("Error: No se encuentra la capa Gold. Por favor ejecuta primero src/pipeline_batch.py")
        return

    # 1. Cargar los datos de la capa Gold
    df = pd.read_csv(ruta_gold)
    print(f"Cargados {len(df)} registros para el entrenamiento.")

    # 2. Seleccionar variables (Features) y la variable objetivo (Target)
    # Seleccionamos las características numéricas y las peruanas creadas en la capa Gold
    features = [
        "monto", "distancia_km_home", "comercio_nuevo", 
        "tx_ultimos_15min", "hora_dia", "dia_semana", 
        "es_madrugada", "yape_plin_alto", "fin_de_semana"
    ]
    target = "es_fraude"

    X = df[features]
    y = df[target]

    # 3. Dividir en datos de Entrenamiento (80%) y Prueba (20%)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    print("\n[1/3] Entrenando Clasificador Random Forest...")
    # Usamos class_weight='balanced' porque el fraude suele ser un evento muy raro (desbalanceado)
    model = RandomForestClassifier(n_estimators=100, class_weight='balanced', random_state=42)
    model.fit(X_train, y_train)
    print("-> ¡Modelo entrenado con éxito!")

    # 4. Evaluación del Modelo
    print("\n[2/3] Evaluando métricas de rendimiento...")
    y_pred = model.predict(X_test)
    
    print("\n=== REPORTE DE CLASIFICACIÓN ===")
    print(classification_report(y_test, y_pred))
    
    print("=== MATRIZ DE CONFUSIÓN ===")
    print(confusion_matrix(y_test, y_pred))

    # 5. Importancia de las características (Features)
    print("\n[3/3] Análisis de impacto de variables:")
    importances = pd.Series(model.feature_importances_, index=features).sort_values(ascending=False)
    for feat, imp in importances.items():
        print(f"   - {feat}: {imp:.4f}")

    print("\n==================================================")
    print("¡PROCESO FINALIZADO CON ÉXITO!")
    print("==================================================")

if __name__ == "__main__":
    main()