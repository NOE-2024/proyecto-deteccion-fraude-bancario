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
            # Cambiamos p=[0.88, 0.12] a 3 estados con mayor visibilidad de fraude y alertas
            "Estado": np.random.choice(
                ["Aprobada", "Bloqueada (Fraude)", "Alerta (Revisión)"], 
                n_samples, 
                p=[0.75, 0.15, 0.10]  # 75% Aprobadas, 15% Bloqueadas, 10% Alertas
            )
        })
        fig_scat = px.scatter(
            df_scatter, 
            x="Distancia (km)", 
            y="Monto (S/)", 
            color="Estado", 
            # Mapeo de colores para cada estado (Verde, Rojo, Amarillo)
            color_discrete_map={
                "Aprobada": "#2ECC71", 
                "Bloqueada (Fraude)": "#E74C3C",
                "Alerta (Revisión)": "#F1C40F"
            }
        )

# ======================================================================
# VISTA 2: MAPA POR PROVINCIAS
# ======================================================================
elif vista == "🗺️ Mapa Estadístico por Provincias":
    st.title("🗺️ Mapa Estadístico de Fraude por Provincias")
    st.caption("Concentración territorial del riesgo transaccional en el Perú y tasa de rechazos.")
    
    # Generación de datos con métricas de aprobación y rechazo
    np.random.seed(123)
    
    # Cálculo de métricas realistas según nivel de riesgo
    riesgos = np.random.choice(["Bajo", "Medio", "Alto", "Crítico"], len(PROVINCIAS), p=[0.35, 0.30, 0.20, 0.15])
    transacciones = np.random.randint(15000, 450000, len(PROVINCIAS))
    
    # Porcentajes de rechazo según riesgo
    pct_rechazo_map = {"Bajo": 0.02, "Medio": 0.08, "Alto": 0.18, "Crítico": 0.35}
    pct_alerta_map = {"Bajo": 0.05, "Medio": 0.12, "Alto": 0.22, "Crítico": 0.25}
    
    rechazadas = [int(t * pct_rechazo_map[r]) for t, r in zip(transacciones, riesgos)]
    alertas = [int(t * pct_alerta_map[r]) for t, r in zip(transacciones, riesgos)]
    aprobadas = [t - rec - alt for t, rec, alt in zip(transacciones, rechazadas, alertas)]
    
    df_prov = pd.DataFrame({
        "Provincia": PROVINCIAS,
        "Nivel_Riesgo": riesgos,
        "Transacciones Totales": transacciones,
        "🟢 Aprobadas": aprobadas,
        "🟡 En Alerta": alertas,
        "🔴 Bloqueadas (Fraude)": rechazadas,
        "% Rechazo": [round((rec / t) * 100, 2) for rec, t in zip(rechazadas, transacciones)]
    })

    # --- FILTROS Y CONTROLES ---
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

    # Filtrado dinámico
    if filtro_riesgo != "Todos":
        df_filtrado = df_prov[df_prov["Nivel_Riesgo"] == filtro_riesgo]
    else:
        df_filtrado = df_prov

    # KPI Summary Cards
    m1, m2, m3, m4 = st.columns(4)
    total_tx_sel = df_filtrado["Transacciones Totales"].sum()
    total_bloq_sel = df_filtrado["🔴 Bloqueadas (Fraude)"].sum()
    total_alt_sel = df_filtrado["🟡 En Alerta"].sum()
    tasa_bloqueo_prom = round((total_bloq_sel / total_tx_sel * 100), 2) if total_tx_sel > 0 else 0

    m1.metric("Provincias Mostradas", len(df_filtrado))
    m2.metric("Transacciones Evaluadas", f"{total_tx_sel:,}")
    m3.metric("Total Bloqueadas", f"{total_bloq_sel:,}", delta=f"{tasa_bloqueo_prom}% Tasa Global", delta_color="inverse")
    m4.metric("En Alerta (MFA)", f"{total_alt_sel:,}")

    st.markdown("---")

    # VISTA TABLA O GRÁFICO
    if "Tabla" in modo_vista:
        st.subheader(f"📋 Detalle por Provincia ({len(df_filtrado)} encontradas)")
        st.dataframe(
            df_filtrado, 
            use_container_width=True, 
            hide_index=True,
            column_config={
                "% Rechazo": st.column_config.NumberColumn(format="%.2f %%"),
                "Transacciones Totales": st.column_config.NumberColumn(format="%d"),
                "🟢 Aprobadas": st.column_config.NumberColumn(format="%d"),
                "🟡 En Alerta": st.column_config.NumberColumn(format="%d"),
                "🔴 Bloqueadas (Fraude)": st.column_config.NumberColumn(format="%d")
            }
        )
    else:
        st.subheader("📊 Comparativo de Transacciones Bloqueadas vs Aprobadas por Provincia")
        
        # Preparar datos desglosados para el gráfico de barras acumuladas
        df_melted = df_filtrado.melt(
            id_vars=["Provincia", "Nivel_Riesgo"], 
            value_vars=["🟢 Aprobadas", "🟡 En Alerta", "🔴 Bloqueadas (Fraude)"],
            var_name="Estado_Transaccion", 
            value_name="Cantidad"
        )
        
        fig_bar = px.bar(
            df_melted, 
            x="Provincia", 
            y="Cantidad", 
            color="Estado_Transaccion", 
            color_discrete_map={
                "🟢 Aprobadas": "#2ECC71", 
                "🟡 En Alerta": "#F1C40F", 
                "🔴 Bloqueadas (Fraude)": "#E74C3C"
            },
            title="Distribución del Estado de Transacciones por Provincia",
            labels={"Cantidad": "N° de Transacciones", "Provincia": "Provincia"}
        )
        st.plotly_chart(fig_bar, use_container_width=True)

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
        
        # 2. Listas extensas de Métodos y Bancos
        metodos_lista = ["Tarjeta de Débito", "Tarjeta de Crédito", "Transferencia CCI", "Yape / Plin", "Banca por Internet"]
        bancos_lista = ["BCP", "BBVA", "Interbank", "Scotiabank", "BanBif", "Pichincha"]
        
        metodo_final = str(np.random.choice(metodos_lista))
        banco_final = str(np.random.choice(bancos_lista))

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
        import time
        time.sleep(velocidad)
        st.rerun()

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