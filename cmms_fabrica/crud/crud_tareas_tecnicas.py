'''
📌 CRUD de Tareas Técnicas – CMMS Fábrica

Este módulo permite registrar, visualizar, editar y eliminar tareas técnicas de gestión, presupuestos u otras intervenciones no correctivas ni preventivas.
Se registran automáticamente en la colección `historial` para trazabilidad.

✅ Normas aplicables:
- ISO 9001:2015 (Control de tareas técnicas, presupuestos, acciones de soporte)
- ISO 55001 (Gestión de mantenimiento y soporte técnico como parte del ciclo de vida del activo)
'''

import streamlit as st
from datetime import datetime
from modulos.conexion_mongo import db

coleccion = db["tareas_tecnicas"]
historial = db["historial"]

def registrar_evento_historial(evento):
    historial.insert_one({
        "tipo_evento": "tecnica",
        "id_activo_tecnico": evento.get("id_activo_tecnico", ""),
        "descripcion": evento.get("descripcion", ""),
        "usuario": evento.get("usuario", "sistema"),
        "fecha_evento": datetime.now(),
        "modulo": "tareas_tecnicas"
    })

def form_tecnica(defaults=None):
    with st.form("form_tarea_tecnica"):
        hoy = datetime.today()

        # 🔽 Selectbox dinámico para IDs de activos técnicos
        lista_ids = [d["id_activo"] for d in db["activos_tecnicos"].find({}, {"_id": 0, "id_activo": 1})]
        lista_ids = sorted(lista_ids)
        lista_ids.insert(0, "")  # Para permitir vacío si es opcional

        id_activo_default = defaults.get("id_activo_tecnico") if defaults else ""
        id_activo = st.selectbox("ID del Activo Técnico (opcional)", options=lista_ids, index=lista_ids.index(id_activo_default) if id_activo_default in lista_ids else 0)

        fecha_evento = st.date_input("📆 Fecha del Evento", value=defaults.get("fecha_evento", hoy) if defaults else hoy)
        fecha_inicio = st.date_input("🗕️ Fecha de Inicio", value=defaults.get("fecha_inicio", fecha_evento) if defaults else fecha_evento)
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
        return {
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
    return None

def app():
    st.title("📌 Gestión de Tareas Técnicas")

    menu = ["Registrar Tarea Técnica", "Ver Tareas", "Editar Tarea", "Eliminar Tarea"]
    choice = st.sidebar.radio("Acción", menu)

    if choice == "Registrar Tarea Técnica":
        st.subheader("➕ Nueva Tarea Técnica")
        data = form_tecnica()
        if data:
            coleccion.insert_one(data)
            registrar_evento_historial({
                "id_activo_tecnico": data["id_activo_tecnico"],
                "usuario": data["usuario_registro"],
                "descripcion": f"Tarea registrada: {data['descripcion'][:60]}..."
            })
            st.success("Tarea técnica registrada correctamente.")

    elif choice == "Ver Tareas":
        st.subheader("📋 Tareas Técnicas por Activo Técnico")

        tareas = list(coleccion.find().sort("fecha_evento", -1))
        if not tareas:
            st.info("No hay tareas técnicas registradas.")
            return

        estado_filtro = st.selectbox("📌 Filtrar por Estado", ["Todos", "Abierta", "En proceso", "Cerrada"])
        tipo_filtro = st.selectbox("📂 Filtrar por Tipo", ["Todos", "Presupuesto", "Gestión", "Consulta Técnica", "Otro"])
        texto_filtro = st.text_input("🔍 Buscar por ID, tipo o descripción")

        filtradas = []
        for t in tareas:
            coincide_estado = estado_filtro == "Todos" or t.get("estado") == estado_filtro
            coincide_tipo = tipo_filtro == "Todos" or t.get("tipo_tecnica") == tipo_filtro
            coincide_texto = texto_filtro.lower() in str(t.get("id_activo_tecnico", "")).lower() or \
                             texto_filtro.lower() in str(t.get("descripcion", "")).lower() or \
                             texto_filtro.lower() in str(t.get("tipo_tecnica", "")).lower()
            if coincide_estado and coincide_tipo and coincide_texto:
                filtradas.append(t)

        if not filtradas:
            st.warning("No se encontraron tareas técnicas con esos filtros.")
            return

        activos = sorted(set(str(t.get("id_activo_tecnico") or "⛔ Sin ID") for t in filtradas))
        for activo in activos:
            st.markdown(f"### 🏷️ Activo Técnico: `{activo}`")
            tareas_activo = [t for t in filtradas if str(t.get("id_activo_tecnico") or "⛔ Sin ID") == activo]
            for t in tareas_activo:
                fecha = t.get("fecha_evento", "Sin Fecha")
                estado = t.get("estado", "Sin Estado")
                tipo = t.get("tipo_tecnica", "Sin Tipo")
                descripcion = t.get("descripcion", "")
                st.markdown(f"- 📅 **{fecha}** | 📋 **Tipo:** {tipo} | 🛠️ **Estado:** {estado}")
                st.write(descripcion)
            st.markdown("---")

        # ✅ Finalizar tarea técnica desde la vista
        st.markdown("### ✅ Finalizar Tarea Técnica")
        tareas_abiertas = [t for t in filtradas if t.get("estado") != "Cerrada"]

        if not tareas_abiertas:
            st.info("Todas las tareas ya están finalizadas.")
        else:
            opciones = {f"{t['id_activo_tecnico']} - {t['descripcion'][:30]}": t for t in tareas_abiertas}
            seleccion = st.selectbox("Seleccionar tarea a finalizar", list(opciones.keys()))
            datos = opciones[seleccion]

            if st.button("Marcar como finalizada"):
                coleccion.update_one(
                    {"_id": datos["_id"]},
                    {"$set": {
                        "estado": "Cerrada",
                        "fecha_actualizacion": datetime.now(),
                        "observaciones": datos.get("observaciones", "") + " | Finalizada vía dashboard"
                    }}
                )
                registrar_evento_historial({
                    "id_activo_tecnico": datos["id_activo_tecnico"],
                    "usuario": datos["usuario_registro"],
                    "descripcion": f"Tarea marcada como finalizada: {datos['descripcion'][:60]}..."
                })
                st.success("Tarea marcada como finalizada.")
                st.rerun()

    elif choice == "Editar Tarea":
        st.subheader("✏️ Editar Tarea Técnica")
        tareas = list(coleccion.find())
        opciones = {f"{t.get('id_activo_tecnico', 'Sin ID')} - {t.get('descripcion', '')[:30]}": t for t in tareas}
        seleccion = st.selectbox("Seleccionar tarea", list(opciones.keys()))
        datos = opciones[seleccion]
        nuevos_datos = form_tecnica(defaults=datos)
        if nuevos_datos:
            coleccion.update_one({"_id": datos["_id"]}, {"$set": nuevos_datos})
            registrar_evento_historial({
                "id_activo_tecnico": nuevos_datos["id_activo_tecnico"],
                "usuario": nuevos_datos["usuario_registro"],
                "descripcion": f"Tarea técnica editada: {nuevos_datos['descripcion'][:60]}..."
            })
            st.success("Tarea técnica actualizada correctamente.")

    elif choice == "Eliminar Tarea":
        st.subheader("🗑️ Eliminar Tarea Técnica")
        tareas = list(coleccion.find())
        opciones = {f"{t.get('id_activo_tecnico', 'Sin ID')} - {t.get('descripcion', '')[:30]}": t for t in tareas}
        seleccion = st.selectbox("Seleccionar tarea", list(opciones.keys()))
        datos = opciones[seleccion]
        if st.button("Eliminar definitivamente"):
            coleccion.delete_one({"_id": datos["_id"]})
            registrar_evento_historial({
                "id_activo_tecnico": datos.get("id_activo_tecnico", ""),
                "usuario": datos.get("usuario_registro", "desconocido"),
                "descripcion": f"Se eliminó tarea: {datos.get('descripcion', '')[:60]}..."
            })
            st.success("Tarea técnica eliminada.")

if __name__ == "__main__":
    app()
