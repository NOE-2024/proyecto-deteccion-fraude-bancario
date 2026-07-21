import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import time

# ======================================================================
# CONFIGURACIÓN GENERAL DE LA PÁGINA
# ======================================================================
st.set_page_config(
    page_title="Sistema de Detección de Fraude Bancario",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constantes Globales
PROVINCIAS = [
    "Lima", "Arequipa", "Cusco", "La Libertad (Trujillo)", "Lambayeque (Chiclayo)",
    "Piura", "Junín (Huancayo)", "Puno", "Ica", "Tacna", "Ancash (Chimbote)", "Ucayali (Pucallpa)"
]

METODOS = ["Tarjeta de Débito", "Tarjeta de Crédito", "Transferencia CCI", "Yape / Plin", "Banca por Internet"]
BANCOS = ["BCP", "BBVA", "Interbank", "Scotiabank", "BanBif", "Pichincha"]

# ======================================================================
# BARRA LATERAL (NAVEGACIÓN Y FILTROS)
# ======================================================================
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2830/2830284.png", width=100)
st.sidebar.title("🛡️ SOC Fraude Banperú")
st.sidebar.caption("Sistema de Prevención y Monitoreo en Tiempo Real")

vista = st.sidebar.radio(
    "Navegación del Sistema:",
    [
        "📊 Dashboard General (Métricas Globales)",
        "🗺️ Análisis Geoespacial & Regiones",
        "🔎 Evaluador de Transacciones (Vista Horizontal)"
    ]
)

st.sidebar.markdown("---")
st.sidebar.subheader("🎛️ Filtros Globales de Red")
region_filtro = st.sidebar.selectbox("Filtrar por Región Base:", ["Todas las Regiones"] + PROVINCIAS)
nivel_riesgo_filtro = st.sidebar.select_slider("Sensibilidad de Reglas de Riesgo:", options=["Baja", "Media", "Alta", "Estricta (SOC)"])


# ======================================================================
# VISTA 1: DASHBOARD GENERAL
# ======================================================================
if vista == "📊 Dashboard General (Métricas Globales)":
    st.title("📊 Dashboard General de Prevención de Fraude")
    st.caption(f"Monitoreo de tráfico bancario nacional | Filtro Activo: **{region_filtro}** | Sensibilidad: **{nivel_riesgo_filtro}**")

    # KPIs Superiores
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    
    base_tx = 12450 if region_filtro == "Todas las Regiones" else 1850
    monto_eval = 4850200.00 if region_filtro == "Todas las Regiones" else 620400.00
    fraudes_detect = 142 if region_filtro == "Todas las Regiones" else 24
    monto_salvado = 385400.00 if region_filtro == "Todas las Regiones" else 48200.00

    kpi1.metric("Transacciones Evaluadas", f"{base_tx:,} txs", "▲ 12% vs mes anterior")
    kpi2.metric("Monto Total Procesado", f"S/ {monto_eval:,.2f}")
    kpi3.metric("Casos de Fraude Bloqueados", f"{fraudes_detect} casos", f"Tasa de Riesgo: {(fraudes_detect/base_tx)*100:.2f}%", delta_color="inverse")
    kpi4.metric("Capital Salvaguardado", f"S/ {monto_salvado:,.2f}", "Eficiencia del Modelo: 98.4%")

    st.markdown("---")

    # Gráficos Principales
    c_left, c_right = st.columns([1.5, 1])

    with c_left:
        st.subheader("Volumen de Transacciones y Detección de Fraudes por Hora")
        horas = [f"{i:02d}:00" for i in range(24)]
        tx_normales = np.random.poisson(lam=400, size=24)
        tx_fraudes = np.random.poisson(lam=12, size=24)
        
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(x=horas, y=tx_normales, mode='lines+markers', name='Transacciones Legítimas', line=dict(color='#2ECC71', width=2)))
        fig_trend.add_trace(go.Bar(x=horas, y=tx_fraudes, name='Alertas de Fraude Bloqueadas', marker=dict(color='#E74C3C')))
        fig_trend.update_layout(height=380, margin=dict(l=20, r=20, t=30, b=20), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig_trend, use_container_width=True)

    with c_right:
        st.subheader("Relación Monto vs Distancia de Domicilio")
        
        n_samples = 500
        df_scatter = pd.DataFrame({
            "Monto (S/)": np.random.exponential(scale=500, size=n_samples) + 10,
            "Distancia (km)": np.random.exponential(scale=15, size=n_samples),
            "Estado": np.random.choice(
                ["Aprobada", "Bloqueada (Fraude)", "Alerta (Revisión)"], 
                n_samples, 
                p=[0.80, 0.12, 0.08]
            )
        })
        fig_scat = px.scatter(
            df_scatter, 
            x="Distancia (km)", 
            y="Monto (S/)", 
            color="Estado", 
            color_discrete_map={
                "Aprobada": "#2ECC71", 
                "Bloqueada (Fraude)": "#E74C3C",
                "Alerta (Revisión)": "#F1C40F"
            }
        )
        st.plotly_chart(fig_scat, use_container_width=True)


