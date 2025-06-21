"""
📦 CRUD de Inventario Técnico – CMMS Fábrica

Gestiona ítems del inventario técnico asociados a repuestos e insumos.
Registra todas las altas, ediciones y bajas en la colección ``historial``
para mantener la trazabilidad de acuerdo con ISO 9001 e ISO 55001.
"""

import pandas as pd
import streamlit as st
from datetime import datetime
from modulos.conexion_mongo import db
from crud.generador_historial import registrar_evento_historial

coleccion = db["inventario"]


def form_item(defaults=None, key: str = "form_inventario"):
    """Formulario para cargar o editar un ítem del inventario.

    Parameters
    ----------
    defaults : dict, optional
        Valores por defecto para editar un ítem existente.
    key : str, default "form_inventario"
        Identificador único del formulario en la interfaz.
    """
    with st.form(key):
        col1, col2 = st.columns(2)
        with col1:
            id_item = st.text_input("ID del ítem", value=defaults.get("id_item") if defaults else "")
            descripcion = st.text_input("Descripción", value=defaults.get("descripcion") if defaults else "")
            tipo = st.selectbox(
                "Tipo",
                ["repuesto", "insumo"],
                index=["repuesto", "insumo"].index(defaults.get("tipo")) if defaults and defaults.get("tipo") in ["repuesto", "insumo"] else 0,
            )
            cantidad = st.number_input(
                "Cantidad",
                min_value=0,
                step=1,
                value=int(defaults.get("cantidad", 0)) if defaults else 0,
            )
            unidad = st.text_input("Unidad", value=defaults.get("unidad") if defaults else "")
            ubicacion = st.text_input("Ubicación", value=defaults.get("ubicacion") if defaults else "")
        with col2:
            destino = st.text_input("Destino", value=defaults.get("destino") if defaults else "")
            uso_destino = st.selectbox(
                "Uso",
                ["interno", "externo"],
                index=0 if not defaults or defaults.get("uso_destino") != "externo" else 1,
            )
            maquina_compatible = st.text_input(
                "Máquina compatible (ID Activo Técnico)",
                value=defaults.get("maquina_compatible") if defaults else "",
            )
            stock_minimo = st.number_input(
                "Stock mínimo",
                min_value=0,
                step=1,
                value=int(defaults.get("stock_minimo", 0)) if defaults else 0,
            )
            proveedor = st.text_input("Proveedor", value=defaults.get("proveedor") if defaults else "")
            observaciones = st.text_area("Observaciones", value=defaults.get("observaciones") if defaults else "")
        submitted = st.form_submit_button("Guardar")

    if submitted:
        if not id_item or not descripcion or not unidad:
            st.error("⚠️ Los campos 'ID del ítem', 'Descripción' y 'Unidad' son obligatorios.")
            return None
        data = {
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
            "observaciones": observaciones,
            "ultima_actualizacion": datetime.today().strftime("%Y-%m-%d"),
        }
        return data
    return None


def visualizar_inventario():
    """Muestra el inventario con filtros básicos."""
    datos = list(coleccion.find({}, {"_id": 0}))
    if not datos:
        st.info("No hay ítems cargados en el inventario.")
        return

    df = pd.DataFrame(datos)
    tipo = st.selectbox("Filtrar por tipo", ["Todos"] + sorted(df["tipo"].dropna().unique()))
    if tipo != "Todos":
        df = df[df["tipo"] == tipo]

    uso = st.selectbox("Filtrar por uso", ["Todos"] + sorted(df["uso_destino"].dropna().unique()))
    if uso != "Todos":
        df = df[df["uso_destino"] == uso]

    maquina = st.selectbox(
        "Filtrar por máquina compatible",
        ["Todas"] + sorted(df["maquina_compatible"].dropna().unique()),
    )
    if maquina != "Todas":
        df = df[df["maquina_compatible"] == maquina]

    st.dataframe(df.sort_values("descripcion"), use_container_width=True)


def app_inventario(usuario: str) -> None:
    """Interfaz principal para gestionar el inventario técnico."""
    st.title("📦 Inventario Técnico")
    pestañas = st.tabs(["📄 Ver Inventario", "🛠️ Administrar Inventario"])

    with pestañas[0]:
        visualizar_inventario()

    with pestañas[1]:
        st.markdown("### ➕ Agregar nuevo ítem")
        data = form_item(key="form_nuevo_item")
        if data:
            if coleccion.find_one({"id_item": data["id_item"]}):
                st.error("⚠️ Ya existe un ítem con ese ID.")
            else:
                data["usuario_registro"] = usuario
                data["fecha_registro"] = datetime.now()
                coleccion.insert_one(data)
                registrar_evento_historial(
                    "Alta de ítem inventario",
                    data.get("maquina_compatible", ""),
                    data["id_item"],
                    f"Alta de ítem: {data['descripcion']}",
                    usuario,
                )
                st.success("Ítem agregado correctamente.")
                st.rerun()

        items = list(coleccion.find())
        if items:
            st.divider()
            st.markdown("### ✏️ Editar ítem existente")
            opciones = {
                f"{i.get('id_item')} - {i.get('descripcion', '')}": i for i in items
            }
            seleccionado = st.selectbox("Seleccionar ítem", list(opciones.keys()))
            seleccionado_datos = opciones[seleccionado]

            nuevos_datos = form_item(defaults=seleccionado_datos)
            if nuevos_datos:
                coleccion.update_one({"_id": seleccionado_datos["_id"]}, {"$set": nuevos_datos})
                registrar_evento_historial(
                    "Edición de ítem inventario",
                    nuevos_datos.get("maquina_compatible", ""),
                    nuevos_datos["id_item"],
                    f"Edición de ítem: {nuevos_datos['descripcion']}",
                    usuario,
                )
                st.success("Ítem actualizado correctamente.")
                st.rerun()

            st.divider()
            st.markdown("### 🗑️ Eliminar ítem")
            eliminar_opcion = st.selectbox(
                "Seleccionar ítem a eliminar",
                list(opciones.keys()),
                key="eliminar_item",
            )
            if st.button("Eliminar ítem seleccionado"):
                item = opciones[eliminar_opcion]
                coleccion.delete_one({"_id": item["_id"]})
                registrar_evento_historial(
                    "Baja de ítem inventario",
                    item.get("maquina_compatible", ""),
                    item["id_item"],
                    f"Baja de ítem: {item.get('descripcion', '')}",
                    usuario,
                )
                st.success("Ítem eliminado correctamente.")
                st.rerun()


if __name__ == "__main__":
    app_inventario("admin")
