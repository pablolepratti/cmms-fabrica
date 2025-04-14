import streamlit as st
import pandas as pd
import os

DATA_PATH = "data/inventario.csv"

def cargar_inventario():
    columnas = [
        "id_item", "descripcion", "tipo", "cantidad", "unidad", "ubicacion",
        "destino", "uso_destino", "maquina_compatible", "stock_minimo",
        "proveedor", "ultima_actualizacion", "observaciones"
    ]
    if os.path.exists(DATA_PATH):
        return pd.read_csv(DATA_PATH)
    else:
        return pd.DataFrame(columns=columnas)

def mostrar_inventario():
    st.subheader("📦 Inventario Técnico")
    df = cargar_inventario()

    if df.empty:
        st.warning("No hay elementos cargados en el inventario.")
        return

    # Filtro por tipo
    tipo = st.selectbox("Filtrar por tipo", ["Todos"] + sorted(df["tipo"].dropna().unique()))
    if tipo != "Todos":
        df = df[df["tipo"] == tipo]

    # Filtro por uso_destino
    uso = st.selectbox("Filtrar por uso", ["Todos"] + sorted(df["uso_destino"].dropna().unique()))
    if uso != "Todos":
        df = df[df["uso_destino"] == uso]

    # Filtro por maquina compatible
    maquina = st.selectbox("Filtrar por máquina compatible", ["Todas"] + sorted(df["maquina_compatible"].dropna().unique()))
    if maquina != "Todas":
        df = df[df["maquina_compatible"] == maquina]

    st.dataframe(df.sort_values("descripcion"), use_container_width=True)

def app_inventario():
    mostrar_inventario()
