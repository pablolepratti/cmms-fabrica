import streamlit as st
from datetime import datetime
from modulos.conexion_mongo import db

coleccion = db["tareas_tecnicas"]

def app():
    st.title("📌 Gestión de Tareas Técnicas")

    menu = ["Registrar Tarea Técnica", "Ver Tareas", "Editar Tarea", "Eliminar Tarea"]
    choice = st.sidebar.selectbox("Acción", menu)

    def form_tecnica(defaults=None):
        with st.form("form_tarea_tecnica"):
            hoy = datetime.today()
            id_activo = st.text_input("ID del Activo Técnico (opcional)", value=defaults.get("id_activo_tecnico") if defaults else "")
            fecha_evento = st.date_input("📆 Fecha del Evento", value=defaults.get("fecha_evento", hoy) if defaults else hoy)
            fecha_inicio = st.date_input("📅 Fecha de Inicio", value=defaults.get("fecha_inicio", fecha_evento) if defaults else fecha_evento)
            fecha_actualizacion = st.date_input("🕓 Fecha de Última Actualización", value=defaults.get("fecha_actualizacion", fecha_evento) if defaults else fecha_evento)
            descripcion = st.text_area("Descripción de la Tarea Técnica", value=defaults.get("descripcion") if defaults else "")
            tipo = st.selectbox("Tipo de Tarea Técnica", ["Presupuesto", "Gestión", "Consulta Técnica", "Otro"],
                                index=["Presupuesto", "Gestión", "Consulta Técnica", "Otro"].index(defaults.get("tipo_tecnica")) if defaults and defaults.get("tipo_tecnica") in ["Presupuesto", "Gestión", "Consulta Técnica", "Otro"] else 0)
            responsable = st.text_input("Responsable", value=defaults.get("responsable") if defaults else "")
            proveedor_externo = st.text_input("Proveedor Externo (si aplica)", value=defaults.get("proveedor_externo") if defaults else "")
            estado = st.selectbox("Estado", ["Abierta", "En proceso", "Cerrada"],
                                  index=["Abierta", "En proceso", "Cerrada"].index(defaults.get("estado")) if defaults and defaults.get("estado") in ["Abierta", "En proceso", "Cerrada"] else 0)
            usuario = st.text_input("Usuario que registra", value=defaults.get("usuario_registro") if defaults else "")
            observaciones = st.text_area("Observaciones adicionales", value=defaults.get("observaciones") if defaults else "")
            submit = st.form_submit_button("Guardar Tarea Técnica")

        if submit:
            data = {
                "id_activo_tecnico": id_activo,
                "fecha_evento": str(fecha_evento),
                "fecha_inicio": str(fecha_inicio),
                "fecha_actualizacion": str(fecha_actualizacion),
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

        # Filtros
        estado_filtro = st.selectbox("Filtrar por Estado", ["Todos", "Abierta", "En proceso", "Cerrada"])
        tipo_filtro = st.selectbox("Filtrar por Tipo de Tarea", ["Todos", "Presupuesto", "Gestión", "Consulta Técnica", "Otro"])

        # Traer todas las tareas
        tareas = list(coleccion.find().sort("fecha_evento", -1))

        # Aplicar filtros
        if estado_filtro != "Todos":
            tareas = [t for t in tareas if t.get("estado") == estado_filtro]
        if tipo_filtro != "Todos":
            tareas = [t for t in tareas if t.get("tipo_tecnica") == tipo_filtro]

        # Mostrar resultados
        if tareas:
            for t in tareas:
                id_activo = t.get('id_activo_tecnico', 'Sin ID')
                estado = t.get('estado', 'Sin Estado')
                tipo = t.get('tipo_tecnica', 'Sin Tipo')
                fecha = t.get('fecha_evento', 'Sin Fecha')
                descripcion = t.get('descripcion', '')
                st.markdown(f"**{id_activo}** ({estado} / {tipo}) - {fecha}")
                st.write(descripcion)
                st.write("---")
        else:
            st.info("No hay tareas técnicas que coincidan con los filtros seleccionados.")

    # Editar tarea
    elif choice == "Editar Tarea":
        st.subheader("✏️ Editar Tarea Técnica")
        tareas = list(coleccion.find())
        opciones = {f"{t.get('id_activo_tecnico', 'Sin ID')} - {t.get('descripcion', '')[:30]}": t for t in tareas}
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
        opciones = {f"{t.get('id_activo_tecnico', 'Sin ID')} - {t.get('descripcion', '')[:30]}": t for t in tareas}
        seleccion = st.selectbox("Seleccionar tarea", list(opciones.keys()))
        datos = opciones[seleccion]
        if st.button("Eliminar definitivamente"):
            coleccion.delete_one({"_id": datos["_id"]})
            st.success("Tarea técnica eliminada.")

if __name__ == "__main__":
    app()
