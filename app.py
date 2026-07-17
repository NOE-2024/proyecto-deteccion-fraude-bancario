"""
Dashboard web — Detección de Fraude Bancario en Tiempo Real
Grupo 1 · DD283 Big Data · Cycle VIII · 2026-1
Alumno: Noe Paredes Hilario

Ejecutar con:  streamlit run app.py
"""

import os
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime, timedelta
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix

st.set_page_config(
    page_title="Detección de Fraude Bancario | Grupo 1",
    page_icon="🏦",
    layout="wide",
)

# ----------------------------------------------------------------------
# 1. GENERACIÓN / CARGA DE DATOS (mismo simulador del proyecto)
# ----------------------------------------------------------------------
BANCOS = ["BCP", "BBVA", "Interbank", "Scotiabank", "Banco de la Nacion"]
METODOS = ["Yape", "Plin", "Tarjeta de Credito", "Tarjeta de Debito", "Transferencia"]
CATEGORIAS = ["Restaurantes", "Grifos", "Supermercados", "Tecnologia", "Casinos", "Otros"]
DISTRITOS = ["Lima", "Miraflores", "San Isidro", "Santiago de Surco", "Los Olivos"]

FEATURES = [
    "monto", "distancia_km_home", "comercio_nuevo",
    "tx_ultimos_15min", "hora_dia", "dia_semana",
    "es_madrugada", "yape_plin_alto", "fin_de_semana",
]


@st.cache_data
def generar_dataset(n=2000, seed=42):
    np.random.seed(seed)
    inicio = datetime.now() - timedelta(days=30)

    data = {
        "transaccion_id": [f"TX_{100000 + i}" for i in range(n)],
        "usuario_id": [f"USR_{np.random.randint(100, 500)}" for _ in range(n)],
        "banco": np.random.choice(BANCOS, n),
        "timestamp": [
            (inicio + timedelta(minutes=int(np.random.randint(0, 43200))))
            for _ in range(n)
        ],
        "monto": np.round(np.random.exponential(scale=150, size=n) + 5, 2),
        "metodo_pago": np.random.choice(METODOS, n),
        "categoria_comercio": np.random.choice(CATEGORIAS, n),
        "distrito_home": np.random.choice(DISTRITOS, n),
        "distancia_km_home": np.round(np.random.rayleigh(scale=5, size=n), 2),
        "comercio_nuevo": np.random.choice([0, 1], n, p=[0.85, 0.15]),
        "tx_ultimos_15min": np.random.randint(1, 4, n),
        "es_fraude": np.random.choice([0, 1], n, p=[0.96, 0.04]),
    }
    df = pd.DataFrame(data)
    df["hora_dia"] = df["timestamp"].dt.hour
    df["dia_semana"] = df["timestamp"].dt.dayofweek

    # Reglas de fraude realistas (igual que el simulador original)
    mask = (df["metodo_pago"].isin(["Yape", "Plin"])) & (df["monto"] > 450)
    ruido = np.random.rand(len(df)) > 0.3
    df.loc[mask & ruido, "es_fraude"] = 1
    return df


def construir_capas(df_bronze: pd.DataFrame):
    """Bronze -> Silver -> Gold, igual lógica que pipeline_batch.py"""
    silver = df_bronze.drop_duplicates(subset=["transaccion_id"])
    silver = silver.dropna(subset=["usuario_id", "monto"])

    gold = silver.copy()
    gold["es_madrugada"] = gold["hora_dia"].between(1, 5).astype(int)
    gold["yape_plin_alto"] = (
        (gold["metodo_pago"].isin(["Yape", "Plin"])) & (gold["monto"] > 400)
    ).astype(int)
    gold["fin_de_semana"] = gold["dia_semana"].isin([5, 6]).astype(int)
    return silver, gold


