"""
🔧 CRUD de Activos Técnicos – CMMS Fábrica

Este módulo permite la gestión completa de activos técnicos (agregar, ver, editar, eliminar).
Registra automáticamente los eventos en la colección `historial` para trazabilidad completa.

✅ Normas aplicables:
- ISO 14224 (Información sobre confiabilidad y mantenimiento de activos)
- ISO 55000 (Gestión de activos)
- ISO 9001:2015 (Trazabilidad y control documental en mantenimiento)
"""

import streamlit as st
from datetime import datetime
from modulos.conexion_mongo import db

coleccion = db["activos_tecnicos"]
historial = db["historial"]

def registrar_evento_historial(evento):
    historial.insert_one({
        "tipo_evento": evento["tipo_evento"],
        "id_activo_tecnico": evento.get("id_activo_tecnico"),
        "descripcion": evento.get("descripcion", ""),
        "usuario": evento.get("usuario"),
        "fecha_evento": datetime.now(),
        "modulo": "activos_tecnicos"
    })

def app():
    st.title("🔧 Gestión de Activos Técnicos")

    menu = ["Agregar", "Ver", "Editar", "Eliminar"]
    choice = st.sidebar.radio("Acción", menu)

    def form_activo(defaults=None):
        opciones_tipo = ["Sistema General", "Infraestructura", "Administración", "Producción",
                         "Logística", "Mantenimiento", "Instrumento Laboratorio", "Equipo en Cliente", "Componente"]
        opciones_estado = ["Activo", "En revisión", "Fuera de servicio"]

        tipo_default = defaults.get("tipo") if defaults else None
        estado_default = defaults.get("estado") if defaults else None

        tipo_index = opciones_tipo.index(tipo_default) if tipo_default in opciones_tipo else 0
        estado_index = opciones_estado.index(estado_default) if estado_default in opciones_estado else 0

        with st.form("form_activo"):
            id_activo = st.text_input("ID del Activo Técnico", value=defaults.get("id_activo_tecnico") if defaults else "")
            nombre = st.text_input("Nombre o Descripción", value=defaults.get("nombre") if defaults else "")
            ubicacion = st.text_input("Ubicación", value=defaults.get("ubicacion") if defaults else "")
            tipo = st.selectbox("Tipo de Activo", opciones_tipo, index=tipo_index)
            estado = st.selectbox("Estado", opciones_estado, index=estado_index)

            # Selectbox dinámico para jerarquía funcional
            activos_existentes = list(coleccion.find({}, {"_id": 0, "id_activo_tecnico": 1}))
            ids_disponibles = sorted([a["id_activo_tecnico"] for a in activos_existentes if a.get("id_activo_tecnico") != id_activo])
            ids_disponibles.insert(0, "")  # permitir vacío
            valor_default = defaults.get("pertenece_a") if defaults else ""
            index_default = ids_disponibles.index(valor_default) if valor_default in ids_disponibles else 0
            pertenece_a = st.selectbox("Pertenece a (opcional)", options=ids_disponibles, index=index_default)

            usuario = st.text_input("Usuario que registra", value=defaults.get("usuario_registro") if defaults else "")
            submit = st.form_submit_button("Guardar")

            if submit:
                data = {
                    "id_activo_tecnico": id_activo,
                    "nombre": nombre,
                    "ubicacion": ubicacion,
                    "tipo": tipo,
                    "estado": estado,
                    "usuario_registro": usuario,
                    "fecha_registro": datetime.now()
                }
                if pertenece_a:
                    data["pertenece_a"] = pertenece_a
                return data

        return None

    if choice == "Agregar":
        st.subheader("➕ Agregar nuevo activo técnico")
        data = form_activo()
        if data:
            coleccion.insert_one(data)
            registrar_evento_historial({
                "tipo_evento": "Alta de activo técnico",
                "id_activo_tecnico": data["id_activo_tecnico"],
                "usuario": data["usuario_registro"],
                "descripcion": f"Se dio de alta el activo '{data['nombre']}'"
            })
            st.success("Activo técnico agregado correctamente.")

    elif choice == "Ver":
        st.subheader("📋 Lista de activos técnicos filtrable")

        activos = list(coleccion.find())
        if not activos:
            st.info("No hay activos cargados.")
            return

        tipos_existentes = sorted(set([a.get("tipo", "⛔ Sin Tipo") for a in activos]))
        tipo_filtro = st.selectbox("Filtrar por tipo de activo", ["Todos"] + tipos_existentes)
        texto_filtro = st.text_input("🔍 Buscar por nombre o ID")

        filtrados = []
        for a in activos:
            coincide_tipo = (tipo_filtro == "Todos") or (a.get("tipo") == tipo_filtro)
            coincide_texto = texto_filtro.lower() in a.get("nombre", "").lower() or texto_filtro.lower() in a.get("id_activo_tecnico", "").lower()
            if coincide_tipo and coincide_texto:
                filtrados.append(a)

        if not filtrados:
            st.warning("No se encontraron activos con esos filtros.")
        else:
            agrupados = {}
            for a in filtrados:
                tipo = a.get("tipo", "⛔ Sin Tipo")
                agrupados.setdefault(tipo, []).append(a)

            for tipo, lista in sorted(agrupados.items()):
                st.markdown(f"<h4 style='text-align: left; margin-bottom: 0.5em;'>🔹 {tipo}</h4>", unsafe_allow_html=True)
                for a in lista:
                    nombre = a.get("nombre", "")
                    estado = a.get("estado", "-")
                    id_activo = a.get("id_activo_tecnico", "⛔ Sin ID")
                    subtitulo = f" (pertenece a {a['pertenece_a']})" if "pertenece_a" in a else ""
                    st.code(f"ID del Activo: {id_activo}", language="yaml")
                    st.markdown(f"- **{nombre}** ({estado}){subtitulo}")

    elif choice == "Editar":
        st.subheader("✏️ Editar activo técnico")
        activos = list(coleccion.find())
        opciones = {f"{a.get('id_activo_tecnico', '⛔ Sin ID')} - {a.get('nombre', '')}": a for a in activos}
        if opciones:
            seleccion = st.selectbox("Seleccionar activo", list(opciones.keys()))
            datos = opciones[seleccion]

            nuevos_datos = form_activo(defaults=datos)
            if nuevos_datos:
                coleccion.update_one({"_id": datos["_id"]}, {"$set": nuevos_datos})
                registrar_evento_historial({
                    "tipo_evento": "Edición de activo técnico",
                    "id_activo_tecnico": nuevos_datos["id_activo_tecnico"],
                    "usuario": nuevos_datos["usuario_registro"],
                    "descripcion": f"Se editó el activo '{nuevos_datos['nombre']}'"
                })
                st.success("Activo técnico actualizado correctamente.")
        else:
            st.info("No hay activos cargados.")

    elif choice == "Eliminar":
        st.subheader("🗑️ Eliminar activo técnico")
        activos = list(coleccion.find())
        opciones = {f"{a.get('id_activo_tecnico', '⛔ Sin ID')} - {a.get('nombre', '')}": a for a in activos}
        if opciones:
            seleccion = st.selectbox("Seleccionar activo", list(opciones.keys()))
            datos = opciones[seleccion]
            if st.button("Eliminar definitivamente"):
                coleccion.delete_one({"_id": datos["_id"]})
                registrar_evento_historial({
                    "tipo_evento": "Baja de activo técnico",
                    "id_activo_tecnico": datos.get("id_activo_tecnico"),
                    "usuario": datos.get("usuario_registro", "desconocido"),
                    "descripcion": f"Se eliminó el activo '{datos.get('nombre', '')}'"
                })
                st.success("Activo técnico eliminado.")
        else:
            st.info("No hay activos cargados.")

if __name__ == "__main__":
    app()
