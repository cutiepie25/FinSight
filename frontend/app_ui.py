"""
Interfaz de usuario con Streamlit para FinSight.
Incluye inputs, visualización de tabla, gráficos y exportación.
"""

import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
from datetime import datetime, date
import matplotlib.pyplot as plt
import io

# Configuración de la página
st.set_page_config(
    page_title="FinSight - Tabla de Amortización",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# URL del backend
BACKEND_URL = "http://localhost:8000"

# Estilos CSS personalizados
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #555;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    </style>
""", unsafe_allow_html=True)

# Título principal
st.markdown('<div class="main-header">💰 FinSight</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Sistema de Amortización con Método Francés</div>', unsafe_allow_html=True)

# Inicializar estado de sesión
if 'tabla_actual' not in st.session_state:
    st.session_state.tabla_actual = None
if 'resumen_actual' not in st.session_state:
    st.session_state.resumen_actual = None
if 'parametros_actuales' not in st.session_state:
    st.session_state.parametros_actuales = None
if 'ahorro_actual' not in st.session_state:
    st.session_state.ahorro_actual = None
if 'necesita_recalcular' not in st.session_state:
    st.session_state.necesita_recalcular = False


def verificar_backend():
    """Verifica que el backend esté disponible."""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=2)
        return response.status_code == 200
    except:
        return False


def formatear_moneda(valor):
    """Formatea un valor como moneda."""
    return f"${valor:,.2f}"


# Sidebar con inputs
with st.sidebar:
    st.header("📋 Parámetros del Crédito")
    
    # Verificar conexión con backend
    if not verificar_backend():
        st.error("⚠️ Backend no disponible. Inicie el servidor con: `uvicorn backend.main:app --reload`")
    else:
        st.success("✅ Backend conectado")
    
    st.markdown("---")
    
    # Parámetros básicos
    monto = st.number_input(
        "Monto del Préstamo ($)",
        min_value=1000.0,
        max_value=1000000000.0,
        value=100000.0,
        step=1000.0,
        help="Monto total del préstamo"
    )
    
    tasa = st.number_input(
        "Tasa de Interés (%)",
        min_value=0.01,
        max_value=100.0,
        value=12.0,
        step=0.1,
        help="Tasa de interés anual"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        tipo_tasa = st.selectbox(
            "Tipo de Tasa",
            ["efectiva", "nominal"],
            help="Tipo de tasa de interés"
        )
    
    with col2:
        tipo_pago = st.selectbox(
            "Tipo de Pago",
            ["vencida", "anticipada"],
            help="Modalidad de pago"
        )
    
    # Frecuencia de la tasa (ANTES del plazo, según requerimiento)
    if tipo_tasa == "nominal":
        # Mapeo de etiquetas a valores internos
        opciones_nominal = {
            "Año mes": "mensual",
            "Año bimestre": "bimestral",
            "Año trimestre": "trimestral",
            "Año cuatrimestre": "cuatrimestral",
            "Año semestre": "semestral"
        }
        
        frecuencia_label = st.selectbox(
            "Frecuencia de la Tasa Nominal",
            list(opciones_nominal.keys()),
            help="Frecuencia de capitalización de la tasa nominal"
        )
        frecuencia_tasa = opciones_nominal[frecuencia_label]
    else:
        frecuencia_tasa = st.selectbox(
            "Frecuencia de la Tasa Efectiva",
            ["anual", "mensual", "trimestral", "semestral"],
            help="Frecuencia de la tasa efectiva"
        )
    
    plazo_meses = st.number_input(
        "Plazo (meses)",
        min_value=1,
        max_value=600,
        value=12,
        step=1,
        help="Plazo total en meses"
    )
    
    frecuencia_pago = st.selectbox(
        "Frecuencia de Pago",
        ["mensual", "quincenal", "trimestral", "semestral", "anual"],
        help="Frecuencia de los pagos"
    )
    
    fecha_inicio = st.date_input(
        "Fecha de Inicio",
        value=date.today(),
        help="Fecha de inicio del crédito"
    )
    
    st.markdown("---")
    
    # Sección de abonos
    st.header("💵 Abonos Extraordinarios")
    
    tipo_abono = st.radio(
        "Tipo de Abono",
        ["Sin abonos", "Abonos programados", "Abonos específicos"],
        help="Seleccione el tipo de abonos a aplicar"
    )
    
    abonos_data = []
    frecuencia_abono = None
    monto_abono_programado = 0
    
    if tipo_abono == "Abonos programados":
        frecuencia_abono = st.selectbox(
            "Frecuencia del Abono",
            ["trimestral", "semestral", "anual", "mensual"],
            help="Cada cuánto se hace el abono"
        )
        
        monto_abono_programado = st.number_input(
            "Monto del Abono ($)",
            min_value=0.0,
            max_value=float(monto),
            value=1000.0,
            step=100.0,
            help="Monto del abono extraordinario"
        )
    
    elif tipo_abono == "Abonos específicos":
        st.subheader("Agregar Abonos Específicos")
        
        # Inicializar lista de abonos en session_state si no existe
        if 'abonos_especificos' not in st.session_state:
            st.session_state.abonos_especificos = []
        
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            periodo_abono = st.number_input(
                "Periodo del Abono",
                min_value=1,
                max_value=int(plazo_meses / (1 if frecuencia_pago == "mensual" else 
                                            0.5 if frecuencia_pago == "quincenal" else
                                            3 if frecuencia_pago == "trimestral" else
                                            6 if frecuencia_pago == "semestral" else 12)),
                value=1,
                step=1,
                help="Periodo en el que se hará el abono"
            )
        
        with col2:
            monto_abono_especifico = st.number_input(
                "Monto del Abono ($)",
                min_value=0.0,
                max_value=float(monto),
                value=1000.0,
                step=100.0,
                help="Monto del abono extraordinario"
            )
        
        with col3:
            st.write("")
            st.write("")
            if st.button("➕ Agregar", use_container_width=True):
                # Verificar que no exista ya un abono en ese periodo
                periodos_existentes = [a['periodo'] for a in st.session_state.abonos_especificos]
                if periodo_abono in periodos_existentes:
                    st.error(f"Ya existe un abono en el periodo {periodo_abono}")
                else:
                    st.session_state.abonos_especificos.append({
                        'periodo': periodo_abono,
                        'monto': monto_abono_especifico
                    })
                    st.success(f"Abono agregado: Periodo {periodo_abono} - ${monto_abono_especifico:,.2f}")
                    
                    # Recalcular automáticamente si ya existe una tabla calculada
                    if st.session_state.tabla_actual is not None and st.session_state.parametros_actuales is not None:
                        st.session_state.necesita_recalcular = True
                        st.rerun()
        
        # Mostrar lista de abonos agregados
        if st.session_state.abonos_especificos:
            st.write("**Abonos Agregados:**")
            abonos_df = pd.DataFrame(st.session_state.abonos_especificos)
            abonos_df = abonos_df.sort_values('periodo')
            abonos_df['monto'] = abonos_df['monto'].apply(lambda x: f"${x:,.2f}")
            st.dataframe(abonos_df, use_container_width=True, hide_index=True)
            
            if st.button("🗑️ Limpiar Todos los Abonos", type="secondary"):
                st.session_state.abonos_especificos = []
                # Recalcular automáticamente si ya existe una tabla calculada
                if st.session_state.tabla_actual is not None and st.session_state.parametros_actuales is not None:
                    st.session_state.necesita_recalcular = True
                st.rerun()
        else:
            st.info("No hay abonos agregados. Use el formulario arriba para agregar abonos.")
    
    if tipo_abono != "Sin abonos":
        opcion_recalculo = st.radio(
            "Opción de Recálculo",
            ["reducir_cuota", "reducir_plazo"],
            format_func=lambda x: "Reducir Cuota" if x == "reducir_cuota" else "Reducir Plazo",
            help="Cómo aplicar los abonos"
        )
    else:
        opcion_recalculo = "reducir_cuota"
    
    st.markdown("---")
    
    # Botón de cálculo
    calcular_btn = st.button("🔢 Calcular Amortización", type="primary", use_container_width=True)


# Área principal
# Ejecutar cálculo si se presionó el botón O si necesita recalcular automáticamente
if calcular_btn or st.session_state.necesita_recalcular:
    # Resetear bandera de recálculo
    if st.session_state.necesita_recalcular:
        st.session_state.necesita_recalcular = False
    
    with st.spinner("Calculando tabla de amortización..."):
        try:
            # Preparar parámetros
            parametros = {
                "monto": monto,
                "tasa": tasa,
                "tipo_tasa": tipo_tasa,
                "tipo_pago": tipo_pago,
                "plazo_meses": plazo_meses,
                "frecuencia_pago": frecuencia_pago,
                "fecha_inicio": fecha_inicio.strftime("%Y-%m-%d"),
                "frecuencia_tasa": frecuencia_tasa
            }
            
            # Guardar parámetros
            st.session_state.parametros_actuales = parametros
            
            # Llamar al backend según tipo de abono
            if tipo_abono == "Sin abonos":
                response = requests.post(f"{BACKEND_URL}/calcular", json=parametros)
            
            elif tipo_abono == "Abonos programados":
                payload = {
                    "parametros_credito": parametros,
                    "frecuencia_abono": frecuencia_abono,
                    "monto_abono": monto_abono_programado,
                    "opcion_recalculo": opcion_recalculo
                }
                response = requests.post(f"{BACKEND_URL}/calcular-con-abonos-programados", json=payload)
            
            else:  # Abonos específicos
                if st.session_state.abonos_especificos:
                    # Convertir abonos a formato esperado por el backend
                    abonos_list = [
                        {"periodo": a["periodo"], "monto": a["monto"]} 
                        for a in st.session_state.abonos_especificos
                    ]
                    payload = {
                        "parametros_credito": parametros,
                        "abonos": abonos_list,
                        "opcion_recalculo": opcion_recalculo
                    }
                    response = requests.post(f"{BACKEND_URL}/calcular-con-abonos", json=payload)
                else:
                    # Si no hay abonos específicos, calcular tabla normal
                    response = requests.post(f"{BACKEND_URL}/calcular", json=parametros)
            
            if response.status_code == 200:
                data = response.json()
                st.session_state.tabla_actual = pd.DataFrame(data["tabla"])
                st.session_state.resumen_actual = data["resumen"]
                
                # Guardar tasas efectivas si están disponibles
                if "tasa_efectiva_anual" in data:
                    st.session_state.tasa_efectiva_anual = data["tasa_efectiva_anual"]
                    st.session_state.tasa_efectiva_periodo = data["tasa_efectiva_periodo"]
                else:
                    st.session_state.tasa_efectiva_anual = None
                    st.session_state.tasa_efectiva_periodo = None
                
                if "ahorro" in data:
                    st.session_state.ahorro_actual = data["ahorro"]
                else:
                    st.session_state.ahorro_actual = None
                
                st.success("✅ Tabla calculada exitosamente")
            else:
                st.error(f"Error: {response.json().get('detail', 'Error desconocido')}")
        
        except Exception as e:
            st.error(f"Error al conectar con el backend: {str(e)}")


# Mostrar resultados si existen
if st.session_state.tabla_actual is not None:
    
    # Mostrar tasas efectivas convertidas (antes de la tabla)
    if hasattr(st.session_state, 'tasa_efectiva_anual') and st.session_state.tasa_efectiva_anual is not None:
        st.markdown("---")
        st.subheader("📊 Tasas Efectivas Calculadas")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"""
            **Tasa Efectiva Anual:** {st.session_state.tasa_efectiva_anual:.4f}%
            
            Esta es la tasa efectiva anual después de convertir desde la tasa {st.session_state.parametros_actuales['tipo_tasa']} 
            y ajustar por el tipo de pago {st.session_state.parametros_actuales['tipo_pago']}.
            """)
        
        with col2:
            st.info(f"""
            **Tasa Efectiva por Periodo ({st.session_state.parametros_actuales['frecuencia_pago']}):** {st.session_state.tasa_efectiva_periodo:.4f}%
            
            Esta es la tasa que se aplica en cada periodo de pago para calcular los intereses.
            """)
        
        st.markdown("---")
    
    # Tabs para organizar la información
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Resumen", "📋 Tabla Completa", "📈 Gráficos", "💾 Exportar"])
    
    with tab1:
        st.header("Resumen del Crédito")
        
        resumen = st.session_state.resumen_actual
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Monto Inicial",
                formatear_moneda(resumen["monto_inicial"]),
                help="Monto del préstamo"
            )
        
        with col2:
            st.metric(
                "Total Intereses",
                formatear_moneda(resumen["total_intereses"]),
                help="Total de intereses a pagar"
            )
        
        with col3:
            st.metric(
                "Total Pagado",
                formatear_moneda(resumen["total_pagado"]),
                help="Total a pagar (capital + intereses + abonos)"
            )
        
        with col4:
            st.metric(
                "Número de Cuotas",
                resumen["numero_cuotas"],
                help="Cantidad de pagos"
            )
        
        st.markdown("---")
        
        col5, col6, col7 = st.columns(3)
        
        with col5:
            st.metric(
                "Cuota Promedio",
                formatear_moneda(resumen["cuota_promedio"]),
                help="Promedio de las cuotas"
            )
        
        with col6:
            st.metric(
                "Abonos Extra",
                formatear_moneda(resumen["total_abonos_extra"]),
                help="Total de abonos extraordinarios"
            )
        
        with col7:
            st.metric(
                "Saldo Final",
                formatear_moneda(resumen["saldo_final"]),
                delta="Completado" if resumen["saldo_final"] < 0.01 else None,
                help="Saldo pendiente al final"
            )
        
        # Mostrar ahorro si existe
        if st.session_state.ahorro_actual:
            st.markdown("---")
            st.subheader("💰 Ahorro por Abonos Extraordinarios")
            
            ahorro = st.session_state.ahorro_actual
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Ahorro en Intereses",
                    formatear_moneda(ahorro["ahorro_intereses"]),
                    help="Intereses ahorrados por los abonos"
                )
            
            with col2:
                st.metric(
                    "Reducción de Plazo",
                    f"{ahorro['reduccion_plazo_periodos']} periodos",
                    help="Periodos reducidos"
                )
            
            with col3:
                porcentaje_ahorro = (ahorro["ahorro_intereses"] / ahorro["total_intereses_sin_abonos"] * 100) if ahorro["total_intereses_sin_abonos"] > 0 else 0
                st.metric(
                    "% Ahorro",
                    f"{porcentaje_ahorro:.2f}%",
                    help="Porcentaje de ahorro en intereses"
                )
    
    with tab2:
        st.header("Tabla de Amortización Completa")
        
        # Formatear tabla para visualización
        tabla_display = st.session_state.tabla_actual.copy()
        
        # Aplicar formato de moneda a columnas numéricas
        columnas_moneda = ["Cuota", "Interes", "Abono_Capital", "Abono_Extra", "Saldo"]
        for col in columnas_moneda:
            if col in tabla_display.columns:
                tabla_display[col] = tabla_display[col].apply(lambda x: formatear_moneda(x))
        
        # Renombrar columnas para mejor presentación
        tabla_display = tabla_display.rename(columns={
            "Periodo": "Periodo",
            "Fecha": "Fecha",
            "Cuota": "Cuota",
            "Interes": "Interés",
            "Abono_Capital": "Abono Capital",
            "Abono_Extra": "Abono Extra",
            "Saldo": "Saldo"
        })
        
        st.dataframe(
            tabla_display,
            use_container_width=True,
            height=500
        )
        
    
    with tab3:
        st.header("Visualizaciones")
        
        tabla = st.session_state.tabla_actual
        
        # Gráfico 1: Composición de la cuota (Interés vs Capital)
        #st.subheader("📊 Composición de la Cuota")

        tabla = st.session_state.tabla_actual

        # Crear figura y ejes
        fig, ax1 = plt.subplots(figsize=(12, 6))

        # Barras apiladas: interés y abono capital
        ax1.bar(tabla["Periodo"], tabla["Interes"], bottom=tabla["Abono_Capital"],
                color="#FF9800", width=0.6, label="Interés")
        ax1.bar(tabla["Periodo"], tabla["Abono_Capital"],
                color="#4CAF50", width=0.6, label="Abono al Capital")

        # Eje secundario: saldo pendiente
        ax2 = ax1.twinx()
        ax2.plot(tabla["Periodo"], tabla["Saldo"],
                color="black", linewidth=2.5, label="Saldo Pendiente")

        # Etiquetas y títulos
        ax1.set_xlabel("Período")
        ax1.set_ylabel("Cuota ($)")
        ax2.set_ylabel("Saldo Pendiente ($)")
        fig.suptitle("Amortización con Abonos Trimestrales y Recalculo de Cuota", fontsize=14)

        # Cuadrícula
        ax1.grid(True, linestyle="--", alpha=0.4)

        # Combinar leyendas
        handles1, labels1 = ax1.get_legend_handles_labels()
        handles2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(handles1 + handles2, labels1 + labels2, loc="upper right")

        plt.tight_layout()

        # Mostrar en Streamlit
        st.pyplot(fig)
                
        # Gráfico 3: Distribución de pagos
        st.subheader("🥧 Distribución de Pagos")
        
        total_capital = tabla["Abono_Capital"].sum()
        total_interes = tabla["Interes"].sum()
        total_abono_extra = tabla["Abono_Extra"].sum()
        
        labels = ["Capital", "Intereses"]
        values = [total_capital, total_interes]
        colors = ["#4CAF50", "#FF9800"]
        
        if total_abono_extra > 0:
            labels.append("Abonos Extra")
            values.append(total_abono_extra)
            colors.append("#2196F3")
        
        fig3 = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            marker=dict(colors=colors),
            hole=0.3
        )])
        
        fig3.update_layout(height=400)
        
        st.plotly_chart(fig3, use_container_width=True)
    
    with tab4:
        st.header("Exportar Datos")
        
        st.write("Descargue la tabla de amortización en diferentes formatos:")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Exportar a CSV
            csv = st.session_state.tabla_actual.to_csv(index=False).encode('utf-8')
            
            st.download_button(
                label="📄 Descargar CSV",
                data=csv,
                file_name=f"amortizacion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col2:
            # Exportar a Excel
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                st.session_state.tabla_actual.to_excel(writer, sheet_name='Amortización', index=False)
            
            excel_data = buffer.getvalue()
            
            st.download_button(
                label="📊 Descargar Excel",
                data=excel_data,
                file_name=f"amortizacion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        
        st.markdown("---")
        
        # Mostrar resumen en formato texto
        st.subheader("📋 Resumen en Texto")
        
        resumen_texto = f"""
        **RESUMEN DEL CRÉDITO**
        
        Monto Inicial: {formatear_moneda(resumen["monto_inicial"])}
        Tasa de Interés: {tasa}% {tipo_tasa} {tipo_pago}
        Plazo: {plazo_meses} meses
        Frecuencia de Pago: {frecuencia_pago}
        
        **RESULTADOS**
        
        Total Intereses: {formatear_moneda(resumen["total_intereses"])}
        Total Abonos Extra: {formatear_moneda(resumen["total_abonos_extra"])}
        Total Pagado: {formatear_moneda(resumen["total_pagado"])}
        Número de Cuotas: {resumen["numero_cuotas"]}
        Cuota Promedio: {formatear_moneda(resumen["cuota_promedio"])}
        Saldo Final: {formatear_moneda(resumen["saldo_final"])}
        """
        
        if st.session_state.ahorro_actual:
            ahorro = st.session_state.ahorro_actual
            resumen_texto += f"""
        
        **AHORRO POR ABONOS**
        
        Ahorro en Intereses: {formatear_moneda(ahorro["ahorro_intereses"])}
        Reducción de Plazo: {ahorro["reduccion_plazo_periodos"]} periodos
            """
        
        st.text_area("Resumen", resumen_texto, height=400)

else:
    # Mensaje inicial
    st.info("👈 Configure los parámetros del crédito en el panel lateral y presione 'Calcular Amortización'")
    
    # Información adicional
    with st.expander("ℹ️ Información sobre el Sistema"):
        st.markdown("""
        ### FinSight - Sistema de Amortización
        
        Este sistema calcula tablas de amortización usando el **Método Francés** (cuota constante).
        
        **Características:**
        - ✅ Conversión automática de tasas (nominal/efectiva, anticipada/vencida)
        - ✅ Múltiples frecuencias de pago
        - ✅ Abonos extraordinarios programados o específicos
        - ✅ Opciones de recálculo (reducir cuota o reducir plazo)
        - ✅ Visualizaciones interactivas
        - ✅ Exportación a CSV y Excel
        
        **Fórmulas Utilizadas:**
        
        1. **Cuota Francés**: `C = P * [r * (1 + r)^n] / [(1 + r)^n - 1]`
        2. **Nominal → Efectiva**: `ie = (1 + in/m)^m - 1`
        3. **Anticipada → Vencida**: `iv = ia / (1 + ia)`
        4. **Equivalente frecuencia**: `ieq = (1 + i)^(frec_pago/365) - 1`
        
        **Supuestos:**
        - Año comercial de 360 días
        - Redondeo a 2 decimales
        - Saldo final ≤ 0.01
        """)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #888;'>FinSight v1.0 - Sistema de Amortización Financiera</div>",
    unsafe_allow_html=True
)
