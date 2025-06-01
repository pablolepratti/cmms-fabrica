"""
👁️ CRUD de Observaciones Técnicas – CMMS Fábrica

Este módulo permite registrar, visualizar, editar y eliminar observaciones técnicas asociadas a activos técnicos.
Soporta activos jerárquicos mediante el campo `pertenece_a`, reflejando relaciones funcionales.
Registra automáticamente cada evento en la colección `historial` para trazabilidad completa.

✅ Normas aplicables:
- ISO 14224 (Información sobre mantenimiento y confiabilidad de activos)
- ISO 55001 (Gestión de activos físicos y jerarquía funcional)
- ISO 9001:2015 (Gestión de calidad, observaciones y acciones correctivas)
"""

import streamlit as st
from datetime import datetime
from modulos.conexion_mongo import db

coleccion = db["observaciones"]
historial = db["historial"]
activos = db["activos_tecnicos"]

def registrar_evento_historial(evento):
    historial.insert_one({
        "tipo_evento": evento["tipo_evento"],
        "id_activo_tecnico": evento.get("id_activo_tecnico"),
        "descripcion": evento.get("descripcion", ""),
        "usuario": evento.get("usuario"),
        "fecha_evento": datetime.now(),
        "modulo": "observaciones"
    })

def app():
    st.title("👁️ Registro de Observaciones Técnicas")

    menu = ["Registrar Observación", "Ver Observaciones", "Editar Observación", "Eliminar Observación"]
    choice = st.sidebar.radio("Acción", menu)

    def form_observacion(defaults=None):
        activos_lista = list(activos.find({}, {"_id": 0, "id_activo_tecnico": 1, "nombre": 1, "pertenece_a": 1}))
        if not activos_lista:
            st.warning("⚠️ No hay activos técnicos registrados.")
            return None

        opciones = []
        map_id = {}
        for a in activos_lista:
            label = f"{a['id_activo_tecnico']} - {a.get('nombre', '')}"
            if "pertenece_a" in a:
                label += f" (pertenece a {a['pertenece_a']})"
            opciones.append(label)
            map_id[label] = a["id_activo_tecnico"]

        activo_default = None
        if defaults and defaults.get("id_activo_tecnico"):
            for k, v in map_id.items():
                if v == defaults["id_activo_tecnico"]:
                    activo_default = k
                    break

        with st.form("form_observacion"):
            id_activo_label = st.selectbox("ID del Activo Técnico", opciones, index=opciones.index(activo_default) if activo_default else 0)
            id_activo = map_id[id_activo_label]

            fecha_evento = st.date_input("Fecha del Evento", value=defaults.get("fecha_evento") if defaults else datetime.today())
            descripcion = st.text_area("Descripción de la Observación", value=defaults.get("descripcion") if defaults else "")
            tipo = st.selectbox("Tipo de Observación", ["Advertencia", "Hallazgo", "Ruido", "Otro"],
                                index=["Advertencia", "Hallazgo", "Ruido", "Otro"].index(defaults.get("tipo_observacion")) if defaults and defaults.get("tipo_observacion") in ["Advertencia", "Hallazgo", "Ruido", "Otro"] else 0)
            reportado_por = st.text_input("Reportado por", value=defaults.get("reportado_por") if defaults else "")
            estado = st.selectbox("Estado", ["Pendiente", "Revisado"],
                                  index=["Pendiente", "Revisado"].index(defaults.get("estado")) if defaults and defaults.get("estado") in ["Pendiente", "Revisado"] else 0)
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

    if choice == "Registrar Observación":
        st.subheader("➕ Nueva Observación Técnica")
        data = form_observacion()
        if data:
            coleccion.insert_one(data)
            registrar_evento_historial({
                "tipo_evento": "Registro de observación técnica",
                "id_activo_tecnico": data["id_activo_tecnico"],
                "usuario": data["usuario_registro"],
                "descripcion": f"{data['tipo_observacion']} registrada: {data['descripcion'][:60]}..."
            })
            st.success("Observación registrada correctamente.")

    elif choice == "Ver Observaciones":
        st.subheader("👁️ Observaciones Técnicas por Activo Técnico")

        observaciones = list(coleccion.find().sort("fecha_evento", -1))

        if not observaciones:
            st.info("No hay observaciones registradas.")
            return

        estados_existentes = sorted(set(o.get("estado", "Pendiente") for o in observaciones))
        estado_filtro = st.selectbox("Filtrar por estado", ["Todos"] + estados_existentes)
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

        activos_listados = sorted(set(str(o.get("id_activo_tecnico") or "⛔ Sin ID") for o in filtradas))
        for activo in activos_listados:
            st.markdown(f"### 🏷️ Activo Técnico: `{activo}`")
            observaciones_activo = [o for o in filtradas if str(o.get("id_activo_tecnico") or "⛔ Sin ID") == activo]
            for o in observaciones_activo:
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
        opciones = {f"{o.get('id_observacion', 'Sin ID')} - {o.get('id_activo_tecnico', 'Sin Activo')} ({o.get('fecha_evento', 'Sin Fecha')})": o for o in obs}
        seleccion = st.selectbox("Seleccionar observación", list(opciones.keys()))
        datos = opciones[seleccion]
        nuevos_datos = form_observacion(defaults=datos)
        if nuevos_datos:
            coleccion.update_one({"_id": datos["_id"]}, {"$set": nuevos_datos})
            registrar_evento_historial({
                "tipo_evento": "Edición de observación técnica",
                "id_activo_tecnico": nuevos_datos["id_activo_tecnico"],
                "usuario": nuevos_datos["usuario_registro"],
                "descripcion": f"Observación editada: {nuevos_datos['descripcion'][:60]}..."
            })
            st.success("Observación actualizada correctamente.")

    elif choice == "Eliminar Observación":
        st.subheader("🗑️ Eliminar Observación Técnica")
        obs = list(coleccion.find())
        opciones = {f"{o.get('id_observacion', 'Sin ID')} - {o.get('id_activo_tecnico', 'Sin Activo')} ({o.get('fecha_evento', 'Sin Fecha')})": o for o in obs}
        seleccion = st.selectbox("Seleccionar observación", list(opciones.keys()))
        datos = opciones[seleccion]
        if st.button("Eliminar definitivamente"):
            coleccion.delete_one({"_id": datos["_id"]})
            registrar_evento_historial({
                "tipo_evento": "Baja de observación técnica",
                "id_activo_tecnico": datos.get("id_activo_tecnico"),
                "usuario": datos.get("usuario_registro", "desconocido"),
                "descripcion": f"Se eliminó la observación: {datos.get('descripcion', '')[:60]}..."
            })
            st.success("Observación eliminada.")

if __name__ == "__main__":
    app()