# ======================================================================
# VISTA 2: ANÁLISIS GEOESPACIAL Y REGIONES
# ======================================================================
elif vista == "🗺️ Análisis Geoespacial & Regiones":
    st.title("🗺️ Análisis Geoespacial y Distribución de Riesgo Regional")
    st.caption("Identificación de patrones territoriales y focos de fraude interprovincial.")

    data_regiones = []
    for prov in PROVINCIAS:
        txs = np.random.randint(1500, 8500)
        fraudes = np.random.randint(30, 320)
        monto = np.random.uniform(500000, 4800000)
        data_regiones.append({
            "Provincia / Región": prov,
            "Transacciones Total": txs,
            "Casos Bloqueados": fraudes,
            "Tasa de Fraude (%)": round((fraudes / txs) * 100, 2),
            "Monto Total (S/)": round(monto, 2)
        })

    df_regiones = pd.DataFrame(data_regiones)

    col_g1, col_g2 = st.columns([1.5, 1])

    with col_g1:
        st.subheader("Tasa de Fraude (%) por Provincia")
        fig_bar = px.bar(
            df_regiones.sort_values(by="Tasa de Fraude (%)", ascending=True),
            x="Tasa de Fraude (%)",
            y="Provincia / Región",
            orientation="h",
            color="Tasa de Fraude (%)",
            color_continuous_scale="Reds",
            text="Tasa de Fraude (%)"
        )
        fig_bar.update_layout(height=480)
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_g2:
        st.subheader("Resumen Métrico Territorial")
        st.dataframe(
            df_regiones,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Monto Total (S/)": st.column_config.NumberColumn(format="S/ %.2f"),
                "Tasa de Fraude (%)": st.column_config.NumberColumn(format="%.2f %%")
            }
        )


