import streamlit as st
from datetime import datetime
from modulos.conexion_mongo import db

coleccion = db["activos_tecnicos"]

def app():
    st.title("🔧 Gestión de Activos Técnicos")

    menu = ["Agregar", "Ver", "Editar", "Eliminar"]
    choice = st.sidebar.selectbox("Acción", menu)

    # Campos comunes
    def form_activo(defaults=None):
        opciones_tipo = ["Sistema General", "Infraestructura", "Administración", "Producción",
                         "Logística", "Mantenimiento", "Instrumento Laboratorio", "Equipo en Cliente"]
        opciones_estado = ["Activo", "En revisión", "Fuera de servicio"]

        tipo_default = defaults.get("tipo") if defaults else None
        estado_default = defaults.get("estado") if defaults else None

        # Index seguros
        tipo_index = opciones_tipo.index(tipo_default) if tipo_default in opciones_tipo else 0
        estado_index = opciones_estado.index(estado_default) if estado_default in opciones_estado else 0

        with st.form("form_activo"):
            id_activo = st.text_input("ID del Activo Técnico", value=defaults.get("id_activo_tecnico") if defaults else "")
            nombre = st.text_input("Nombre o Descripción", value=defaults.get("nombre") if defaults else "")
            ubicacion = st.text_input("Ubicación", value=defaults.get("ubicacion") if defaults else "")
            tipo = st.selectbox("Tipo de Activo", opciones_tipo, index=tipo_index)
            estado = st.selectbox("Estado", opciones_estado, index=estado_index)
            usuario = st.text_input("Usuario que registra", value=defaults.get("usuario_registro") if defaults else "")
            submit = st.form_submit_button("Guardar")

            if submit:
                return {
                    "id_activo_tecnico": id_activo,
                    "nombre": nombre,
                    "ubicacion": ubicacion,
                    "tipo": tipo,
                    "estado": estado,
                    "usuario_registro": usuario,
                    "fecha_registro": datetime.now()
                }

        return None

    # Agregar
    if choice == "Agregar":
        st.subheader("➕ Agregar nuevo activo técnico")
        data = form_activo()
        if data:
            coleccion.insert_one(data)
            st.success("Activo técnico agregado correctamente.")

    # Ver
    elif choice == "Ver":
        st.subheader("📋 Lista de activos técnicos agrupados por tipo")
       
        st.markdown("<br><br>", unsafe_allow_html=True)

        activos = list(coleccion.find())
        if not activos:
            st.info("No hay activos cargados.")
        else:
            # Agrupar por tipo
            agrupados = {}
            for a in activos:
                tipo = a.get("tipo", "⛔ Sin Tipo")
                if tipo not in agrupados:
                    agrupados[tipo] = []
                agrupados[tipo].append(a)

            # Mostrar por grupo ordenado alfabéticamente
            for tipo, lista in sorted(agrupados.items()):
                st.markdown(f"<h4 style='text-align: left; margin-bottom: 0.5em;'>🔹 {tipo}</h4>", unsafe_allow_html=True)
                for a in lista:
                    nombre = a.get("nombre", "")
                    estado = a.get("estado", "-")
                    id_activo = a.get("id_activo_tecnico", "⛔ Sin ID")
                    st.markdown(f"- **{id_activo}** – {nombre} ({estado})")


    # Editar
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
                st.success("Activo técnico actualizado correctamente.")
        else:
            st.info("No hay activos cargados.")

    # Eliminar
    elif choice == "Eliminar":
        st.subheader("🗑️ Eliminar activo técnico")
        activos = list(coleccion.find())
        opciones = {f"{a.get('id_activo_tecnico', '⛔ Sin ID')} - {a.get('nombre', '')}": a for a in activos}
        if opciones:
            seleccion = st.selectbox("Seleccionar activo", list(opciones.keys()))
            datos = opciones[seleccion]
            if st.button("Eliminar definitivamente"):
                coleccion.delete_one({"_id": datos["_id"]})
                st.success("Activo técnico eliminado.")
        else:
            st.info("No hay activos cargados.")

if __name__ == "__main__":
    app()

