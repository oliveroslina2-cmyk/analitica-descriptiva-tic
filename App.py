import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as bg

# ---------------------------------------------------------
# CONFIGURACIÓN DE LA PÁGINA
# ---------------------------------------------------------
st.set_page_config(
    page_title="Dashboard Analítica Descriptiva",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo visual personalizado
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# CARGA Y PREPROCESAMIENTO DE DATOS
# ---------------------------------------------------------
@st.cache_data
def cargar_datos():
    # Intenta cargar el archivo Excel predeterminado
    try:
        df = pd.read_excel("datos.xlsx")
    except Exception:
        # En caso de no encontrarlo localmente, permite subirlo desde la barra lateral
        st.sidebar.warning("No se encontró 'datos.xlsx' en la raíz. Por favor sube tu archivo.")
        uploaded_file = st.sidebar.file_uploader("Subir archivo Excel", type=["xlsx", "xls"])
        if uploaded_file is not None:
            df = pd.read_excel(uploaded_file)
        else:
            return None

    # Estandarizar nombres de columnas a minúsculas/sin espacios si es necesario
    df.columns = df.columns.str.strip()
    
    # Asegurar formato de fecha si existe columna de fecha
    col_fecha = [c for c in df.columns if 'fecha' in c.lower() or 'date' in c.lower()]
    if col_fecha:
        df[col_fecha[0]] = pd.to_datetime(df[col_fecha[0]])
        
    return df

df_raw = cargar_datos()

if df_raw is None:
    st.info("👋 Por favor, asegúrate de colocar el archivo `datos.xlsx` en la misma carpeta o subirlo desde la barra lateral.")
    st.stop()

# ---------------------------------------------------------
# FILTROS DE BARRA LATERAL (INTERACTIVIDAD)
# ---------------------------------------------------------
st.sidebar.header("🔍 Filtros de Navegación")

df_filtered = df_raw.copy()

# Filtro por Región si existe
cols_region = [c for c in df_filtered.columns if 'region' in c.lower() or 'región' in c.lower()]
if cols_region:
    regiones = ["Todas"] + list(df_filtered[cols_region[0]].dropna().unique())
    region_sel = st.sidebar.selectbox("Seleccionar Región:", regiones)
    if region_sel != "Todas":
        df_filtered = df_filtered[df_filtered[cols_region[0]] == region_sel]

# Filtro por Categoría si existe
cols_cat = [c for c in df_filtered.columns if 'categoria' in c.lower() or 'categoría' in c.lower()]
if cols_cat:
    categorias = ["Todas"] + list(df_filtered[cols_cat[0]].dropna().unique())
    cat_sel = st.sidebar.selectbox("Seleccionar Categoría:", categorias)
    if cat_sel != "Todas":
        df_filtered = df_filtered[df_filtered[cols_cat[0]] == cat_sel]

# ---------------------------------------------------------
# ENCABEZADO Y RESUMEN EJECUTIVO
# ---------------------------------------------------------
st.title("📈 Proyecto Final - Analítica Descriptiva con IA")
st.caption("Uso Gerencial de TIC - Diagnóstico e Inteligencia de Negocio")
st.markdown("---")

# Identificación automática de columnas numéricas clave
col_ventas = next((c for c in df_filtered.columns if 'venta' in c.lower() or 'sales' in c.lower()), None)
col_utilidad = next((c for c in df_filtered.columns if 'utilidad' in c.lower() or 'profit' in c.lower() or 'ganancia' in c.lower()), None)
col_margen = next((c for c in df_filtered.columns if 'margen' in c.lower() or 'margin' in c.lower()), None)

# Cálculo automático de Margen % si no existe directamente
if col_ventas and col_utilidad and not col_margen:
    df_filtered['Margen_%'] = (df_filtered[col_utilidad] / df_filtered[col_ventas]) * 100
    col_margen = 'Margen_%'

st.subheader("💡 Ventana de Resumen Ejecutivo (KPIs)")
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

total_ventas = df_filtered[col_ventas].sum() if col_ventas else 0
total_utilidad = df_filtered[col_utilidad].sum() if col_utilidad else 0
margen_prom = df_filtered[col_margen].mean() if col_margen else 0
total_pedidos = len(df_filtered)

kpi1.metric("Ventas Totales", f"${total_ventas:,.2f}")
kpi2.metric("Utilidad Total", f"${total_utilidad:,.2f}")
kpi3.metric("Margen Promedio", f"{margen_prom:.2f}%")
kpi4.metric("Total Registro / Pedidos", f"{total_pedidos:,}")

st.markdown("---")

# ---------------------------------------------------------
# ESTRUCTURA DE LOS 10 PUNTOS GERENCIALES
#