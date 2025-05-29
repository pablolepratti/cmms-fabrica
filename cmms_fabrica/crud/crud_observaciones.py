import streamlit as st
from datetime import datetime
from modulos.conexion_mongo import db

coleccion = db["observaciones"]

st.title("👁️ Registro de Observaciones Técnicas")

menu = ["Registrar Observación", "Ver Observaciones", "Editar Observación", "Eliminar Observación"]
choice = st.sidebar.selectbox("Acción", menu)

# Formulario de observación
def form_observacion(defaults=None):
    with st.form("form_observacion"):
        id_activo = st.text_input("ID del Activo Técnico", value=defaults.get("id_activo_tecnico") if defaults else "")
        fecha_evento = st.date_input("Fecha del Evento", value=defaults.get("fecha_evento") if defaults else datetime.today())
        descripcion = st.text_area("Descripción de la Observación", value=defaults.get("descripcion") if defaults else "")
        tipo = st.selectbox("Tipo de Observación", ["Advertencia", "Hallazgo", "Ruido", "Otro"],
                            index=["Advertencia", "Hallazgo", "Ruido", "Otro"].index(defaults.get("tipo_observacion")) if defaults else 0)
        reportado_por = st.text_input("Reportado por", value=defaults.get("reportado_por") if defaults else "")
        estado = st.selectbox("Estado", ["Pendiente", "Revisado"],
                              index=["Pendiente", "Revisado"].index(defaults.get("estado")) if defaults else 0)
        usuario = st.text_input("Usuario que registra", value=defaults.get("usuario_registro") if defaults else "")
        observaciones = st.text_area("Notas adicionales", value=defaults.get("observaciones") if defaults else "")
        submit = st.form_submit_button("Guardar Observación")

    if submit:
        data = {
            "id_observacion": f"OBS_{int(datetime.now().timestamp())}",
            "id_activo_tecnico": id_activo,
            "fecha_evento": str(fecha_evento),
            "descripcion": descripcion,
            "tipo_observacion": tipo,
            "reportado_por": reportado_por,
            "estado": estado,
            "usuario_registro": usuario,
            "observaciones": observaciones,
            "fecha_registro": datetime.now()
        }
        return data
    return None

# Registrar
if choice == "Registrar Observación":
    st.subheader("➕ Nueva Observación Técnica")
    data = form_observacion()
    if data:
        coleccion.insert_one(data)
        st.success("Observación registrada correctamente.")

# Ver observaciones
elif choice == "Ver Observaciones":
    st.subheader("📋 Observaciones Técnicas Registradas")
    obs = list(coleccion.find().sort("fecha_evento", -1))
    for o in obs:
        st.markdown(f"**{o['id_activo_tecnico']}** - {o['fecha_evento']} - {o['tipo_observacion']}")
        st.write(o['descripcion'])
        st.write("---")

# Editar
elif choice == "Editar Observación":
    st.subheader("✏️ Editar Observación Técnica")
    obs = list(coleccion.find())
    opciones = {f"{o['id_observacion']} - {o['id_activo_tecnico']} ({o['fecha_evento']})": o for o in obs}
    seleccion = st.selectbox("Seleccionar observación", list(opciones.keys()))
    datos = opciones[seleccion]

    nuevos_datos = form_observacion(defaults=datos)
    if nuevos_datos:
        coleccion.update_one({"_id": datos["_id"]}, {"$set": nuevos_datos})
        st.success("Observación actualizada correctamente.")

# Eliminar
elif choice == "Eliminar Observación":
    st.subheader("🗑️ Eliminar Observación Técnica")
    obs = list(coleccion.find())
    opciones = {f"{o['id_observacion']} - {o['id_activo_tecnico']} ({o['fecha_evento']})": o for o in obs}
    seleccion = st.selectbox("Seleccionar observación", list(opciones.keys()))
    datos = opciones[seleccion]
    if st.button("Eliminar definitivamente"):
        coleccion.delete_one({"_id": datos["_id"]})
        st.success("Observación eliminada.")
