import streamlit as st
from datetime import datetime
from modulos.conexion_mongo import db

coleccion = db["tareas_tecnicas"]

def app():
st.title("📌 Gestión de Tareas Técnicas")

menu = ["Registrar Tarea Técnica", "Ver Tareas", "Editar Tarea", "Eliminar Tarea"]
choice = st.sidebar.selectbox("Acción", menu)

# Formulario
def form_tecnica(defaults=None):
    with st.form("form_tarea_tecnica"):
        id_activo = st.text_input("ID del Activo Técnico (opcional)", value=defaults.get("id_activo_tecnico") if defaults else "")
        fecha_evento = st.date_input("Fecha del Evento", value=defaults.get("fecha_evento") if defaults else datetime.today())
        descripcion = st.text_area("Descripción de la Tarea Técnica", value=defaults.get("descripcion") if defaults else "")
        tipo = st.selectbox("Tipo de Tarea Técnica", ["Presupuesto", "Gestión", "Consulta Técnica", "Otro"],
                            index=["Presupuesto", "Gestión", "Consulta Técnica", "Otro"].index(defaults.get("tipo_tecnica")) if defaults else 0)
        responsable = st.text_input("Responsable", value=defaults.get("responsable") if defaults else "")
        proveedor_externo = st.text_input("Proveedor Externo (si aplica)", value=defaults.get("proveedor_externo") if defaults else "")
        estado = st.selectbox("Estado", ["Abierta", "En proceso", "Cerrada"],
                              index=["Abierta", "En proceso", "Cerrada"].index(defaults.get("estado")) if defaults else 0)
        usuario = st.text_input("Usuario que registra", value=defaults.get("usuario_registro") if defaults else "")
        observaciones = st.text_area("Observaciones adicionales", value=defaults.get("observaciones") if defaults else "")
        submit = st.form_submit_button("Guardar Tarea Técnica")

    if submit:
        data = {
            "id_activo_tecnico": id_activo,
            "fecha_evento": str(fecha_evento),
            "descripcion": descripcion,
            "tipo_tecnica": tipo,
            "responsable": responsable,
            "proveedor_externo": proveedor_externo,
            "estado": estado,
            "usuario_registro": usuario,
            "observaciones": observaciones,
            "fecha_registro": datetime.now()
        }
        return data
    return None

# Registrar
if choice == "Registrar Tarea Técnica":
    st.subheader("➕ Nueva Tarea Técnica")
    data = form_tecnica()
    if data:
        coleccion.insert_one(data)
        st.success("Tarea técnica registrada correctamente.")

# Ver tareas
elif choice == "Ver Tareas":
    st.subheader("📋 Tareas Técnicas Registradas")
    tareas = list(coleccion.find().sort("fecha_evento", -1))
    for t in tareas:
        st.markdown(f"**{t.get('id_activo_tecnico', 'Sin ID')}** ({t['estado']}) - {t['fecha_evento']}")
        st.write(t['descripcion'])
        st.write("---")

# Editar tarea
elif choice == "Editar Tarea":
    st.subheader("✏️ Editar Tarea Técnica")
    tareas = list(coleccion.find())
    opciones = {f"{t.get('id_activo_tecnico', 'Sin ID')} - {t['descripcion'][:30]}": t for t in tareas}
    seleccion = st.selectbox("Seleccionar tarea", list(opciones.keys()))
    datos = opciones[seleccion]

    nuevos_datos = form_tecnica(defaults=datos)
    if nuevos_datos:
        coleccion.update_one({"_id": datos["_id"]}, {"$set": nuevos_datos})
        st.success("Tarea técnica actualizada correctamente.")

# Eliminar tarea
elif choice == "Eliminar Tarea":
    st.subheader("🗑️ Eliminar Tarea Técnica")
    tareas = list(coleccion.find())
    opciones = {f"{t.get('id_activo_tecnico', 'Sin ID')} - {t['descripcion'][:30]}": t for t in tareas}
    seleccion = st.selectbox("Seleccionar tarea", list(opciones.keys()))
    datos = opciones[seleccion]
    if st.button("Eliminar definitivamente"):
        coleccion.delete_one({"_id": datos["_id"]})
        st.success("Tarea técnica eliminada.")

if __name__ == "__main__":
    app()
