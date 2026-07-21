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
# SIMULACIÓN / CARGA DE MODELO ENTRENADO
# ----------------------------------------------------------------------
@st.cache_resource
def cargar_modelo():
    np.random.seed(42)
    n = 1000
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
    y = ((df_train["monto"] > 1000) & (df_train["es_madrugada"] == 1) | (df_train["distancia_km_home"] > 30)).astype(int)
    rf = RandomForestClassifier(n_estimators=50, random_state=42)
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
st.sidebar.caption("🔒 Versión del Core: 3.4.1")
st.sidebar.caption("⚡ SLA de Latencia: < 25 ms")

# ======================================================================
# VISTA 1: DASHBOARD GENERAL (AHORA TOTALMENTE DINÁMICO)
# ======================================================================
if vista == "📊 Dashboard General de Riesgos":
    st.title("📊 Dashboard General de Riesgos y Fraude Bancario")
    st.caption("Visión ejecutiva del comportamiento de transacciones a nivel nacional con controles dinámicos.")
    
    # --- FILTROS DINÁMICOS ---
    f_col1, f_col2, f_col3 = st.columns(3)
    with f_col1:
        periodo = st.selectbox("📅 Período Evaluado:", ["Hoy", "Últimos 7 días", "Este Mes", "Año 2026"])
    with f_col2:
        banco_sel = st.selectbox("🏦 Entidad Bancaria:", ["Todas las Entidades"] + BANCOS)
    with f_col3:
        canal_sel = st.selectbox("💳 Canal de Pago:", ["Todos los Canales"] + METODOS)

    # Generación/Cálculo dinámico basado en filtros
    multiplicador = {"Hoy": 1, "Últimos 7 días": 7, "Este Mes": 30, "Año 2026": 200}[periodo]
    if banco_sel != "Todas las Entidades":
        multiplicador *= 0.25
    if canal_sel != "Todos los Canales":
        multiplicador *= 0.2

    base_tx = int(41529 * multiplicador)
    monto_salvado = float(150670 * multiplicador)
    efectividad = round(99.2 + (np.random.rand() * 0.5 - 0.25), 2)
    falsos_pos = round(0.8 + (np.random.rand() * 0.2 - 0.1), 2)

    st.markdown("---")
    
    # Métricas dinámicas
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Transacciones Evaluadas", f"{base_tx:,}", "+12% vs periodo anterior")
    col2.metric("Índice de Fraude Detenido", f"{efectividad}%", "+0.4%")
    col3.metric("Monto Salvaguardado", f"S/ {monto_salvado:,.2f}", "Actualizado al instante")
    col4.metric("Falsos Positivos", f"{falsos_pos}%", "-0.1%")
    
    st.markdown("---")
    c_left, c_right = st.columns(2)
    
    with c_left:
        st.subheader("Distribución de Transacciones por Canal")
        
        # Filtrado dinámico del gráfico de torta
        if canal_sel == "Todos los Canales":
            df_canal = pd.DataFrame({"Método": METODOS, "Volumen": np.random.randint(10000, 100000, len(METODOS))})
        else:
            df_canal = pd.DataFrame({"Método": [canal_sel, "Otros Canales"], "Volumen": [int(base_tx * 0.7), int(base_tx * 0.3)]})
            
        fig_canal = px.pie(df_canal, names="Método", values="Volumen", hole=0.4, color_discrete_sequence=px.colors.qualitative.Set2)
        st.plotly_chart(fig_canal, use_container_width=True)

    with c_right:
        st.subheader("Relación Monto vs Distancia de Domicilio")
        
        n_samples = min(200, max(30, int(base_tx / 100)))
        df_scatter = pd.DataFrame({
            "Monto (S/)": np.random.uniform(10, 4000, n_samples),
            "Distancia (km)": np.random.uniform(0, 60, n_samples),
            "Estado": np.random.choice(["Aprobada", "Sospechosa / Fraude"], n_samples, p=[0.88, 0.12])
        })
        fig_scat = px.scatter(
            df_scatter, 
            x="Distancia (km)", 
            y="Monto (S/)", 
            color="Estado", 
            color_discrete_map={"Aprobada": "#2ECC71", "Sospechosa / Fraude": "#E74C3C"}
        )
        st.plotly_chart(fig_scat, use_container_width=True)

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
        filtro_riesgo = st.selectbox(
            "🎯 Filtrar por Nivel de Riesgo:",
            ["Todos", "Crítico", "Alto", "Medio", "Bajo"]
        )

    with c_filt2:
        modo_vista = st.radio(
            "👁️ Selecciona Modo de Vista:",
            ["📋 Tabla Detallada", "📊 Gráfico de Barras"],
            horizontal=True
        )

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

    if filtro_riesgo != "Todos":
        df_filtrado = df_prov[df_prov["Nivel_Riesgo"] == filtro_riesgo]
    else:
        df_filtrado = df_prov

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
# VISTA 3: EVALUADOR EN TIEMPO REAL Y SIMULADOR
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

        btn_evaluar = st.form_submit_button("🔍 Evaluar Riesgo de Transacción", type="primary", use_container_width=True)

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
            "provincia": provincia_eval,
            "hora": hora,
            "metodo": metodo,
            "monto": monto,
            "distancia": distancia,
            "tx_recientes": tx_recientes,
            "categoria": categoria,
            "comercio_nuevo": comercio_nuevo,
            "dia_semana": dia_semana
        }

    if "ultima_evaluacion" in st.session_state:
        ev = st.session_state.ultima_evaluacion
        prob = ev["prob"]
        
        st.markdown("---")
        st.subheader("🛡️ Dictamen del Motor de Seguridad")

        if prob >= 0.65:
            st.error(
                f"🚨 **ACCIÓN BANCARIA: TRANSACCIÓN BLOQUEADA / RETENIDA**\n\n"
                f"📍 **Ubicación:** Prov. {ev['provincia']} | "
                f"Probabilidad de Fraude: **{prob*100:.1f}%** | "
                f"Tiempo de Respuesta: `{ev['latency']:.2f} ms`"
            )
        elif 0.35 <= prob < 0.65:
            st.warning(
                f"🟡 **ACCIÓN BANCARIA: REQUIERE AUTENTICACIÓN REFORZADA (OTP / Facial)**\n\n"
                f"📍 **Ubicación:** Prov. {ev['provincia']} | "
                f"Probabilidad de Riesgo Moderado: **{prob*100:.1f}%** | "
                f"Latencia: `{ev['latency']:.2f} ms`"
            )
        else:
            st.success(
                f"✅ **ACCIÓN BANCARIA: TRANSACCIÓN APROBADA**\n\n"
                f"📍 **Ubicación:** Prov. {ev['provincia']} | "
                f"Nivel de Riesgo Seguro: **{prob*100:.1f}%** | "
                f"Latencia: `{ev['latency']:.2f} ms`"
            )

        st.markdown("#### 🔍 Factores de Riesgo Detectados:")
        factores_hallados = False

        if 1 <= ev["hora"] <= 5:
            st.write("• ⚠️ **Horario Atípico:** Operación realizada en horario nocturno/madrugada (1 AM - 5 AM).")
            factores_hallados = True

        if "categoria" in ev:
            if "ATM" in ev["categoria"] or "Cajero" in ev["categoria"]:
                st.write("• ⚠️ **Canal Físico Crítico (ATM):** Retiro de efectivo presencial en Cajero Automático.")
                factores_hallados = True
            elif "E-commerce" in ev["categoria"] or "Web" in ev["categoria"]:
                st.write("• ⚠️ **Comercio Digital (E-commerce):** Operación en línea sin presencia física de tarjeta.")
                factores_hallados = True

        if ev["metodo"] in ["Yape", "Plin"] and ev["monto"] > 400:
            st.write(f"• ⚠️ **Anomalía en Monedero Digital:** Operación por {ev['metodo']} (S/ {ev['monto']:,.2f}) supera el umbral seguro de S/ 400.")
            factores_hallados = True
        elif ev["monto"] >= 800:
            st.write(f"• ⚠️ **Monto Elevado:** Importe de la transacción (S/ {ev['monto']:,.2f}) excede el promedio habitual.")
            factores_hallados = True

        if ev["distancia"] > 20:
            st.write(f"• ⚠️ **Geolocalización Inusual:** Transacción realizada a {ev['distancia']:.1f} km del domicilio registrado.")
            factores_hallados = True

        if ev["tx_recientes"] >= 3:
            st.write(f"• ⚠️ **Alta Velocidad Operativa:** Frecuencia de {ev['tx_recientes']} transacciones en los últimos 15 minutos.")
            factores_hallados = True

        if ev.get("comercio_nuevo", True):
            st.write("• ⚠️ **Comercio Sin Historial:** Primera interacción registrada del usuario con este establecimiento.")
            factores_hallados = True

        if ev.get("dia_semana") in ["Sábado", "Domingo"]:
            st.write(f"• ⚠️ **Patrón de Fin de Semana:** Transacción efectuada en día {ev.get('dia_semana')}.")
            factores_hallados = True

        if not factores_hallados:
            st.write("• ✅ **Sin anomalías detectadas:** La operación se ajusta al perfil de comportamiento habitual.")

        st.progress(float(prob))

    # ----------------------------------------------------------------------
    # SIMULADOR DE FLUJO TRANSACCIONAL EN TIEMPO REAL
    # ----------------------------------------------------------------------
    st.markdown("---")
    st.subheader("⚡ Simulador de Flujo Transaccional en Tiempo Real")
    st.caption("Monitoreo continuo estilo SOC/Fintech con evaluación de métricas al vuelo y registro de auditoría.")

    if "historial_stream" not in st.session_state:
        st.session_state.historial_stream = []

    if "ejecutando_stream" not in st.session_state:
        st.session_state.ejecutando_stream = False

    col_ctrl1, col_ctrl2, col_ctrl3 = st.columns([2, 1, 1])
    with col_ctrl1:
        velocidad = st.select_slider(
            "⚡ Velocidad del Stream:", 
            options=["Lenta (1.5s)", "Normal (0.8s)", "Rápida (0.3s)"], 
            value="Normal (0.8s)",
            key="slider_velocidad_stream"
        )
    
    with col_ctrl2:
        if not st.session_state.ejecutando_stream:
            if st.button("🔴 Iniciar Streaming", type="primary", use_container_width=True, key="btn_iniciar_stream"):
                st.session_state.ejecutando_stream = True
                st.rerun()
        else:
            if st.button("⏹️ Detener Streaming", type="secondary", use_container_width=True, key="btn_detener_stream"):
                st.session_state.ejecutando_stream = False
                st.rerun()

    with col_ctrl3:
        if st.button("🗑️ Limpiar Log", use_container_width=True, key="btn_limpiar_stream"):
            st.session_state.historial_stream = []
            st.session_state.ejecutando_stream = False
            st.rerun()

    delay_map = {"Lenta (1.5s)": 1.5, "Normal (0.8s)": 0.8, "Rápida (0.3s)": 0.3}
    delay_sec = delay_map[velocidad]

    kpi_placeholder = st.empty()
    feed_placeholder = st.empty()

    if st.session_state.ejecutando_stream:
        hora_actual = time.strftime("%H:%M:%S")
        dia_idx = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"].index(dia_semana)

        fila_sim = pd.DataFrame([{
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
        
        prob_sim = model.predict_proba(fila_sim)[0][1]

        if prob_sim >= 0.65:
            tipo_evento, estado_txt, icono = "BLOQUEO", "BLOQUEADA / FRAUDE", "🚨"
        elif 0.35 <= prob_sim < 0.65:
            tipo_evento, estado_txt, icono = "MFA", "REQUIERE OTP / FACIAL", "🟡"
        else:
            tipo_evento, estado_txt, icono = "OK", "APROBADA", "✅"

        nuevo_registro = {
            "Hora": hora_actual,
            "ID": f"TX-{np.random.randint(100000, 999999)}",
            "Estado": f"{icono} {estado_txt}",
            "Monto": monto,
            "Método": metodo,
            "Banco": banco,
            "Provincia": provincia_eval,
            "Tipo": tipo_evento
        }
        st.session_state.historial_stream.insert(0, nuevo_registro)

        df_hist = pd.DataFrame(st.session_state.historial_stream)
        tot_tx = len(df_hist)
        tot_bloqueadas = len(df_hist[df_hist["Tipo"] == "BLOQUEO"])
        monto_riesgo = df_hist[df_hist["Tipo"] == "BLOQUEO"]["Monto"].sum()
        monto_procesado = df_hist["Monto"].sum()

        with kpi_placeholder.container():
            mk1, mk2, mk3, mk4 = st.columns(4)
            mk1.metric("Transacciones en Feed", f"{tot_tx} txs")
            mk2.metric("Monto Procesado", f"S/ {monto_procesado:,.2f}")
            mk3.metric("Fraudes Bloqueados", f"{tot_bloqueadas} casos", delta_color="inverse")
            mk4.metric("Monto en Riesgo Salvaguardado", f"S/ {monto_riesgo:,.2f}", delta_color="inverse")

        with feed_placeholder.container():
            st.markdown("#### 📜 Feed Transaccional en Vivo")
            st.dataframe(
                df_hist[["Hora", "ID", "Estado", "Monto", "Método", "Banco", "Provincia"]].rename(
                    columns={"Monto": "Monto (S/)"}
                ),
                use_container_width=True,
                hide_index=True,
                height=300
            )

        time.sleep(delay_sec)
        st.rerun()

    elif len(st.session_state.historial_stream) > 0:
        df_hist = pd.DataFrame(st.session_state.historial_stream)
        tot_tx = len(df_hist)
        tot_bloqueadas = len(df_hist[df_hist["Tipo"] == "BLOQUEO"])
        monto_riesgo = df_hist[df_hist["Tipo"] == "BLOQUEO"]["Monto"].sum()
        monto_procesado = df_hist["Monto"].sum()

        with kpi_placeholder.container():
            mk1, mk2, mk3, mk4 = st.columns(4)
            mk1.metric("Transacciones en Feed", f"{tot_tx} txs")
            mk2.metric("Monto Procesado", f"S/ {monto_procesado:,.2f}")
            mk3.metric("Fraudes Bloqueados", f"{tot_bloqueadas} casos")
            mk4.metric("Monto en Riesgo Salvaguardado", f"S/ {monto_riesgo:,.2f}")

        with feed_placeholder.container():
            st.markdown("#### 📜 Feed Transaccional Registrado")
            st.dataframe(
                df_hist[["Hora", "ID", "Estado", "Monto", "Método", "Banco", "Provincia"]].rename(
                    columns={"Monto": "Monto (S/)"}
                ),
                use_container_width=True,
                hide_index=True,
                height=300
            )