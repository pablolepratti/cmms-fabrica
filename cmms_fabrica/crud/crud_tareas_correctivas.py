import streamlit as st
from datetime import datetime
from modulos.conexion_mongo import db

coleccion = db["tareas_correctivas"]

def app():    

    st.title("🛠️ Gestión de Tareas Correctivas")
    
    menu = ["Registrar Falla", "Ver Tareas", "Editar Tarea", "Eliminar Tarea"]
    choice = st.sidebar.selectbox("Acción", menu)
    
    def form_tarea(defaults=None):
        with st.form("form_tarea_correctiva"):
            id_activo = st.text_input("ID del Activo Técnico", value=defaults.get("id_activo_tecnico") if defaults else "")
            fecha_evento = st.date_input("Fecha del Evento", value=defaults.get("fecha_evento") if defaults else datetime.today())
            descripcion_falla = st.text_area("Descripción de la Falla", value=defaults.get("descripcion_falla") if defaults else "")
            modo_falla = st.text_input("Modo de Falla", value=defaults.get("modo_falla") if defaults else "")
            rca_requerido = st.checkbox("¿Requiere Análisis de Causa Raíz?", value=defaults.get("rca_requerido") if defaults else False)
            rca_completado = st.checkbox("RCA Completado", value=defaults.get("rca_completado") if defaults else False)
            causa_raiz = st.text_input("Causa Raíz", value=defaults.get("causa_raiz") if defaults else "")
            metodo_rca = st.text_input("Método RCA", value=defaults.get("metodo_rca") if defaults else "")
            acciones_rca = st.text_area("Acciones Derivadas del RCA", value=defaults.get("acciones_rca") if defaults else "")
            usuario_rca = st.text_input("Usuario Responsable del RCA", value=defaults.get("usuario_rca") if defaults else "")
            responsable = st.text_input("Responsable de la Reparación", value=defaults.get("responsable") if defaults else "")
            proveedor_externo = st.text_input("Proveedor Externo (si aplica)", value=defaults.get("proveedor_externo") if defaults else "")
            estado = st.selectbox("Estado", ["Abierta", "En proceso", "Cerrada"],
                                  index=["Abierta", "En proceso", "Cerrada"].index(defaults.get("estado")) if defaults and defaults.get("estado") in ["Abierta", "En proceso", "Cerrada"] else 0)
            usuario = st.text_input("Usuario que registra", value=defaults.get("usuario_registro") if defaults else "")
            observaciones = st.text_area("Observaciones adicionales", value=defaults.get("observaciones") if defaults else "")
            submit = st.form_submit_button("Guardar Tarea")

        if submit:
            data = {
                "id_activo_tecnico": id_activo,
                "fecha_evento": str(fecha_evento),
                "descripcion_falla": descripcion_falla,
                "modo_falla": modo_falla,
                "rca_requerido": rca_requerido,
                "rca_completado": rca_completado,
                "causa_raiz": causa_raiz,
                "metodo_rca": metodo_rca,
                "acciones_rca": acciones_rca,
                "usuario_rca": usuario_rca,
                "responsable": responsable,
                "proveedor_externo": proveedor_externo,
                "estado": estado,
                "usuario_registro": usuario,
                "observaciones": observaciones,
                "fecha_registro": datetime.now()
            }
            return data
        return None

    # Registrar nueva tarea
    if choice == "Registrar Falla":
        st.subheader("➕ Nueva Tarea Correctiva")
        data = form_tarea()
        if data:
            coleccion.insert_one(data)
            st.success("Tarea correctiva registrada correctamente.")

    # Ver tareas existentes
    elif choice == "Ver Tareas":
        st.subheader("📋 Tareas Correctivas Registradas")
        tareas = list(coleccion.find().sort("fecha_evento", -1))

        for t in tareas:
            id_activo = t.get("id_activo_tecnico", "⛔ Sin ID")
            estado = t.get("estado", "Sin Estado")
            fecha = t.get("fecha_evento") or t.get("fecha_reporte", "Sin Fecha")
            descripcion = t.get("descripcion_falla") or t.get("descripcion", "")

            st.markdown(f"**{id_activo}** ({estado}) - {fecha}")
            st.write(descripcion)
            st.write("---")

    # Editar tarea existente
    elif choice == "Editar Tarea":
        st.subheader("✏️ Editar Tarea Correctiva")
        tareas = list(coleccion.find())

        opciones = {}
        for t in tareas:
            id_activo = t.get("id_activo_tecnico", "⛔ Sin ID")
            desc = t.get("descripcion_falla") or t.get("descripcion") or ""
            opciones[f"{id_activo} - {desc[:30]}"] = t

        seleccion = st.selectbox("Seleccionar tarea", list(opciones.keys()))
        datos = opciones[seleccion]

        nuevos_datos = form_tarea(defaults=datos)
        if nuevos_datos:
            coleccion.update_one({"_id": datos["_id"]}, {"$set": nuevos_datos})
            st.success("Tarea actualizada correctamente.")

    # Eliminar tarea
    elif choice == "Eliminar Tarea":
        st.subheader("🗑️ Eliminar Tarea Correctiva")
        tareas = list(coleccion.find())

        opciones = {}
        for t in tareas:
            id_activo = t.get("id_activo_tecnico", "⛔ Sin ID")
            desc = t.get("descripcion_falla") or t.get("descripcion") or ""
            opciones[f"{id_activo} - {desc[:30]}"] = t

        seleccion = st.selectbox("Seleccionar tarea", list(opciones.keys()))
        datos = opciones[seleccion]

        if st.button("Eliminar definitivamente"):
            coleccion.delete_one({"_id": datos["_id"]})
            st.success("Tarea eliminada.")

if __name__ == "__main__":
    app()
