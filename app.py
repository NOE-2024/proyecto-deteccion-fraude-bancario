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
        "🔎 Evaluador Simulación de Fraude (Individual)"
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
        
        # Muestra amplia de datos (500 casos)
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

    # Generar data sintética regional
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
# VISTA 3: SIMULADOR INTERACTIVO DE FRAUDE (EVALUACIÓN MANUAL)
# ======================================================================
elif vista == "🔎 Evaluador Simulación de Fraude (Individual)":
    st.title("🔎 Evaluador y Simulador de Operaciones de Fraude")
    st.caption("Ingrese los parámetros de una transacción puntual para evaluar el score de riesgo en tiempo real.")

    col_form, col_res = st.columns([1.2, 1])

    with col_form:
        st.subheader("📋 Datos de la Transacción a Simular")
        
        with st.form("form_fraude"):
            f_banco = st.selectbox("🏦 Banco Origen:", BANCOS)
            f_metodo = st.selectbox("💳 Método de Pago:", METODOS)
            f_provincia = st.selectbox("📍 Ubicación / Provincia de la TX:", PROVINCIAS)
            
            f_monto = st.number_input("💰 Monto de la Transacción (S/):", min_value=1.0, max_value=50000.0, value=250.0, step=50.0)
            f_distancia = st.slider("📏 Distancia respecto al Domicilio (km):", 0.0, 500.0, 5.0)
            f_hora = st.time_input("⏰ Hora de Intento de Operación:")
            f_intento_fallido = st.slider("⚠️ Intentos de Contraseña/OTP Fallidos Previos:", 0, 5, 0)
            
            btn_evaluar = st.form_submit_button("⚡ EVALUAR TRANSACCIÓN (ANALIZAR RIESGO)")

    with col_res:
        st.subheader("📊 Diagnóstico del Modelo de Inteligencia Artificial")
        
        if btn_evaluar:
            # Lógica de cálculo de score de riesgo sintético
            score_riesgo = 0.05
            
            if f_monto > 2500:
                score_riesgo += 0.35
            elif f_monto > 800:
                score_riesgo += 0.15
                
            if f_distancia > 100:
                score_riesgo += 0.30
            elif f_distancia > 30:
                score_riesgo += 0.15
                
            if f_intento_fallido >= 2:
                score_riesgo += 0.30
                
            hora_num = f_hora.hour
            if 0 <= hora_num <= 5: # Madrugada aumenta riesgo
                score_riesgo += 0.20
                
            score_final = min(round(score_riesgo * 100, 1), 99.9)

            # Mostrar resultado según el Score
            st.markdown(f"### Score de Riesgo Calculado: **{score_final}%**")
            st.progress(int(score_final))

            if score_final >= 65.0:
                st.error("🚨 **RESULTADO: TRANSACCIÓN BLOQUEADA POR ALTO RIESGO DE FRAUDE**")
                st.warning("""
                **Factores de Alerta Detectados:**
                * Monto o localización fuera del patrón habitual del cliente.
                * Anomalía de horario/intentos fallidos en el acceso.
                * **Acción ejecutada:** Transacción rechazada y cuenta en congelamiento preventivo.
                """)
            elif score_final >= 35.0:
                st.warning("🟡 **RESULTADO: REQUIERE VERIFICACIÓN ADICIONAL (MFA)**")
                st.info("""
                **Factores de Alerta Detectados:**
                * Riesgo moderado detectado.
                * **Acción ejecutada:** Se ha enviado un código OTP al celular registrado y solicitud de biometría facial.
                """)
            else:
                st.success("🟢 **RESULTADO: TRANSACCIÓN APROBADA (OPERACIÓN LEGÍTIMA)**")
                st.caption("Los parámetros coinciden con el perfil histórico del usuario.")
        else:
            st.info("👈 Ingresa los datos en el formulario de la izquierda y presiona **'EVALUAR TRANSACCIÓN'** para obtener el resultado.")