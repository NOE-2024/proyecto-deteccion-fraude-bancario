import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generar_datos_ficticios(n=2000):
    np.random.seed(42)
    bancos = ['BCP', 'BBVA', 'Interbank', 'Scotiabank', 'Banco de la Nacion']
    metodos = ['Yape', 'Plin', 'Tarjeta de Credito', 'Tarjeta de Debito', 'Transferencia']
    categorias = ['Restaurantes', 'Grifos', 'Supermercados', 'Tecnologia', 'Casinos', 'Otros']
    distritos = ['Lima', 'Miraflores', 'San Isidro', 'Santiago de Surco', 'Los Olivos']
    
    inicio = datetime.now() - timedelta(days=30)
    
    data = {
        'transaccion_id': [f"TX_{100000 + i}" for i in range(n)],
        'usuario_id': [f"USR_{np.random.randint(100, 500)}" for _ in range(n)],
        'banco': np.random.choice(bancos, n),
        'timestamp': [(inicio + timedelta(minutes=int(np.random.randint(0, 43200)))).strftime('%Y-%m-%d %H:%M:%S') for _ in range(n)],
        'monto': np.round(np.random.exponential(scale=150, size=n) + 5, 2),
        'metodo_pago': np.random.choice(metodos, n),
        'categoria_comercio': np.random.choice(categorias, n),
        'distrito_home': np.random.choice(distritos, n),
        'lat_transaccion': np.round(np.random.uniform(-12.15, -11.90, n), 5),
        'lon_transaccion': np.round(np.random.uniform(-77.10, -76.90, n), 5),
        'distancia_km_home': np.round(np.random.rayleigh(scale=5, size=n), 2),
        'comercio_nuevo': np.random.choice([0, 1], n, p=[0.85, 0.15]),
        'tx_ultimos_15min': np.random.randint(1, 4, n),
        'hora_dia': 0,
        'dia_semana': 0,
        'es_fraude': np.random.choice([0, 1], n, p=[0.96, 0.04])
    }
    
    df = pd.DataFrame(data)
    # Llenar campos de tiempo
    df['timestamp_dt'] = pd.to_datetime(df['timestamp'])
    df['hora_dia'] = df['timestamp_dt'].dt.hour
    df['dia_semana'] = df['timestamp_dt'].dt.dayofweek
    df.drop(columns=['timestamp_dt'], inplace=True)
    
    # Forzar patrones anómalos de fraude (Reglas peruanas)
    for i in range(len(df)):
        if df.loc[i, 'metodo_pago'] in ['Yape', 'Plin'] and df.loc[i, 'monto'] > 450:
            if np.random.rand() > 0.3: df.loc[i, 'es_fraude'] = 1
            
    return df

if __name__ == "__main__":
    base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    ruta_salida = os.path.join(base_dir, "data", "sample", "transacciones_sample.csv")
    os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)
    
    df = generar_datos_ficticios()
    df.to_csv(ruta_salida, index=False)
    print(f"Dataset de simulación creado con {len(df)} registros en: {ruta_salida}")