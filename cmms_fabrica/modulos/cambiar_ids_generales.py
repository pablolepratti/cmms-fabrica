
import streamlit as st
from modulos.conexion_mongo import db

# Definir los campos editables por colección y en qué otras colecciones deben reflejarse
EDITABLES = {
    "maquinas": {
        "id": ["tareas.codigo_maquina", "mantenimientos_preventivos.codigo_maquina", "historial.id_maquina", "observaciones.id_maquina"]
    },
    "tareas": {
        "id_tarea": []
    },
    "mantenimientos_preventivos": {
        "id_mantenimiento": []
    },
    "historial": {
        "id_referencia": []
    },
    "observaciones": {
        "id_obs": []
    }
}

def cambiar_ids_generales():
    st.subheader("🛠️ Cambiar IDs manuales en MongoDB")

    coleccion_nombre = st.selectbox("📦 Seleccionar colección", list(EDITABLES.keys()))
    campos = list(EDITABLES[coleccion_nombre].keys())
    campo = st.selectbox("🔑 Seleccionar campo ID editable", campos)

    coleccion = db[coleccion_nombre]
    ids = [doc[campo] for doc in coleccion.find({campo: {"$exists": True}}, {campo: 1, "_id": 0})]
    ids = sorted(set(str(i) for i in ids))

    if not ids:
        st.info("No hay IDs disponibles para editar en esta colección.")
        return

    id_actual = st.selectbox("🆔 Seleccionar ID actual", ids)
    nuevo_id = st.text_input("🆕 Ingresar nuevo ID")

    if st.button("Actualizar ID"):
        if not nuevo_id.strip():
            st.error("⚠️ El nuevo ID no puede estar vacío.")
            return

        if coleccion.find_one({campo: nuevo_id}):
            st.error("⚠️ Ya existe un documento con ese nuevo ID.")
            return

        # Actualizar en la colección principal
        coleccion.update_many({campo: id_actual}, {"$set": {campo: nuevo_id}})

        # Actualizar en las colecciones relacionadas
        for ruta in EDITABLES[coleccion_nombre][campo]:
            col_rel, campo_rel = ruta.split(".")
            db[col_rel].update_many({campo_rel: id_actual}, {"$set": {campo_rel: nuevo_id}})

        st.success(f"✅ ID actualizado de '{id_actual}' a '{nuevo_id}' en '{coleccion_nombre}' y colecciones relacionadas.")
