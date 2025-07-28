# 📄 CRUD de Observaciones Técnicas – CMMS Fábrica
# Versión: Julio 2025
# Autor: Pablo Lepratti
# Normas aplicables: ISO 14224 | ISO 55001 | ISO 9001:2015
# Descripción: Módulo para registrar hallazgos técnicos asociados a activos sin necesidad de acción inmediata.
# Cada evento queda trazado automáticamente en la colección `historial`.

import streamlit as st
from datetime import datetime
from modulos.conexion_mongo import db
from crud.generador_historial import registrar_evento_historial
from modulos.utilidades_formularios import select_activo_tecnico



tipos_observacion = ["Advertencia", "Hallazgo", "Ruido", "Otro"]
estados_posibles = ["Pendiente", "Revisado"]

def generar_id_observacion():
    return f"OBS_{int(datetime.now().timestamp())}"

def form_observacion(defaults=None):
    activos_lista = list(activos.find({}, {"_id": 0, "id_activo_tecnico": 1, "nombre": 1, "pertenece_a": 1}))
    if not activos_lista:
        st.warning("⚠️ No hay activos técnicos registrados.")
        return None

    id_map = {
        a["id_activo_tecnico"]: f"{a['id_activo_tecnico']} - {a.get('nombre', '')}" +
        (f" (pertenece a {a['pertenece_a']})" if a.get("pertenece_a") else "")
        for a in activos_lista
    }
    opciones = [""] + sorted(id_map.values())
    id_default = defaults.get("id_activo_tecnico") if defaults else ""
    label_default = id_map.get(id_default, id_default)
    index_default = opciones.index(label_default) if label_default in opciones else 0

    with st.form("form_observacion"):
        seleccion_visible = st.selectbox("ID del Activo Técnico", opciones, index=index_default)
        id_activo = next((k for k, v in id_map.items() if v == seleccion_visible), "") if seleccion_visible else ""

        id_observacion = defaults.get("id_observacion") if defaults else generar_id_observacion()
        fecha_evento = st.date_input("Fecha del Evento", value=datetime.strptime(defaults.get("fecha_evento"), "%Y-%m-%d") if defaults else datetime.today())
        descripcion = st.text_area("Descripción de la Observación", value=defaults.get("descripcion") if defaults else "")
        tipo = st.selectbox("Tipo de Observación", tipos_observacion,
                            index=tipos_observacion.index(defaults.get("tipo_observacion")) if defaults and defaults.get("tipo_observacion") in tipos_observacion else 0)
        reportado_por = st.text_input("Reportado por", value=defaults.get("reportado_por") if defaults else "")
        estado = st.selectbox("Estado", estados_posibles,
                              index=estados_posibles.index(defaults.get("estado")) if defaults and defaults.get("estado") in estados_posibles else 0)
        usuario = st.text_input("Usuario que registra", value=defaults.get("usuario_registro") if defaults else "")
        observaciones = st.text_area("Notas adicionales", value=defaults.get("observaciones") if defaults else "")

        submit = st.form_submit_button("Guardar Observación")

    if submit:
        if not id_activo or not usuario:
            st.error("Debe seleccionar un activo y completar el usuario.")
            return None

        return {
            "id_observacion": id_observacion,
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
    return None

def app():
    if db is None:
        st.error("MongoDB no disponible")
        return
    coleccion = db["observaciones"]
    activos = db["activos_tecnicos"]

    st.title("👁️ Gestión de Observaciones Técnicas")
    menu = ["Registrar Observación", "Ver Observaciones", "Editar Observación", "Eliminar Observación"]
    choice = st.sidebar.radio("Acción", menu)

    if choice == "Registrar Observación":
        st.subheader("➕ Nueva Observación Técnica")
        data = form_observacion()
        if data:
            coleccion.insert_one(data)
            registrar_evento_historial(
                "Registro de observación técnica",
                data["id_activo_tecnico"],
                data["id_observacion"],
                f"{data['tipo_observacion']} registrada: {data['descripcion'][:60]}...",
                data["usuario_registro"],
                observaciones=data.get("observaciones"),
            )
            st.success("✅ Observación registrada correctamente.")

    elif choice == "Ver Observaciones":
        st.subheader("👁️ Observaciones Técnicas por Activo Técnico")
        observaciones = list(coleccion.find().sort("fecha_evento", -1))

        if not observaciones:
            st.info("No hay observaciones registradas.")
            return

        estado_filtro = st.selectbox("Filtrar por estado", ["Todos"] + estados_posibles)
        texto_filtro = st.text_input("🔍 Buscar por ID, tipo o texto")

        filtradas = []
        for o in observaciones:
            coincide_estado = (estado_filtro == "Todos") or (o.get("estado") == estado_filtro)
            coincide_texto = texto_filtro.lower() in o.get("id_activo_tecnico", "").lower() or \
                             texto_filtro.lower() in o.get("descripcion", "").lower() or \
                             texto_filtro.lower() in o.get("tipo_observacion", "").lower()
            if coincide_estado and coincide_texto:
                filtradas.append(o)

        if not filtradas:
            st.warning("No se encontraron observaciones con esos filtros.")
            return

        activos_listados = sorted(set(o.get("id_activo_tecnico", "⛔ Sin ID") for o in filtradas))
        for activo in activos_listados:
            st.markdown(f"### 🏷️ Activo Técnico: `{activo}`")
            obs_activas = [o for o in filtradas if o.get("id_activo_tecnico") == activo]
            for o in obs_activas:
                st.code(f"ID Observación: {o.get('id_observacion', '❌ No definido')}", language="yaml")
                fecha = o.get("fecha_evento", "Sin Fecha")
                tipo = o.get("tipo_observacion", "Sin Tipo")
                estado = o.get("estado", "Sin Estado")
                descripcion = o.get("descripcion", "")
                st.markdown(f"- 📅 **{fecha}** | 🔍 **Tipo:** {tipo} | 🛠️ **Estado:** {estado}")
                st.write(descripcion)
            st.markdown("---")

    elif choice == "Editar Observación":
        st.subheader("✏️ Editar Observación Técnica")
        obs = list(coleccion.find())
        opciones = {
            f"{o.get('id_observacion', 'Sin ID')} - {o.get('id_activo_tecnico', 'Sin Activo')} ({o.get('fecha_evento', 'Sin Fecha')})": o
            for o in obs
        }
        if not opciones:
            st.info("No hay observaciones disponibles.")
            return
        seleccion = st.selectbox("Seleccionar observación", list(opciones.keys()))
        datos = opciones[seleccion]
        nuevos_datos = form_observacion(defaults=datos)
        if nuevos_datos:
            coleccion.update_one({"_id": datos["_id"]}, {"$set": nuevos_datos})
            registrar_evento_historial(
                "Edición de observación técnica",
                nuevos_datos["id_activo_tecnico"],
                nuevos_datos["id_observacion"],
                f"Observación editada: {nuevos_datos['descripcion'][:60]}...",
                nuevos_datos["usuario_registro"],
                observaciones=nuevos_datos.get("observaciones"),
            )
            st.success("✅ Observación actualizada correctamente.")

    elif choice == "Eliminar Observación":
        st.subheader("🗑️ Eliminar Observación Técnica")
        obs = list(coleccion.find())
        opciones = {
            f"{o.get('id_observacion', 'Sin ID')} - {o.get('id_activo_tecnico', 'Sin Activo')} ({o.get('fecha_evento', 'Sin Fecha')})": o
            for o in obs
        }
        if not opciones:
            st.info("No hay observaciones disponibles.")
            return
        seleccion = st.selectbox("Seleccionar observación", list(opciones.keys()))
        datos = opciones[seleccion]
        if st.button("Eliminar definitivamente"):
            coleccion.delete_one({"_id": datos["_id"]})
            registrar_evento_historial(
                "Baja de observación técnica",
                datos.get("id_activo_tecnico"),
                datos.get("id_observacion"),
                f"Se eliminó la observación: {datos.get('descripcion', '')[:60]}...",
                datos.get("usuario_registro", "desconocido"),
                observaciones=datos.get("observaciones"),
            )
            st.success("🗑️ Observación eliminada correctamente.")

if __name__ == "__main__":
    app()
