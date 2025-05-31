import streamlit as st
from modulos.conexion_mongo import db

# 🔁 Campos editables por colección y relaciones a mantener
EDITABLES = {
    "activos_tecnicos": {
        "id_activo_tecnico": [
            "tareas_correctivas.id_activo_tecnico",
            "tareas_tecnicas.id_activo_tecnico",
            "planes_preventivos.id_activo_tecnico",
            "observaciones.id_activo_tecnico",
            "calibraciones.id_activo_tecnico",
            "historial.id_activo_tecnico"
        ]
    },
    "tareas_correctivas": {
        "id_origen": ["historial.id_origen"]
    },
    "tareas_tecnicas": {
        "id_origen": ["historial.id_origen"]
    },
    "planes_preventivos": {
        "id_plan": ["historial.id_origen"]
    },
    "observaciones": {
        "id_observacion": ["historial.id_origen"]
    },
    "calibraciones": {
        "_id": []  # No editable por ahora
    },
    "servicios_externos": {
        "id_proveedor": []  # No relacionado con otras colecciones
    }
}

def app():
    st.subheader("🛠️ Cambiar IDs manuales en MongoDB")

    coleccion_nombre = st.selectbox("📦 Seleccionar colección", list(EDITABLES.keys()))
    campos = list(EDITABLES[coleccion_nombre].keys())
    campo = st.selectbox("🔑 Seleccionar campo editable", campos)

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

        # Principal
        coleccion.update_many({campo: id_actual}, {"$set": {campo: nuevo_id}})

        # Relaciones
        for ruta in EDITABLES[coleccion_nombre][campo]:
            col_rel, campo_rel = ruta.split(".")
            db[col_rel].update_many({campo_rel: id_actual}, {"$set": {campo_rel: nuevo_id}})

        st.success(f"✅ ID actualizado de '{id_actual}' a '{nuevo_id}' en '{coleccion_nombre}' y colecciones relacionadas.")
