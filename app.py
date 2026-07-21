import streamlit as st
import pandas as pd
import numpy as np
import time
import plotly.express as px
from sklearn.ensemble import RandomForestClassifier

# ----------------------------------------------------------------------
# CONFIGURACIÓN DE PÁGINA
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="Core de Seguridad | Detección de Fraude Bancario",
    page_icon="🛡️",
    layout="wide"
)

# ----------------------------------------------------------------------
# CONSTANTES Y LISTAS DE CONTROL
# ----------------------------------------------------------------------
METODOS = ["Tarjeta de Débito", "Tarjeta de Crédito", "Yape", "Plin", "Transferencia CCI", "Cajero Automático (ATM)"]
BANCOS = ["BCP", "BBVA", "Interbank", "Scotiabank", "Banco de la Nación", "BanBif"]
CATEGORIAS = ["Supermercados/Retail", "Restaurantes", "E-commerce / Compras Web", "Juegos de Azar / Apuestas", "Retiro en Cajero (ATM)", "Transferencia Personal", "Servicios Básicos"]
PROVINCIAS = [
    "Lima", "Callao", "Arequipa", "Trujillo", "Chiclayo", "Piura", "Cusco", 
    "Huancayo", "Iquitos", "Pucallpa", "Tacna", "Ica", "Cajamarca", "Sullana", "Ayacucho"
]
FEATURES = ["monto", "distancia_km_home", "comercio_nuevo", "tx_ultimos_15min", "hora_dia", "dia_semana", "es_madrugada", "yape_plin_alto", "fin_de_semana"]

# ----------------------------------------------------------------------
# MODELO ENTRENADO
# ----------------------------------------------------------------------
@st.cache_resource
def cargar_modelo():
    np.random.seed(42)
    n = 1500
    df_train = pd.DataFrame({
        "monto": np.random.uniform(10, 5000, n),
        "distancia_km_home": np.random.uniform(0, 80, n),
        "comercio_nuevo": np.random.choice([0, 1], n),
        "tx_ultimos_15min": np.random.randint(1, 10, n),
        "hora_dia": np.random.randint(0, 24, n),
        "dia_semana": np.random.randint(0, 7, n),
        "es_madrugada": np.random.choice([0, 1], n),
        "yape_plin_alto": np.random.choice([0, 1], n),
        "fin_de_semana": np.random.choice([0, 1], n),
    })
    y = ((df_train["monto"] > 1200) & (df_train["es_madrugada"] == 1) | (df_train["distancia_km_home"] > 35) | (df_train["tx_ultimos_15min"] > 5)).astype(int)
    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    rf.fit(df_train[FEATURES], y)
    return rf

model = cargar_modelo()

# ----------------------------------------------------------------------
# BARRA LATERAL (SIDEBAR)
# ----------------------------------------------------------------------
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2092/2092663.png", width=80)
st.sidebar.title("Core de Seguridad")
vista = st.sidebar.radio(
    "Selecciona una vista:",
    ["📊 Dashboard General de Riesgos", "🗺️ Mapa Estadístico por Provincias", "🔎 Evaluador de Transacciones (En Vivo)"]
)
st.sidebar.markdown("---")
st.sidebar.caption("🔒 Versión del Core: 3.5.0")
st.sidebar.caption("⚡ SLA de Latencia: < 25 ms")

