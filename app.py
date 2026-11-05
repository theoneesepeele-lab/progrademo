import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

# 1. Configuración de la página (¡siempre primero!)
st.set_page_config(
    page_title="Ventas de autos",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 2. Estilos personalizados (CSS para métricas y contenedores limpios)
st.markdown(
    """
    <style>
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border: 1px solid #f0f2f6;
    }
    </style>
""",
    unsafe_allow_html=True,
)

st.title("🚗 Ventas de autos por color")
st.caption("Panel interactivo de análisis de ventas y tendencias")


@st.cache_data
def cargar_datos() -> pd.DataFrame:
    return pd.read_csv("ventas.csv", sep=";", parse_dates=["fecha"])


df = cargar_datos()

# --- Filtros en la barra lateral ---
with st.sidebar:
    st.header("⚙️ Filtros")

    colores_disponibles = sorted(df["color"].unique())
    anios_disponibles = sorted(df["fecha"].dt.year.unique())

    colores = st.multiselect(
        "Colores", colores_disponibles, default=colores_disponibles
    )
    anios = st.multiselect("Años", anios_disponibles, default=anios_disponibles)

    st.divider()
    st.caption("Creado con Streamlit & Matplotlib")

filtrado = df[df["color"].isin(colores) & df["fecha"].dt.year.isin(anios)]

if filtrado.empty:
    st.warning(
        "⚠️ No hay datos para los filtros seleccionados. Selecciona al menos un color y un año."
    )
    st.stop()

# --- Métricas principales en columnas ---
st.markdown("### 📊 Indicadores Clave")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(
        label="Total de autos vendidos",
        value=f"{filtrado['unidades'].sum():,}".replace(",", "."),
    )
with col2:
    color_top = filtrado.groupby("color")["unidades"].sum().idxmax()
    st.metric(label="Color más vendido", value=color_top)
with col3:
    st.metric(
        label="Registros filtrados",
        value=f"{len(filtrado):,}".replace(",", "."),
    )

st.markdown("###")  # Espaciador visual

# --- Gráficos en dos columnas ---
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📈 Ventas totales por color")
    por_color = filtrado.groupby("color")["unidades"].sum().sort_values(ascending=False)

    fig1, ax1 = plt.subplots(figsize=(7, 4.5))
    barras = ax1.bar(
        por_color.index, por_color.values, color="#2E86C1", width=0.6, alpha=0.9
    )

    # Estética limpia de Matplotlib
    ax1.set_ylabel("Unidades vendidas", fontsize=10)
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    ax1.grid(axis="y", linestyle="--", alpha=0.3)
    plt.xticks(rotation=20)

    st.pyplot(fig1)

with col_right:
    st.subheader("📅 Evolución temporal mensual")

    # Agrupamos por mes para evitar líneas demasiado saturadas por día
    df_mensual = filtrado.copy()
    df_mensual["mes"] = df_mensual["fecha"].dt.to_period("M").dt.to_timestamp()
    pivot = df_mensual.pivot_table(
        index="mes", columns="color", values="unidades", aggfunc="sum"
    ).fillna(0)

    fig2, ax2 = plt.subplots(figsize=(7, 4.5))
    pivot.plot(ax=ax2, marker="o", linewidth=2, alpha=0.85)

    ax2.set_ylabel("Unidades vendidas", fontsize=10)
    ax2.set_xlabel("")
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.grid(True, linestyle="--", alpha=0.3)
    ax2.legend(title="Color", frameon=True, facecolor="#ffffff", edgecolor="none")

    st.pyplot(fig2)

st.divider()

# --- Tabla de datos ---
with st.expander("🔍 Ver tabla de datos detallada"):
    st.dataframe(filtrado, use_container_width=True)
