"""
🛠️ CRUD de Tareas Correctivas – CMMS Fábrica

Este módulo permite registrar, visualizar, editar y eliminar tareas correctivas originadas por fallas en activos técnicos.
Registra automáticamente en la colección `historial` cada evento para asegurar trazabilidad y análisis posterior.

✅ Normas aplicables:
- ISO 14224 (Clasificación de modos de falla y datos de mantenimiento)
- ISO 55001 (Gestión del ciclo de vida del activo – correctivos incluidos)
- ISO 9001:2015 (Gestión de no conformidades, análisis de causa raíz y acciones correctivas)
"""

import streamlit as st
from datetime import datetime
from modulos.conexion_mongo import db

coleccion = db["tareas_correctivas"]
historial = db["historial"]

def registrar_evento_historial(evento):
    historial.insert_one({
        "tipo_evento": evento["tipo_evento"],
        "id_activo_tecnico": evento.get("id_activo_tecnico"),
        "descripcion": evento.get("descripcion", ""),
        "usuario": evento.get("usuario", "sistema"),
        "fecha_evento": datetime.now(),
        "modulo": "tareas_correctivas"
    })

def app():
    st.title("🛠️ Gestión de Tareas Correctivas")

    menu = ["Registrar Falla", "Ver Tareas", "Editar Tarea", "Eliminar Tarea"]
    choice = st.sidebar.radio("Acción", menu)

    def form_tarea(defaults=None):
        with st.form("form_tarea_correctiva"):
            id_activo = st.text_input("ID del Activo Técnico", value=defaults.get("id_activo_tecnico") if defaults else "")
            fecha_evento = st.date_input("Fecha del Evento", value=defaults.get("fecha_evento") if defaults else datetime.today())
            descripcion_falla = st.text_area("Descripción de la Falla", value=defaults.get("descripcion_falla") if defaults else "")
            modo_falla = st.text_input("Modo de Falla", value=defaults.get("modo_falla") if defaults else "")
            
            rca_requerido = st.checkbox("¿Requiere Análisis de Causa Raíz?", value=defaults.get("rca_requerido") if defaults else False)
            if rca_requerido:
                st.info("📌 El análisis de causa raíz (RCA) busca identificar el origen real del problema para evitar que se repita. "
                        "Se recomienda usar métodos como 5 Porqués, Ishikawa o AMFE. Documentá la causa, el método y las acciones derivadas.")

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

    if choice == "Registrar Falla":
        st.subheader("➕ Nueva Tarea Correctiva")
        data = form_tarea()
        if data:
            coleccion.insert_one(data)
            registrar_evento_historial({
                "tipo_evento": "Alta de tarea correctiva",
                "id_activo_tecnico": data["id_activo_tecnico"],
                "usuario": data["usuario_registro"],
                "descripcion": f"Tarea registrada por falla: {data['descripcion_falla'][:60]}..."
            })
            st.success("Tarea correctiva registrada correctamente.")

    elif choice == "Ver Tareas":
        st.subheader("📋 Tareas Correctivas por Activo Técnico")

        tareas = list(coleccion.find().sort("fecha_evento", -1))
        if not tareas:
            st.info("No hay tareas registradas.")
            return

        estados_existentes = sorted(set(t.get("estado", "Abierta") for t in tareas))
        estado_filtro = st.selectbox("Filtrar por estado", ["Todos"] + estados_existentes)

        texto_filtro = st.text_input("🔍 Buscar por ID, modo de falla o descripción")

        filtradas = []
        for t in tareas:
            coincide_estado = estado_filtro == "Todos" or t.get("estado") == estado_filtro
            coincide_texto = texto_filtro.lower() in t.get("id_activo_tecnico", "").lower() or \
                             texto_filtro.lower() in t.get("descripcion_falla", "").lower() or \
                             texto_filtro.lower() in t.get("modo_falla", "").lower()
            if coincide_estado and coincide_texto:
                filtradas.append(t)

        if not filtradas:
            st.warning("No se encontraron tareas con esos filtros.")
            return

        activos = sorted(set(t.get("id_activo_tecnico", "⛔ Sin ID") for t in filtradas))
        for activo in activos:
            st.markdown(f"### 🏷️ Activo Técnico: `{activo}`")
            tareas_activo = [t for t in filtradas if t.get("id_activo_tecnico") == activo]
            for t in tareas_activo:
                fecha = t.get("fecha_evento") or t.get("fecha_reporte", "Sin Fecha")
                estado = t.get("estado", "Sin Estado")
                descripcion = t.get("descripcion_falla") or t.get("descripcion", "")
                st.markdown(f"- 📅 **{fecha}** | 🛠️ **Estado:** {estado}")
                st.write(f"{descripcion}")
            st.markdown("---")

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
            registrar_evento_historial({
                "tipo_evento": "Edición de tarea correctiva",
                "id_activo_tecnico": nuevos_datos["id_activo_tecnico"],
                "usuario": nuevos_datos["usuario_registro"],
                "descripcion": f"Tarea editada: {nuevos_datos['descripcion_falla'][:60]}..."
            })
            st.success("Tarea actualizada correctamente.")

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
            registrar_evento_historial({
                "tipo_evento": "Baja de tarea correctiva",
                "id_activo_tecnico": datos.get("id_activo_tecnico"),
                "usuario": datos.get("usuario_registro", "desconocido"),
                "descripcion": f"Se eliminó tarea: {datos.get('descripcion_falla', '')[:60]}..."
            })
            st.success("Tarea eliminada.")

if __name__ == "__main__":
    app()
