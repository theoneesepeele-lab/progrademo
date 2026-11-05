import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

# 1. Configuración de pantalla completa
st.set_page_config(
    page_title="Car Sales Control Panel",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 2. CSS Personalizado para Look Pro Dark / Tech
st.markdown(
    """
    <style>
    .stApp {
        background-color: #0E1117;
    }
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #1E232A 0%, #16191E 100%);
        border: 1px solid #2B303A;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    div[data-testid="stMetric"] label {
        color: #8B949E !important;
        font-size: 0.9rem !important;
        font-weight: 600;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #58A6FF !important;
        font-weight: 800;
    }
    h1, h2, h3 {
        color: #F0F6FC !important;
        font-weight: 700;
    }
    section[data-testid="stSidebar"] {
        background-color: #161B22;
        border-right: 1px solid #21262D;
    }
    </style>
""",
    unsafe_allow_html=True,
)


@st.cache_data
def cargar_datos() -> pd.DataFrame:
    df = pd.read_csv("ventas.csv", sep=";", parse_dates=["fecha"])
    df["color"] = df["color"].str.strip().str.capitalize()
    return df


df = cargar_datos()

# Mapeo de colores reales
COLOR_MAP = {
    "Rojo": "#FF4B4B",
    "Azul": "#1F77B4",
    "Negro": "#333333",
    "Blanco": "#E0E0E0",
    "Gris": "#7F7F7F",
    "Verde": "#2CA02C",
    "Amarillo": "#FFD700",
    "Plata": "#C0C0C0",
}

# --- Sidebar ---
with st.sidebar:
    st.title("🏎️ Control Panel")
    st.caption("Filtros de análisis de flota")
    st.divider()

    colores_disponibles = sorted(df["color"].unique())
    anios_disponibles = sorted(df["fecha"].dt.year.unique())

    colores = st.multiselect(
        "🎨 Seleccionar Colores",
        colores_disponibles,
        default=colores_disponibles,
    )
    anios = st.multiselect(
        "📅 Seleccionar Años", anios_disponibles, default=anios_disponibles
    )

# Filtrado de datos
filtrado = df[df["color"].isin(colores) & df["fecha"].dt.year.isin(anios)]

if filtrado.empty:
    st.error("⚠️ Sin datos disponibles para la combinación de filtros actual.")
    st.stop()

# --- HEADER PRINCIPAL ---
st.title("⚡ Telemetría y Análisis de Ventas de Automóviles")
st.caption("Dashboard completo con distribución, tendencias, dispersión y mapa de calor")

st.markdown("##")

# --- MÉTRICAS DE ALTO IMPACTO ---
por_color = filtrado.groupby("color")["unidades"].sum().sort_values(ascending=False)
total_unidades = filtrado["unidades"].sum()
color_top = por_color.idxmax()
unidades_top = por_color.max()
porcentaje_top = (unidades_top / total_unidades) * 100 if total_unidades > 0 else 0

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Total Vendido", f"{total_unidades:,}".replace(",", "."))
with c2:
    st.metric("Color Líder", color_top, delta=f"{unidades_top} un. ({porcentaje_top:.1f}%)")
with c3:
    promedio_mensual = filtrado.groupby(filtrado["fecha"].dt.to_period("M"))["unidades"].sum().mean()
    st.metric("Promedio Mensual", f"{int(promedio_mensual)} un.")
with c4:
    st.metric("Registros Totales", f"{len(filtrado):,}")

st.markdown("##")

# Configuración global de Matplotlib para modo oscuro
plt.style.use("dark_background")

# --- FILA 1: Gráfico 1 (Barras) y Gráfico 2 (Líneas Mensuales) ---
col_barras, col_lineas = st.columns(2)

with col_barras:
    st.subheader("📊 1. Ventas Totales por Color (Barras)")
    fig1, ax1 = plt.subplots(figsize=(7, 4.5))
    fig1.patch.set_facecolor("#0E1117")
    ax1.set_facecolor("#0E1117")

    colores_barras = [COLOR_MAP.get(c, "#58A6FF") for c in por_color.index]
    barras = ax1.bar(por_color.index, por_color.values, color=colores_barras, edgecolor="#30363D", alpha=0.9)

    for barra in barras:
        yval = barra.get_height()
        ax1.text(barra.get_x() + barra.get_width() / 2.0, yval + (max(por_color.values) * 0.02), f"{int(yval)}", ha="center", va="bottom", color="#C9D1D9", fontsize=9, fontweight="bold")

    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    ax1.spines["left"].set_color("#30363D")
    ax1.spines["bottom"].set_color("#30363D")
    ax1.tick_params(colors="#8B949E")
    ax1.grid(axis="y", linestyle=":", alpha=0.2, color="#8B949E")
    st.pyplot(fig1)

with col_lineas:
    st.subheader("📈 2. Evolución Temporal Mensual (Líneas)")
    df_mensual = filtrado.copy()
    df_mensual["mes"] = df_mensual["fecha"].dt.to_period("M").dt.to_timestamp()
    pivot = df_mensual.pivot_table(index="mes", columns="color", values="unidades", aggfunc="sum").fillna(0)

    fig2, ax2 = plt.subplots(figsize=(7, 4.5))
    fig2.patch.set_facecolor("#0E1117")
    ax2.set_facecolor("#0E1117")

    for col in pivot.columns:
        ax2.plot(pivot.index, pivot[col], marker="o", linewidth=2, label=col, color=COLOR_MAP.get(col, None), alpha=0.85)

    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.spines["left"].set_color("#30363D")
    ax2.spines["bottom"].set_color("#30363D")
    ax2.tick_params(colors="#8B949E")
    ax2.grid(True, linestyle=":", alpha=0.2, color="#8B949E")
    ax2.legend(facecolor="#161B22", edgecolor="#30363D", labelcolor="#C9D1D9", loc="upper left", fontsize=8)
    st.pyplot(fig2)

st.markdown("##")

# --- FILA 2: Gráfico 3 (Líneas Diario) y Gráfico 4 (Scatter) ---
col_lineas_diarias, col_scatter = st.columns(2)

with col_lineas_diarias:
    st.subheader("📉 3. Tendencia Diaria Detallada (Líneas)")
    fig3, ax3 = plt.subplots(figsize=(7, 4.5))
    fig3.patch.set_facecolor("#0E1117")
    ax3.set_facecolor("#0E1117")

    diario = filtrado.groupby(["fecha", "color"])["unidades"].sum().unstack().fillna(0)
    for col in diario.columns:
        ax3.plot(diario.index, diario[col], linewidth=1.5, label=col, color=COLOR_MAP.get(col, None), alpha=0.7)

    ax3.spines["top"].set_visible(False)
    ax3.spines["right"].set_visible(False)
    ax3.spines["left"].set_color("#30363D")
    ax3.spines["bottom"].set_color("#30363D")
    ax3.tick_params(colors="#8B949E")
    ax3.grid(True, linestyle=":", alpha=0.2, color="#8B949E")
    ax3.legend(facecolor="#161B22", edgecolor="#30363D", labelcolor="#C9D1D9", fontsize=8)
    st.pyplot(fig3)

with col_scatter:
    st.subheader("🔵 4. Dispersión de Ventas (*Scatter Plot*)")
    fig4, ax4 = plt.subplots(figsize=(7, 4.5))
    fig4.patch.set_facecolor("#0E1117")
    ax4.set_facecolor("#0E1117")

    for color_nombre in filtrado["color"].unique():
        subset = filtrado[filtrado["color"] == color_nombre]
        ax4.scatter(subset["fecha"], subset["unidades"], label=color_nombre, color=COLOR_MAP.get(color_nombre, "#58A6FF"), alpha=0.8, s=50, edgecolors="#ffffff", linewidths=0.5)

    ax4.set_ylabel("Unidades por registro")
    ax4.spines["top"].set_visible(False)
    ax4.spines["right"].set_visible(False)
    ax4.spines["left"].set_color("#30363D")
    ax4.spines["bottom"].set_color("#30363D")
    ax4.tick_params(colors="#8B949E")
    ax4.grid(True, linestyle=":", alpha=0.2, color="#8B949E")
    ax4.legend(facecolor="#161B22", edgecolor="#30363D", labelcolor="#C9D1D9", fontsize=8)
    st.pyplot(fig4)

st.markdown("##")

# --- FILA 3: Gráfico 5 (Mapa de Calor) ---
st.subheader("🔥 5. Mapa de Calor: Ventas por Mes y Color (*Heatmap*)")

fig5, ax5 = plt.subplots(figsize=(10, 4.5))
fig5.patch.set_facecolor("#0E1117")
ax5.set_facecolor("#0E1117")

df_heatmap = filtrado.copy()
df_heatmap["mes_str"] = df_heatmap["fecha"].dt.to_period("M").astype(str)
matriz_calor = df_heatmap.pivot_table(index="color", columns="mes_str", values="unidades", aggfunc="sum").fillna(0)

cax = ax5.imshow(matriz_calor.values, cmap="magma", aspect="auto")

# Etiquetas en los ejes
ax5.set_xticks(np.arange(len(matriz_calor.columns)))
ax5.set_yticks(np.arange(len(matriz_calor.index)))
ax5.set_xticklabels(matriz_calor.columns, rotation=45, color="#8B949E")
ax5.set_yticklabels(matriz_calor.index, color="#8B949E")

ax5.spines["top"].set_visible(False)
ax5.spines["right"].set_visible(False)
ax5.spines["left"].set_color("#3