# ======================================================================
# VISTA 3: EVALUADOR Y SIMULADOR (DISEÑO HORIZONTAL EN COLUMNAS)
# ======================================================================
elif vista == "🔎 Evaluador de Transacciones (Vista Horizontal)":
    st.title("⚡ Simulador y Evaluador Transaccional en Vivo")
    st.caption("Panel interactivo horizontal para simulación continua o evaluación individual de riesgo.")

    # Inicializar estado
    if "stream_data" not in st.session_state:
        st.session_state["stream_data"] = []

    # DISPOSICIÓN HORIZONTAL EN DOS COLUMNAS PRINCIPALES
    col_izquierda, col_derecha = st.columns([1, 1.3])

    # ------------------------------------------------------------------
    # COLUMNA IZQUIERDA: CONTROLES DE SIMULACIÓN / SIMULADOR MANUAL
    # ------------------------------------------------------------------
    with col_izquierda:
        st.subheader("🎛️ Configuración de Simulación")
        
        region_sel = st.selectbox("📍 Selección de Provincia / Región:", ["Todas las Regiones"] + PROVINCIAS)
        perfil_sim = st.selectbox("🛡️ Escenario de Riesgo:", ["Operación Normal (Bajo Riesgo)", "Simulación de Ataque Masivo", "Modo Alta Seguridad"])
        velocidad = st.slider("⚡ Velocidad de refresco (s):", 0.1, 2.0, 0.8, step=0.1)

        c_sw1, c_sw2 = st.columns(2)
        with c_sw1:
            run_stream = st.checkbox("🔴 Streaming Activo", value=False)
        with c_sw2:
            if st.button("🗑️ Limpiar Historial"):
                st.session_state["stream_data"] = []
                st.rerun()

        st.markdown("---")
        st.subheader("📝 Simulación Manual Rápida")
        
        with st.form("form_manual"):
            f_monto = st.number_input("Monto (S/):", min_value=10.0, max_value=20000.0, value=350.0)
            f_dist = st.slider("Distancia (km):", 0.0, 200.0, 12.0)
            btn_insertar = st.form_submit_button("⚡ Inyectar Transacción Manual")

        if btn_insertar:
            # Determinación de estado para la transacción manual
            if f_monto > 3000 or f_dist > 80:
                est_man = "🔴 BLOQUEADA / FRAUDE"
            elif f_monto > 1000 or f_dist > 30:
                est_man = "🟡 REQUIERE OTP / FACIAL"
            else:
                est_man = "🟢 APROBADA"

            nueva_manual = {
                "Hora": pd.Timestamp.now().strftime("%H:%M:%S"),
                "ID": f"TX-{np.random.randint(100000, 999999)}",
                "Estado": est_man,
                "Monto (S/)": round(f_monto, 2),
                "Distancia (km)": round(f_dist, 1),
                "Método": np.random.choice(METODOS),
                "Banco": np.random.choice(BANCOS),
                "Provincia": region_sel if region_sel != "Todas las Regiones" else np.random.choice(PROVINCIAS)
            }
            st.session_state["stream_data"].insert(0, nueva_manual)

    # ------------------------------------------------------------------
    # BUCLE DE GENERACIÓN DE STREAMING AUTOMÁTICO
    # ------------------------------------------------------------------
    if run_stream:
        prov_final = region_sel if region_sel != "Todas las Regiones" else str(np.random.choice(PROVINCIAS))
        monto_rand = round(float(np.random.choice([25.50, 120.00, 450.00, 1500.00, 4200.00], p=[0.40, 0.35, 0.15, 0.07, 0.03])), 2)
        distancia_rand = round(float(np.random.uniform(0.5, 120.0)), 1)

        if perfil_sim == "Operación Normal (Bajo Riesgo)":
            p_dist = [0.75, 0.15, 0.05, 0.05]
        elif perfil_sim == "Simulación de Ataque Masivo":
            p_dist = [0.30, 0.20, 0.20, 0.30]
        else:
            p_dist = [0.55, 0.20, 0.10, 0.15]

        estados_posibles = ["🟢 APROBADA", "🟡 REQUIERE OTP / FACIAL", "🟠 EN INVESTIGACIÓN (SOC)", "🔴 BLOQUEADA / FRAUDE"]
        estado_eval = str(np.random.choice(estados_posibles, p=p_dist))

        nueva_tx = {
            "Hora": pd.Timestamp.now().strftime("%H:%M:%S"),
            "ID": f"TX-{np.random.randint(100000, 999999)}",
            "Estado": estado_eval,
            "Monto (S/)": monto_rand,
            "Distancia (km)": distancia_rand,
            "Método": str(np.random.choice(METODOS)),
            "Banco": str(np.random.choice(BANCOS)),
            "Provincia": prov_final
        }

        st.session_state["stream_data"].insert(0, nueva_tx)
        
        # Guardar hasta 200 registros en el historial
        if len(st.session_state["stream_data"]) > 200:
            st.session_state["stream_data"].pop()

    # ------------------------------------------------------------------
    # COLUMNA DERECHA: MÉTRICAS Y FEED EN VIVO
    # ------------------------------------------------------------------
    with col_derecha:
        st.subheader("📊 Métricas de Tráfico en Vivo")
        
        df_stream = pd.DataFrame(st.session_state["stream_data"])

        if not df_stream.empty:
            total_txs = len(df_stream)
            monto_total = df_stream["Monto (S/)"].sum()
            df_bloq = df_stream[df_stream["Estado"] == "🔴 BLOQUEADA / FRAUDE"]
            casos_bloqueados = len(df_bloq)
            monto_salvado = df_bloq["Monto (S/)"].sum()
        else:
            total_txs, monto_total, casos_bloqueados, monto_salvado = 0, 0.0, 0, 0.0

        m1, m2 = st.columns(2)
        m1.metric("Transacciones Evaluadas", f"{total_txs} txs")
        m2.metric("Monto Total Procesado", f"S/ {monto_total:,.2f}")

        m3, m4 = st.columns(2)
        m3.metric("Fraudes Bloqueados", f"{casos_bloqueados} casos", delta_color="inverse")
        m4.metric("Monto Salvaguardado", f"S/ {monto_salvado:,.2f}")

        st.markdown("---")
        st.subheader("📜 Feed Transaccional (Registros)")

        if not df_stream.empty:
            st.dataframe(
                df_stream,
                use_container_width=True,
                hide_index=True,
                height=380,
                column_config={
                    "Monto (S/)": st.column_config.NumberColumn(format="S/ %.2f"),
                    "Distancia (km)": st.column_config.NumberColumn(format="%.1f km")
                }
            )
        else:
            st.info("💡 Activa **'🔴 Streaming Activo'** o inyecta una transacción manual para ver el tráfico en vivo.")

    # Refresco en bucle
    if run_stream:
        time.sleep(velocidad)
        st.rerun()