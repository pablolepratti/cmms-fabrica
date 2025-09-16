"""
📦 Módulo unificado de Inventario Técnico – CMMS Fábrica

Combina la lógica previa de `app_inventario` y `crud_inventario` en una
única interfaz con layout estándar similar al de Activos Técnicos.
Todas las operaciones se registran en `historial` para garantizar la
trazabilidad según ISO 9001 e ISO 55001.
"""

import pandas as pd
import streamlit as st
from datetime import datetime
from modulos.conexion_mongo import db
from crud.generador_historial import registrar_evento_historial


# --- Helper: obtener colección de inventario de forma consistente ---
def get_coleccion():
    if db is None:
        return None
    return db["inventario"]


def crear_item_inventario(data: dict):
    """Inserta un item de inventario y registra el evento."""
    col = get_coleccion()
    if col is None:
        return None
    col.insert_one(data)
    registrar_evento_historial(
        "Alta de inventario",
        data.get("maquina_compatible"),   # activo técnico asociado si aplica
        data.get("id_item"),
        f"Ingreso de ítem {data.get('descripcion', '')}",
        data.get("usuario_registro", ""),
    )
    return data.get("id_item")


def cargar_inventario() -> pd.DataFrame:
    """Devuelve el inventario completo como DataFrame."""
    col = get_coleccion()
    if col is None:
        return pd.DataFrame()
    datos = list(col.find({}))  # dejamos _id y lo convertimos a string "id"
    df = pd.DataFrame(datos)
    if df.empty:
        return pd.DataFrame(columns=[
            "id", "id_item", "descripcion", "tipo", "cantidad", "unidad",
            "ubicacion", "destino", "uso_destino", "maquina_compatible",
            "stock_minimo", "proveedor", "observaciones", "fecha_registro",
            "ultima_actualizacion", "usuario_registro"
        ])
    # convertir _id BSON a string y renombrar a "id"
    if "_id" in df.columns:
        df["id"] = df["_id"].astype(str)
        df.drop(columns=["_id"], inplace=True)
    for colname in df.columns:
        if "id" in colname.lower():
            df[colname] = df[colname].astype(str)
    return df