# ======================================================================
# VISTA 1: DASHBOARD GENERAL (CÁLCULO DINÁMICO GARANTIZADO)
# ======================================================================
if vista == "📊 Dashboard General de Riesgos":
    st.title("📊 Dashboard General de Riesgos y Fraude Bancario")
    st.caption("Visión ejecutiva del comportamiento de transacciones a nivel nacional con controles dinámicos.")
    
    f_col1, f_col2, f_col3 = st.columns(3)
    with f_col1:
        periodo = st.selectbox("📅 Período Evaluado:", ["Hoy", "Últimos 7 días", "Este Mes", "Año 2026"])
    with f_col2:
        banco_sel = st.selectbox("🏦 Entidad Bancaria:", ["Todas las Entidades"] + BANCOS)
    with f_col3:
        canal_sel = st.selectbox("💳 Canal de Pago:", ["Todos los Canales"] + METODOS)

    # DICCIONARIOS DE PESOS ESPECÍFICOS PARA CADA OPCIÓN
    pesos_periodo = {"Hoy": 1.0, "Últimos 7 días": 7.0, "Este Mes": 30.0, "Año 2026": 200.0}
    
    pesos_bancos = {
        "Todas las Entidades": 1.0,
        "BCP": 0.38,
        "BBVA": 0.26,
        "Interbank": 0.18,
        "Scotiabank": 0.10,
        "Banco de la Nación": 0.05,
        "BanBif": 0.03
    }
    
    pesos_canales = {
        "Todos los Canales": 1.0,
        "Tarjeta de Débito": 0.32,
        "Tarjeta de Crédito": 0.24,
        "Yape": 0.22,
        "Plin": 0.11,
        "Transferencia CCI": 0.07,
        "Cajero Automático (ATM)": 0.04
    }

    # CÁLCULO INDIVIDUAL Y ÚNICO SEGÚN LA SELECCIÓN
    f_periodo = pesos_periodo[periodo]
    f_banco = pesos_bancos[banco_sel]
    f_canal = pesos_canales[canal_sel]

    # CÁLCULO FINAL RECALCULADO CADA VEZ QUE CAMBIA UN DESPLEGABLE
    base_tx = int(41529 * f_periodo * f_banco * f_canal)
    monto_salvado = float(150670 * f_periodo * f_banco * f_canal)
    efectividad = round(99.0 + (f_banco * 0.8), 2)
    falsos_pos = round(0.9 - (f_canal * 0.2), 2)

    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Transacciones Evaluadas", f"{base_tx:,}", "+12% vs periodo anterior")
    col2.metric("Índice de Fraude Detenido", f"{efectividad}%", "+0.4%")
    col3.metric("Monto Salvaguardado", f"S/ {monto_salvado:,.2f}", "Actualizado al instante")
    col4.metric("Falsos Positivos", f"{falsos_pos}%", "-0.1%")
    
    st.markdown("---")
    c_left, c_right = st.columns(2)
    
    with c_left:
        st.subheader("Distribución de Transacciones por Canal")
        if canal_sel == "Todos los Canales":
            df_canal = pd.DataFrame({"Método": METODOS, "Volumen": np.random.randint(10000, 100000, len(METODOS))})
        else:
            df_canal = pd.DataFrame({"Método": [canal_sel, "Otros Canales"], "Volumen": [int(base_tx * 0.8), int(base_tx * 0.2)]})
            
        fig_canal = px.pie(df_canal, names="Método", values="Volumen", hole=0.4, color_discrete_sequence=px.colors.qualitative.Set2)
        st.plotly_chart(fig_canal, use_container_width=True)

    with c_right:
        st.subheader("Importancia de Variables en el Modelo de Riesgo (ML)")
        df_imp = pd.DataFrame({
            "Característica": [f.replace("_", " ").title() for f in FEATURES],
            "Importancia": model.feature_importances_
        }).sort_values("Importancia", ascending=True)
        
        fig_imp = px.bar(df_imp, x="Importancia", y="Característica", orientation="h", color="Importancia", color_continuous_scale="Viridis")
        st.plotly_chart(fig_imp, use_container_width=True)
# ======================================================================
# VISTA 2: MAPA POR PROVINCIAS
# ======================================================================
elif vista == "🗺️ Mapa Estadístico por Provincias":
    st.title("🗺️ Mapa Estadístico de Fraude por Provincias")
    st.caption("Concentración territorial del riesgo transaccional en el Perú.")
    
    np.random.seed(123)
    df_prov = pd.DataFrame({
        "Provincia": PROVINCIAS,
        "Transacciones": np.random.randint(10000, 500000, len(PROVINCIAS)),
        "Nivel_Riesgo": np.random.choice(["Bajo", "Medio", "Alto", "Crítico"], len(PROVINCIAS), p=[0.4, 0.3, 0.2, 0.1])
    })

    c_filt1, c_filt2, c_descarga = st.columns([2, 2, 1.5])
    
    with c_filt1:
        filtro_riesgo = st.selectbox("🎯 Filtrar por Nivel de Riesgo:", ["Todos", "Crítico", "Alto", "Medio", "Bajo"])

    with c_filt2:
        modo_vista = st.radio("👁️ Selecciona Modo de Vista:", ["📋 Tabla Detallada", "📊 Gráfico de Barras"], horizontal=True)

    with c_descarga:
        st.write(" ")
        csv_data = df_prov.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Descargar CSV",
            data=csv_data,
            file_name="reporte_fraude_provincias.csv",
            mime="text/csv",
            use_container_width=True
        )

    df_filtrado = df_prov if filtro_riesgo == "Todos" else df_prov[df_prov["Nivel_Riesgo"] == filtro_riesgo]

    st.markdown("---")

    if "Tabla" in modo_vista:
        st.subheader(f"Detalle de Provincias ({len(df_filtrado)} encontradas)")
        st.dataframe(df_filtrado, use_container_width=True, hide_index=True)
    else:
        st.subheader("Volumen Operativo por Provincia")
        fig_bar = px.bar(
            df_filtrado, 
            x="Provincia", 
            y="Transacciones", 
            color="Nivel_Riesgo", 
            color_discrete_map={"Bajo": "#2ECC71", "Medio": "#F39C12", "Alto": "#E67E22", "Crítico": "#E74C3C"},
            title="Transacciones Filtradas por Provincia"
        )
        st.plotly_chart(fig_bar, use_container_width=True)

