"""Herramienta para actualizar IDs de documentos en múltiples colecciones."""

import streamlit as st
from .conexion_mongo import db

# Diccionario de colecciones, campos editables y rutas de actualización
EDITABLES = {
    "activos_tecnicos": {
        "id_activo_tecnico": [
            "tareas_correctivas.id_activo_tecnico",
            "tareas_tecnicas.id_activo_tecnico",
            "planes_preventivos.id_activo_tecnico",
            "observaciones.id_activo_tecnico",
            "calibraciones.id_activo_tecnico",
            "historial.id_activo_tecnico",
        ]
    },
    "tareas_correctivas": {"id_tarea": ["historial.id_origen"]},
    "tareas_tecnicas": {"id_tarea_tecnica": ["historial.id_origen"]},
    "planes_preventivos": {"id_plan": ["historial.id_origen"]},
    "observaciones": {
        "id_observacion": ["historial.id_origen"],
        "id_obs": [],
    },
    "calibraciones": {"id_calibracion": ["historial.id_origen"]},
    "servicios_externos": {"id_proveedor": ["historial.id_origen"]},
    "historial": {
        "id_evento": [],
        "id_referencia": [],
    },
    "maquinas": {
        "id": [
            "tareas.codigo_maquina",
            "mantenimientos_preventivos.codigo_maquina",
            "historial.id_maquina",
            "observaciones.id_maquina",
        ]
    },
    "tareas": {"id_tarea": []},
    "mantenimientos_preventivos": {"id_mantenimiento": []},
}

def app(config: dict = EDITABLES) -> None:
    """Interfaz de Streamlit para modificar IDs en colecciones MongoDB."""

    st.subheader("🛠️ Cambiar IDs manuales en MongoDB")

    coleccion_nombre = st.selectbox("📦 Seleccionar colección", list(config.keys()))
    campos = list(config[coleccion_nombre].keys())
    campo = st.selectbox("🔑 Seleccionar campo editable", campos)

    if campo == "_id":
        st.warning("⚠️ El campo '_id' no se puede editar directamente.")
        return

    coleccion = db[coleccion_nombre]
    documentos = list(
        coleccion.find({campo: {"$exists": True}}, {campo: 1, "_id": 0})
    )
    ids = sorted(set(str(doc[campo]) for doc in documentos if campo in doc))

    if not ids:
        st.info("No hay IDs disponibles para editar en esta colección.")
        return

    id_actual = st.selectbox("🆔 Seleccionar ID actual", ids)
    nuevo_id = st.text_input("🆕 Ingresar nuevo ID").strip()

    if st.button("Actualizar ID"):
        if not nuevo_id:
            st.error("⚠️ El nuevo ID no puede estar vacío.")
            return
        if coleccion.find_one({campo: nuevo_id}):
            st.error("⚠️ Ya existe un documento con ese nuevo ID.")
            return

        resultado_principal = coleccion.update_many(
            {campo: id_actual}, {"$set": {campo: nuevo_id}}
        )
        total_actualizados = resultado_principal.modified_count

        for ruta in config[coleccion_nombre][campo]:
            col_rel, campo_rel = ruta.split(".")
            resultado = db[col_rel].update_many(
                {campo_rel: id_actual}, {"$set": {campo_rel: nuevo_id}}
            )
            total_actualizados += resultado.modified_count

        st.success(
            f"✅ Se actualizó el ID '{id_actual}' por '{nuevo_id}' en {total_actualizados} documento(s)."
        )