def form_item(defaults=None, key: str = "form_inventario"):
    """Formulario para cargar o editar un ítem del inventario."""
    defaults = defaults or {}
    with st.form(key):
        col1, col2 = st.columns(2)
        with col1:
            id_item = st.text_input("ID del ítem", value=str(defaults.get("id_item", "")))
            descripcion = st.text_input("Descripción", value=str(defaults.get("descripcion", "")))
            tipo = st.selectbox(
                "Tipo",
                ["repuesto", "insumo"],
                index=(["repuesto", "insumo"].index(defaults.get("tipo"))
                       if defaults.get("tipo") in ["repuesto", "insumo"] else 0),
            )
            cantidad = st.number_input(
                "Cantidad", min_value=0, step=1, value=int(defaults.get("cantidad", 0)),
            )
            unidad = st.text_input("Unidad", value=str(defaults.get("unidad", "")))
            ubicacion = st.text_input("Ubicación", value=str(defaults.get("ubicacion", "")))
        with col2:
            destino = st.text_input("Destino", value=str(defaults.get("destino", "")))
            uso_destino = st.selectbox(
                "Uso", ["interno", "externo"],
                index=(1 if defaults.get("uso_destino") == "externo" else 0),
            )
            maquina_compatible = st.text_input(
                "Máquina compatible (ID Activo Técnico)",
                value=str(defaults.get("maquina_compatible", "")),
            )
            stock_minimo = st.number_input(
                "Stock mínimo", min_value=0, step=1, value=int(defaults.get("stock_minimo", 0)),
            )
            proveedor = st.text_input("Proveedor", value=str(defaults.get("proveedor", "")))
            observaciones = st.text_area("Observaciones", value=str(defaults.get("observaciones", "")))
        submitted = st.form_submit_button("Guardar")

    if not submitted:
        return None

    if not id_item or not descripcion or not unidad:
        st.error("⚠️ Los campos 'ID del ítem', 'Descripción' y 'Unidad' son obligatorios.")
        return None

    return {
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


def visualizar_inventario() -> None:
    """Muestra el inventario con filtros básicos."""
    df = cargar_inventario()
    if df.empty:
        st.info("No hay ítems cargados en el inventario.")
        return

    if "tipo" in df.columns:
        tipo = st.selectbox("Filtrar por tipo", ["Todos"] + sorted(df["tipo"].dropna().unique().tolist()))
        if tipo != "Todos":
            df = df[df["tipo"] == tipo]

    if "uso_destino" in df.columns:
        uso = st.selectbox("Filtrar por uso", ["Todos"] + sorted(df["uso_destino"].dropna().unique().tolist()))
        if uso != "Todos":
            df = df[df["uso_destino"] == uso]

    if "maquina_compatible" in df.columns:
        maquina = st.selectbox(
            "Filtrar por máquina compatible",
            ["Todas"] + sorted(df["maquina_compatible"].dropna().unique().tolist()),
        )
        if maquina != "Todas":
            df = df[df["maquina_compatible"] == maquina]

    st.dataframe(df.sort_values("descripcion"), use_container_width=True)


def app_inventario(usuario: str) -> None:
    """Interfaz principal para gestionar el inventario técnico."""
    col = get_coleccion()
    if col is None:
        st.error("MongoDB no disponible")
        return

    st.title("📦 Gestión de Inventario Técnico")

    menu = ["Agregar", "Ver", "Editar", "Eliminar"]
    accion = st.sidebar.radio("Acción", menu)

    if accion == "Agregar":
        st.subheader("➕ Agregar nuevo ítem")
        data = form_item(key="form_nuevo_item")
        if data:
            if col.find_one({"id_item": data["id_item"]}):
                st.error("⚠️ Ya existe un ítem con ese ID.")
            else:
                data["usuario_registro"] = usuario
                data["fecha_registro"] = datetime.now()
                crear_item_inventario(data)
                st.success("Ítem agregado correctamente.")

    elif accion == "Ver":
        st.subheader("📄 Inventario Técnico")
        visualizar_inventario()

    elif accion == "Editar":
        st.subheader("✏️ Editar ítem de inventario")
        items = list(col.find())
        if not items:
            st.info("No hay ítems cargados.")
        else:
            opciones = {f"{i.get('id_item','')} - {i.get('descripcion','')}": i for i in items}
            seleccionado = st.selectbox("Seleccionar ítem", list(opciones.keys()))
            seleccionado_datos = opciones[seleccionado]
            nuevos_datos = form_item(defaults=seleccionado_datos, key="editar_item")
            if nuevos_datos:
                col.update_one({"_id": seleccionado_datos["_id"]}, {"$set": nuevos_datos})
                registrar_evento_historial(
                    "Edición de ítem inventario",
                    nuevos_datos.get("maquina_compatible", ""),
                    nuevos_datos["id_item"],
                    f"Edición de ítem: {nuevos_datos['descripcion']}",
                    usuario,
                )
                st.success("Ítem actualizado correctamente.")

    elif accion == "Eliminar":
        st.subheader("🗑️ Eliminar ítem de inventario")
        items = list(col.find())
        if not items:
            st.info("No hay ítems cargados.")
        else:
            opciones = {f"{i.get('id_item','')} - {i.get('descripcion','')}": i for i in items}
            seleccionado = st.selectbox("Seleccionar ítem a eliminar", list(opciones.keys()))
            if st.button("Eliminar ítem seleccionado"):
                item = opciones[seleccionado]
                col.delete_one({"_id": item["_id"]})
                registrar_evento_historial(
                    "Baja de ítem inventario",
                    item.get("maquina_compatible", ""),
                    item.get("id_item",""),
                    f"Baja de ítem: {item.get('descripcion', '')}",
                    usuario,
                )
                st.success("Ítem eliminado correctamente.")


if __name__ == "__main__":
    app_inventario("admin")