# ======================================================================
# VISTA 3: EVALUADOR Y SIMULADOR EN VIVO
# ======================================================================
else:
    st.title("🔎 Evaluador de Transacciones en Tiempo Real")
    st.caption("Motor dinámico de inferencia en milisegundos para simulación de decisiones de riesgo.")

    st.subheader("💳 Datos de la Transacción Entrante")

    with st.form("form_evaluacion"):
        c1, c2, c3 = st.columns(3)
        with c1:
            monto = st.number_input("Monto de la Operación (S/.)", min_value=1.0, value=850.0, step=50.0)
            metodo = st.selectbox("Método de Pago", METODOS)
            banco = st.selectbox("Banco Origen", BANCOS)
        with c2:
            distancia = st.slider("Distancia desde Domicilio habitual (km)", 0.0, 100.0, 28.5)
            hora = st.slider("Hora de la Transacción (0-23h)", 0, 23, 3)
            categoria = st.selectbox("Categoría del Comercio", CATEGORIAS)
        with c3:
            provincia_eval = st.selectbox("Provincia de Operación", PROVINCIAS)
            comercio_nuevo = st.checkbox("¿Primera vez en este comercio?", value=True)
            dia_semana = st.selectbox("Día de la Semana", ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"], index=5)
            tx_recientes = st.slider("Transacciones en últimos 15 min", 1, 10, 4)

        btn_evaluar = st.form_submit_button("🔍 Evaluar Riesgo de Transacción Individual", type="primary", use_container_width=True)

    if btn_evaluar:
        start_time = time.time()
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
        latency = (time.time() - start_time) * 1000

        st.session_state.ultima_evaluacion = {
            "prob": prob,
            "latency": latency,
            "provincia": provincia_eval
        }

    if "ultima_evaluacion" in st.session_state:
        ev = st.session_state.ultima_evaluacion
        prob = ev["prob"]
        
        st.markdown("---")
        st.subheader("🛡️ Dictamen del Motor de Seguridad")

        if prob >= 0.65:
            st.error(f"🚨 **ACCIÓN BANCARIA: TRANSACCIÓN BLOQUEADA / RETENIDA**\n\n📍 **Ubicación:** Prov. {ev['provincia']} | Probabilidad de Fraude: **{prob*100:.1f}%** | Latencia: `{ev['latency']:.2f} ms`")
        elif 0.35 <= prob < 0.65:
            st.warning(f"🟡 **ACCIÓN BANCARIA: REQUIERE AUTENTICACIÓN REFORZADA (OTP / Facial)**\n\n📍 **Ubicación:** Prov. {ev['provincia']} | Probabilidad de Riesgo Moderado: **{prob*100:.1f}%** | Latencia: `{ev['latency']:.2f} ms`")
        else:
            st.success(f"✅ **ACCIÓN BANCARIA: TRANSACCIÓN APROBADA**\n\n📍 **Ubicación:** Prov. {ev['provincia']} | Nivel de Riesgo Seguro: **{prob*100:.1f}%** | Latencia: `{ev['latency']:.2f} ms`")

        st.progress(float(prob))

    # ----------------------------------------------------------------------
    # SIMULADOR EN TIEMPO REAL (GENERADOR AUTÓNOMO E INDEPENDIENTE)
    # ----------------------------------------------------------------------
    st.markdown("---")
    st.subheader("⚡ Simulador de Flujo Transaccional en Tiempo Real")
    st.caption("Monitoreo continuo estilo SOC con evaluación de métricas al vuelo y registro de auditoría.")

    if "historial_stream" not in st.session_state:
        st.session_state.historial_stream = []

    if "ejecutando_stream" not in st.session_state:
        st.session_state.ejecutando_stream = False

    col_ctrl1, col_ctrl2, col_ctrl3 = st.columns([2, 1, 1])
    with col_ctrl1:
        velocidad = st.select_slider("⚡ Velocidad del Stream:", options=["Lenta (1.5s)", "Normal (0.8s)", "Rápida (0.3s)"], value="Normal (0.8s)", key="slider_vel")
    
    with col_ctrl2:
        if not st.session_state.ejecutando_stream:
            if st.button("🔴 Iniciar Streaming", type="primary", use_container_width=True, key="btn_start"):
                st.session_state.ejecutando_stream = True
                st.rerun()
        else:
            if st.button("⏹️ Detener Streaming", type="secondary", use_container_width=True, key="btn_stop"):
                st.session_state.ejecutando_stream = False
                st.rerun()

    with col_ctrl3:
        if st.button("🗑️ Limpiar Log", use_container_width=True, key="btn_clear"):
            st.session_state.historial_stream = []
            st.session_state.ejecutando_stream = False
            st.rerun()

    delay_map = {"Lenta (1.5s)": 1.5, "Normal (0.8s)": 0.8, "Rápida (0.3s)": 0.3}
    delay_sec = delay_map[velocidad]

    kpi_placeholder = st.empty()
    feed_placeholder = st.empty()

    # GENERACIÓN DE EVENTOS EN VIVO 100% DINÁMICOS Y ALEATORIOS
    def generar_evento_stream():
        t_seed = int(time.time() * 1000) % 100000
        np.random.seed(t_seed)

        monto_val = float(np.random.choice([
            np.random.uniform(10, 150),
            np.random.uniform(150, 800),
            np.random.uniform(800, 2500),
            np.random.uniform(2500, 6000)
        ], p=[0.55, 0.25, 0.15, 0.05]))

        dist_val = float(np.random.choice([
            np.random.uniform(0.1, 5.0),
            np.random.uniform(5.0, 30.0),
            np.random.uniform(30.0, 85.0)
        ], p=[0.70, 0.20, 0.10]))

        hora_val = int(np.random.choice([np.random.randint(6, 23), np.random.randint(1, 5)], p=[0.85, 0.15]))
        metodo_val = str(np.random.choice(METODOS))
        banco_val = str(np.random.choice(BANCOS))
        prov_val = str(np.random.choice(PROVINCIAS))
        dia_val = int(np.random.randint(0, 7))
        tx_val = int(np.random.choice([1, 2, 3, 5, 7], p=[0.70, 0.15, 0.08, 0.05, 0.02]))
        nuevo_val = int(np.random.choice([0, 1], p=[0.80, 0.20]))

        f_df = pd.DataFrame([{
            "monto": monto_val,
            "distancia_km_home": dist_val,
            "comercio_nuevo": nuevo_val,
            "tx_ultimos_15min": tx_val,
            "hora_dia": hora_val,
            "dia_semana": dia_val,
            "es_madrugada": int(1 <= hora_val <= 5),
            "yape_plin_alto": int(metodo_val in ["Yape", "Plin"] and monto_val > 400),
            "fin_de_semana": int(dia_val in [5, 6]),
        }])[FEATURES]

        p = model.predict_proba(f_df)[0][1]

        if p >= 0.65:
            t_ev, txt, ico = "BLOQUEO", "BLOQUEADA / FRAUDE", "🚨"
        elif 0.35 <= p < 0.65:
            t_ev, txt, ico = "MFA", "REQUIERE OTP / FACIAL", "🟡"
        else:
            t_ev, txt, ico = "OK", "APROBADA", "✅"

        return {
            "Hora": time.strftime("%H:%M:%S"),
            "ID": f"TX-{np.random.randint(100000, 999999)}",
            "Estado": f"{ico} {txt}",
            "Monto": round(monto_val, 2),
            "Método": metodo_val,
            "Banco": banco_val,
            "Provincia": prov_val,
            "Tipo": t_ev
        }

    if st.session_state.ejecutando_stream:
        st.session_state.historial_stream.insert(0, generar_evento_stream())

    if len(st.session_state.historial_stream) > 0:
        df_h = pd.DataFrame(st.session_state.historial_stream)
        
        tot_tx = len(df_h)
        tot_bloq = len(df_h[df_h["Tipo"] == "BLOQUEO"])
        m_salvado = df_h[df_h["Tipo"] == "BLOQUEO"]["Monto"].sum()
        m_total = df_h["Monto"].sum()

        with kpi_placeholder.container():
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("Transacciones en Feed", f"{tot_tx} txs")
            k2.metric("Monto Procesado", f"S/ {m_total:,.2f}")
            k3.metric("Fraudes Bloqueados", f"{tot_bloq} casos")
            k4.metric("Monto en Riesgo Salvaguardado", f"S/ {m_salvado:,.2f}")

        with feed_placeholder.container():
            st.markdown("#### 📜 Feed Transaccional Registrado")
            st.dataframe(
                df_h[["Hora", "ID", "Estado", "Monto", "Método", "Banco", "Provincia"]].rename(
                    columns={"Monto": "Monto (S/)"}
                ),
                use_container_width=True,
                hide_index=True,
                height=350
            )

    if st.session_state.ejecutando_stream:
        time.sleep(delay_sec)
        st.rerun()