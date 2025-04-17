import streamlit as st
import pandas as pd
from datetime import datetime
from modulos.conexion_mongo import db

coleccion = db["inventario"]

def cargar_inventario():
    return pd.DataFrame(list(coleccion.find({}, {"_id": 0})))

def guardar_item(item):
    coleccion.insert_one(item)

def actualizar_item(id_item, nuevos_datos):
    coleccion.update_one({"id_item": id_item}, {"$set": nuevos_datos})

def app_inventario():
    st.subheader("📦 Inventario Técnico")
    tabs = st.tabs(["📄 Ver Inventario", "🛠️ Administrar Inventario"])
    df = cargar_inventario()

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
            if not id_item or not descripcion or not unidad:
                st.error("⚠️ Los campos 'ID del ítem', 'Descripción' y 'Unidad' son obligatorios.")
            elif id_item in df["id_item"].values:
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
                guardar_item(nueva_fila)
                st.success("✅ Ítem agregado correctamente.")
                st.experimental_rerun()

        if len(df) > 0:
            st.divider()
            st.markdown("### ✏️ Editar ítem existente")
            item_sel = st.selectbox("Seleccionar ítem por ID", df["id_item"].tolist())
            item_data = df[df["id_item"] == item_sel].iloc[0]

            with st.form("editar_item"):
                descripcion = st.text_input("Descripción", value=item_data["descripcion"])
                cantidad = st.number_input("Cantidad", min_value=0, step=1, value=int(item_data["cantidad"]))
                unidad = st.text_input("Unidad", value=item_data["unidad"])
                ubicacion = st.text_input("Ubicación", value=item_data["ubicacion"])
                destino = st.text_input("Destino", value=item_data["destino"])
                uso_destino = st.selectbox("Uso", ["interno", "externo"], index=0 if item_data["uso_destino"] == "interno" else 1)
                maquina_compatible = st.text_input("Máquina compatible", value=item_data["maquina_compatible"])
                stock_minimo = st.number_input("Stock mínimo", min_value=0, step=1, value=int(item_data["stock_minimo"]))
                proveedor = st.text_input("Proveedor", value=item_data["proveedor"])
                observaciones = st.text_area("Observaciones", value=item_data["observaciones"])
                update = st.form_submit_button("Actualizar")

            if update:
                nuevos_datos = {
                    "descripcion": descripcion,
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
                actualizar_item(item_sel, nuevos_datos)
                st.success("✅ Ítem actualizado correctamente.")
                st.rerun()
