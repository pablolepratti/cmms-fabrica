import streamlit as st
import pandas as pd
import os

DATA_PATH = "data/inventario.csv"

def cargar_inventario():
    if os.path.exists(DATA_PATH):
        return pd.read_csv(DATA_PATH)
    else:
        return pd.DataFrame(columns=["id_item", "nombre", "tipo", "stock", "unidad", "proveedor", "ultima_actualizacion", "destino", "observaciones"])

def mostrar_inventario():
    st.subheader("📦 Inventario Técnico")
    df = cargar_inventario()

    if df.empty:
        st.warning("No hay elementos cargados en el inventario.")
        return

    # Filtro por tipo
    tipo = st.selectbox("Filtrar por tipo", ["Todos", "repuesto", "insumo"])
    if tipo != "Todos":
        df = df[df["tipo"] == tipo]

    # Filtro por destino
    destino = st.selectbox("Filtrar por destino", ["Todos", "fábrica", "servicio externo"])
    if destino != "Todos":
        df = df[df["destino"] == destino]

    st.dataframe(df.sort_values("nombre"), use_container_width=True)

def app_inventario():
    mostrar_inventario()
