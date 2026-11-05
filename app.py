import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Ventas de autos", page_icon="🚗")
st.title("🚗 Ventas de autos por color")


@st.cache_data
def cargar_datos() -> pd.DataFrame:
    return pd.read_csv("ventas.csv", sep=";", parse_dates=["fecha"])


df = cargar_datos()

# --- Filtros en la barra lateral ---
st.sidebar.header("Filtros")
colores = st.sidebar.multiselect(
    "Colores", sorted(df["color"].unique()), default=sorted(df["color"].unique())
)
anios = st.sidebar.multiselect(
    "Años", sorted(df["fecha"].dt.year.unique()), default=sorted(df["fecha"].dt.year.unique())
)

filtrado = df[df["color"].isin(colores) & df["fecha"].dt.year.isin(anios)]

if filtrado.empty:
    st.warning("Selecciona al menos un color y un año.")
    st.stop()

# --- Métricas ---
col1, col2 = st.columns(2)
col1.metric("Total de autos vendidos", f"{filtrado['unidades'].sum():,}")
col2.metric(
    "Color más vendido", filtrado.groupby("color")["unidades"].sum().idxmax()
)

# --- Gráfico 1: ventas por color ---
st.subheader("Ventas totales por color")
por_color = filtrado.groupby("color")["unidades"].sum().sort_values(ascending=False)
fig1, ax1 = plt.subplots()
ax1.bar(por_color.index, por_color.values, color="steelblue")
ax1.set_ylabel("Unidades")
st.pyplot(fig1)

# --- Gráfico 2: evolución mensual ---
st.subheader("Evolución mensual")
pivot = filtrado.pivot_table(index="fecha", columns="color", values="unidades", aggfunc="sum")
fig2, ax2 = plt.subplots()
pivot.plot(ax=ax2, marker="o")
ax2.set_ylabel("Unidades")
ax2.set_xlabel("")
st.pyplot(fig2)

# --- Tabla de datos ---
with st.expander("Ver datos"):
    st.dataframe(filtrado)
