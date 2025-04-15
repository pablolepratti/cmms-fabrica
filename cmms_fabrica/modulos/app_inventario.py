import streamlit as st
import pandas as pd
import os
from datetime import datetime

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

def guardar_inventario(df):
    df.to_csv(DATA_PATH, index=False)

def app_inventario():
    st.subheader("📦 Inventario Técnico")

    tabs = st.tabs(["📄 Ver Inventario", "🛠️ Administrar Inventario"])
    df = cargar_inventario()

    # --- TAB 1: VISUALIZACIÓN ---
    with tabs[0]:
        if df.empty:
            st.warning("No hay elementos cargados en el inventario.")
        else:
            tipo = st.selectbox("Filtrar por tipo", ["Todos"] + sorted(df["tipo"].dropna().unique()))
            if tipo != "Todos":
                df = df[df["tipo"] == tipo]

            uso = st.selectbox("Filtrar por uso", ["Todos"] + sorted(df["uso_destino"].dropna().unique()))
            if uso != "Todos":
                df = df[df["uso_destino"] == uso]

            maquina = st.selectbox("Filtrar por máquina compatible", ["Todas"] + sorted(df["maquina_compatible"].dropna().unique()))
            if maquina != "Todas":
                df = df[df["maquina_compatible"] == maquina]

            st.dataframe(df.sort_values("descripcion"), use_container_width=True)

    # --- TAB 2: CRUD ---
    with tabs[1]:
        st.markdown("### ➕ Agregar nuevo ítem")
        with st.form("form_nuevo_item"):
            col1, col2 = st.columns(2)
            with col1:
                id_item = st.text_input("ID del ítem", "")
                descripcion = st.text_input("Descripción")
                tipo = st.selectbox("Tipo", ["repuesto", "insumo"])
                cantidad = st.number_input("Cantidad", min_value=0, step=1)
                unidad = st.text_input("Unidad")
                ubicacion = st.text_input("Ubicación")
            with col2:
                destino = st.text_input("Destino")
                uso_destino = st.selectbox("Uso", ["interno", "externo"])
                maquina_compatible = st.text_input("Máquina compatible")
                stock_minimo = st.number_input("Stock mínimo", min_value=0, step=1)
                proveedor = st.text_input("Proveedor")
                observaciones = st.text_area("Observaciones")

            submitted = st.form_submit_button("Agregar ítem")

        if submitted:
            if id_item in df["id_item"].values:
                st.error("⚠️ Ya existe un ítem con ese ID.")
            else:
                nueva_fila = {
                    "id_item": id_item,
                    "descripcion": descripcion,
                    "tipo": tipo,
                    "cantidad": cantidad,
                    "unidad": unidad,
                    "ubicacion": ubicacion,
                    "destino": destino,
                    "uso_destino": uso_destino,
                    "maquina_compatible": maquina_compatible,
                    "stock_minimo": stock_minimo,
                    "proveedor": proveedor,
                    "ultima_actualizacion": datetime.today().strftime("%Y-%m-%d"),
                    "observaciones": observaciones
                }
                df = pd.concat([df, pd.DataFrame([nueva_fila])], ignore_index=True)
                guardar_inventario(df)
                st.success("✅ Ítem agregado correctamente.")

        if len(df) > 0:
            st.markdown("### ✏️ Editar ítem existente")
            item_sel = st.selectbox("Seleccionar ítem por ID", df["id_item"].tolist())
            item_data = df[df["id_item"] == item_sel].iloc[0]

            with st.form("editar_item"):
                descripcion = st.text_input("Descripción", value=item_data["descripcion"])
                cantidad = st.number_input("Cantidad", min_value=0, step=1, value=int(item_data["cantidad"]))
                unidad = st.text_input("Unidad", value=item_data["unidad"])
                ubicacion = st.text_input("Ubicación", value=item_data["ubicacion"])
                destino = st.text_input("Destino", value=item_data["destino"])
                uso_destino = st.selectbox("Uso", ["interno", "externo"], index=0 if item_data["uso_destino"]=="interno" else 1)
                maquina_compatible = st.text_input("Máquina compatible", value=item_data["maquina_compatible"])
                stock_minimo = st.number_input("Stock mínimo", min_value=0, step=1, value=int(item_data["stock_minimo"]))
                proveedor = st.text_input("Proveedor", value=item_data["proveedor"])
                observaciones = st.text_area("Observaciones", value=item_data["observaciones"])
                update = st.form_submit_button("Actualizar")

            if update:
                df.loc[df["id_item"] == item_sel, "descripcion"] = descripcion
                df.loc[df["id_item"] == item_sel, "cantidad"] = cantidad
                df.loc[df["id_item"] == item_sel, "unidad"] = unidad
                df.loc[df["id_item"] == item_sel, "ubicacion"] = ubicacion
                df.loc[df["id_item"] == item_sel, "destino"] = destino
                df.loc[df["id_item"] == item_sel, "uso_destino"] = uso_destino
                df.loc[df["id_item"] == item_sel, "maquina_compatible"] = maquina_compatible
                df.loc[df["id_item"] == item_sel, "stock_minimo"] = stock_minimo
                df.loc[df["id_item"] == item_sel, "proveedor"] = proveedor
                df.loc[df["id_item"] == item_sel, "observaciones"] = observaciones
                df.loc[df["id_item"] == item_sel, "ultima_actualizacion"] = datetime.today().strftime("%Y-%m-%d")
                guardar_inventario(df)
                st.success("✅ Ítem actualizado correctamente.")
