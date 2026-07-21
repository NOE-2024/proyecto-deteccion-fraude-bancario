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

# Constantes Globales para Simulación
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
        "🔎 Evaluador de Transacciones (En Vivo)"
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
        
        n_samples = min(200, max(30, int(base_tx / 100)))
        df_scatter = pd.DataFrame({
            "Monto (S/)": np.random.uniform(10, 4000, n_samples),
            "Distancia (km)": np.random.uniform(0, 60, n_samples),
            "Estado": np.random.choice(
                ["Aprobada", "Bloqueada (Fraude)", "Alerta (Revisión)"], 
                n_samples, 
                p=[0.75, 0.15, 0.10]
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

    # Generar data sintética regional
    data_regiones = []
    for prov in PROVINCIAS:
        txs = np.random.randint(500, 3500)
        fraudes = np.random.randint(10, 120)
        monto = np.random.uniform(150000, 1800000)
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
# VISTA 3: SIMULADOR DE FLUJO TRANSACCIONAL EN TIEMPO REAL
# ======================================================================
elif vista == "🔎 Evaluador de Transacciones (En Vivo)":
    st.title("⚡ Simulador de Flujo Transaccional en Tiempo Real")
    st.caption("Monitoreo continuo estilo SOC/Fintech con evaluación dinámica por regiones y reglas de decisión.")

    # --- CONTROLES DE SIMULACIÓN Y SELECCIÓN REGIONAL ---
    ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([2, 2, 1])
    
    with ctrl_col1:
        region_sel = st.selectbox(
            "📍 Seleccionar Provincia / Región:",
            ["Todas las Regiones"] + PROVINCIAS
        )
    
    with ctrl_col2:
        perfil_sim = st.selectbox(
            "🛡️ Escenario de Tráfico:",
            ["Operación Normal (Bajo Riesgo)", "Simulación de Ataque Masivo", "Modo Alta Seguridad"]
        )
        
    with ctrl_col3:
        velocidad = st.slider("⚡ Velocidad (s):", 0.1, 2.0, 0.8, step=0.1)

    st.markdown("---")

    # Botones de Control
    c_btn1, c_btn2, _ = st.columns([1.5, 1.5, 3])
    with c_btn1:
        run_stream = st.checkbox("🔴 Iniciar Streaming", value=False)
    with c_btn2:
        if st.button("🗑️ Limpiar Historial Log"):
            st.session_state["stream_data"] = []
            st.rerun()

    # Memoria de sesión
    if "stream_data" not in st.session_state:
        st.session_state["stream_data"] = []

    # --- BUCLE DE GENERACIÓN DE DATOS VARIADOS ---
    if run_stream:
        # 1. Asignación de Región/Provincia
        if region_sel != "Todas las Regiones":
            prov_final = region_sel
        else:
            prov_final = str(np.random.choice(PROVINCIAS))
        
        # 2. Selección de Método y Banco
        metodo_final = str(np.random.choice(METODOS))
        banco_final = str(np.random.choice(BANCOS))

        # 3. Variabilidad Realista de Montos y Distancias
        monto_rand = round(float(np.random.choice([25.50, 85.00, 240.00, 890.00, 3200.00, 9500.00], p=[0.35, 0.30, 0.20, 0.08, 0.05, 0.02])), 2)
        distancia_rand = round(float(np.random.uniform(0.5, 150.0)), 1)

        # 4. Probabilidades de Estado según el escenario seleccionado
        if perfil_sim == "Operación Normal (Bajo Riesgo)":
            p_dist = [0.75, 0.12, 0.08, 0.05] # 75% Aprobada, 12% OTP, 8% SOC, 5% Bloqueo
        elif perfil_sim == "Simulación de Ataque Masivo":
            p_dist = [0.30, 0.20, 0.20, 0.30] # 30% Aprobada, 20% OTP, 20% SOC, 30% Bloqueo
        else: # Modo Alta Seguridad
            p_dist = [0.55, 0.20, 0.10, 0.15]

        # Estados Versátiles
        estados_posibles = [
            "🟢 APROBADA", 
            "🟡 REQUIERE OTP / FACIAL", 
            "🟠 EN INVESTIGACIÓN (SOC)", 
            "🔴 BLOQUEADA / FRAUDE"
        ]
        
        estado_eval = str(np.random.choice(estados_posibles, p=p_dist))

        # Registrar la nueva transacción
        nueva_tx = {
            "Hora": pd.Timestamp.now().strftime("%H:%M:%S"),
            "ID": f"TX-{np.random.randint(100000, 999999)}",
            "Estado": estado_eval,
            "Monto (S/)": monto_rand,
            "Distancia (km)": distancia_rand,
            "Método": metodo_final,
            "Banco": banco_final,
            "Provincia": prov_final
        }

        st.session_state["stream_data"].insert(0, nueva_tx)
        
        # Mantener solo los últimos 50 registros en memoria
        if len(st.session_state["stream_data"]) > 50:
            st.session_state["stream_data"].pop()

    # --- DATAFRAME Y MÉTRICAS EN TIEMPO REAL ---
    df_stream = pd.DataFrame(st.session_state["stream_data"])

    if not df_stream.empty:
        total_txs = len(df_stream)
        monto_total = df_stream["Monto (S/)"].sum()
        
        df_bloq = df_stream[df_stream["Estado"] == "🔴 BLOQUEADA / FRAUDE"]
        df_alertas = df_stream[df_stream["Estado"].isin(["🟡 REQUIERE OTP / FACIAL", "🟠 EN INVESTIGACIÓN (SOC)"])]
        
        casos_bloqueados = len(df_bloq)
        casos_alertas = len(df_alertas)
        monto_salvado = df_bloq["Monto (S/)"].sum()
    else:
        total_txs, monto_total, casos_bloqueados, casos_alertas, monto_salvado = 0, 0.0, 0, 0, 0.0

    # Panel de Métricas (KPIs)
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Transacciones Evaluadas", f"{total_txs} txs", f"Filtro: {region_sel}")
    k2.metric("Monto Procesado", f"S/ {monto_total:,.2f}")
    k3.metric("Fraudes Bloqueados", f"{casos_bloqueados} casos", delta=f"{casos_alertas} Alertas/Investigación", delta_color="inverse")
    k4.metric("Monto Salvaguardado", f"S/ {monto_salvado:,.2f}")

    st.markdown("---")
    st.subheader(f"📜 Feed Transaccional Registrado — {region_sel}")

    if not df_stream.empty:
        st.dataframe(
            df_stream,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Monto (S/)": st.column_config.NumberColumn(format="S/ %.2f"),
                "Distancia (km)": st.column_config.NumberColumn(format="%.1f km")
            }
        )
    else:
        st.info("💡 Haz clic en el interruptor **'🔴 Iniciar Streaming'** para comenzar la simulación en tiempo real.")

    # Bucle de refresco continuo
    if run_stream:
        time.sleep(velocidad)
        st.rerun()