@st.cache_resource
def entrenar_modelo(gold: pd.DataFrame):
    X = gold[FEATURES]
    y = gold["es_fraude"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    model = RandomForestClassifier(
        n_estimators=100, class_weight="balanced", random_state=42
    )
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    reporte = classification_report(y_test, y_pred, output_dict=True)
    matriz = confusion_matrix(y_test, y_pred)
    importancias = (
        pd.Series(model.feature_importances_, index=FEATURES)
        .sort_values(ascending=False)
    )
    return model, reporte, matriz, importancias


# ----------------------------------------------------------------------
# 2. CARGAR / SUBIR DATOS
# ----------------------------------------------------------------------
st.sidebar.title("🏦 Grupo 1 — Fraude Bancario")
st.sidebar.caption("DD283 · Big Data · Cycle VIII · 2026-1")
st.sidebar.markdown("**Alumno:** Noe Paredes Hilario")

archivo = st.sidebar.file_uploader(
    "Cargar tu propio CSV (opcional)", type=["csv"]
)
n_registros = st.sidebar.slider("N° de transacciones simuladas", 500, 10000, 2000, step=500)

if archivo is not None:
    df_bronze = pd.read_csv(archivo, parse_dates=["timestamp"])
    st.sidebar.success(f"Archivo cargado: {len(df_bronze)} registros")
else:
    df_bronze = generar_dataset(n=n_registros)

silver, gold = construir_capas(df_bronze)
model, reporte, matriz, importancias = entrenar_modelo(gold)

pagina = st.sidebar.radio(
    "Navegación",
    ["📊 Resumen", "🗂️ Pipeline de Datos (Bronze→Silver→Gold)", "🤖 Modelo ML", "🔎 Probar una Transacción"],
)

# ----------------------------------------------------------------------
# 3. PÁGINA: RESUMEN
# ----------------------------------------------------------------------
if pagina == "📊 Resumen":
    st.title("Sistema de Detección de Fraude Bancario en Tiempo Real")
    st.markdown(
        "Arquitectura Lambda + Machine Learning para banca digital peruana "
        "(Yape, Plin, tarjetas, transferencias)."
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Transacciones procesadas", f"{len(df_bronze):,}")
    c2.metric("Casos de fraude", f"{int(df_bronze['es_fraude'].sum()):,}")
    tasa = df_bronze["es_fraude"].mean() * 100
    c3.metric("Tasa de fraude", f"{tasa:.2f}%")
    f1 = reporte.get("1", {}).get("f1-score", 0)
    c4.metric("F1-score del modelo (clase fraude)", f"{f1:.2f}")

    col1, col2 = st.columns(2)
    with col1:
        fig = px.histogram(
            df_bronze, x="monto", color="es_fraude", nbins=40,
            title="Distribución de montos por transacción",
            labels={"es_fraude": "Fraude"},
        )
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig2 = px.pie(
            df_bronze, names="metodo_pago", title="Transacciones por método de pago"
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Transacciones por hora del día")
    fig3 = px.histogram(
        df_bronze, x="hora_dia", color="es_fraude", nbins=24,
        title="Frecuencia horaria (madrugada = mayor riesgo)",
    )
    st.plotly_chart(fig3, use_container_width=True)

# ----------------------------------------------------------------------
# 4. PÁGINA: PIPELINE
# ----------------------------------------------------------------------
elif pagina == "🗂️ Pipeline de Datos (Bronze→Silver→Gold)":
    st.title("Arquitectura Medallion: Bronze → Silver → Gold")

    tab1, tab2, tab3 = st.tabs(["🥉 Bronze (crudo)", "🥈 Silver (limpio)", "🥇 Gold (features)"])
    with tab1:
        st.markdown(f"**{len(df_bronze):,} registros** — datos tal como llegan.")
        st.dataframe(df_bronze.head(50), use_container_width=True)
    with tab2:
        st.markdown(f"**{len(silver):,} registros** — sin duplicados ni nulos en campos críticos.")
        st.dataframe(silver.head(50), use_container_width=True)
    with tab3:
        st.markdown(f"**{len(gold):,} registros** — con variables de negocio para el modelo:")
        st.markdown(
            "- `es_madrugada`: transacción entre 1am–5am\n"
            "- `yape_plin_alto`: Yape/Plin con monto > S/. 400\n"
            "- `fin_de_semana`: transacción en sábado o domingo"
        )
        st.dataframe(
            gold[["transaccion_id", "monto", "metodo_pago", "hora_dia",
                  "es_madrugada", "yape_plin_alto", "fin_de_semana", "es_fraude"]].head(50),
            use_container_width=True,
        )

# ----------------------------------------------------------------------
# 5. PÁGINA: MODELO ML
# ----------------------------------------------------------------------
elif pagina == "🤖 Modelo ML":
    st.title("Modelo de Machine Learning — Random Forest")
    st.caption("Entrenado sobre la capa Gold, con balanceo de clases (class_weight='balanced').")

    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("Importancia de variables")
        fig = px.bar(
            importancias.sort_values(),
            orientation="h",
            labels={"value": "Importancia", "index": "Variable"},
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Matriz de confusión")
        fig_cm = px.imshow(
            matriz, text_auto=True,
            labels=dict(x="Predicción", y="Real", color="Cantidad"),
            x=["No fraude", "Fraude"], y=["No fraude", "Fraude"],
            color_continuous_scale="Blues",
        )
        st.plotly_chart(fig_cm, use_container_width=True)

    st.subheader("Reporte de clasificación")
    st.dataframe(pd.DataFrame(reporte).transpose().round(3), use_container_width=True)

# ----------------------------------------------------------------------
# 6. PÁGINA: PROBAR UNA TRANSACCIÓN (demo en vivo para el profesor)
# ----------------------------------------------------------------------
else:
    st.title("🔎 Probar una transacción en vivo")
    st.caption("Ideal para la demostración: ingresa datos y el modelo predice el riesgo al instante.")

    with st.form("form_prediccion"):
        c1, c2, c3 = st.columns(3)
        with c1:
            monto = st.number_input("Monto (S/.)", min_value=1.0, value=150.0, step=10.0)
            metodo = st.selectbox("Método de pago", METODOS)
        with c2:
            distancia = st.slider("Distancia al distrito habitual (km)", 0.0, 50.0, 3.0)
            hora = st.slider("Hora del día", 0, 23, 14)
        with c3:
            comercio_nuevo = st.checkbox("¿Comercio nuevo para el usuario?")
            dia_semana = st.selectbox(
                "Día de la semana",
                ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"],
            )
            tx_recientes = st.slider("Transacciones en últimos 15 min", 1, 10, 1)

        enviado = st.form_submit_button("Evaluar transacción")

    if enviado:
        dia_idx = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"].index(dia_semana)
        fila = pd.DataFrame([{
            "monto": monto,
            "distancia_km_home": distancia,
            "comercio_nuevo": int(comercio_nuevo),
            "tx_ultimos_15min": tx_recientes,
            "hora_dia": hora,
            "dia_semana": dia_idx,
            "es_madrugada": int(1 <= hora <= 5),
            "yape_plin_alto": int(metodo in ["Yape", "Plin"] and monto > 400),
            "fin_de_semana": int(dia_idx in [5, 6]),
        }])[FEATURES]

        prob = model.predict_proba(fila)[0][1]
        pred = model.predict(fila)[0]

        if pred == 1:
            st.error(f"🚨 ALERTA DE FRAUDE — Probabilidad estimada: {prob*100:.1f}%")
        else:
            st.success(f"✅ Transacción normal — Probabilidad de fraude: {prob*100:.1f}%")

        st.progress(min(prob, 1.0))
        st.dataframe(fila, use_container_width=True)