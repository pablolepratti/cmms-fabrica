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
        with st.form("form_activo"):
            id_activo = st.text_input("ID del Activo Técnico", value=defaults.get("id_activo_tecnico") if defaults else "")
            nombre = st.text_input("Nombre o Descripción", value=defaults.get("nombre") if defaults else "")
            ubicacion = st.text_input("Ubicación", value=defaults.get("ubicacion") if defaults else "")
            tipo = st.selectbox("Tipo de Activo", ["Producción", "Logística", "Infraestructura", "Laboratorio", "Frigorífico"],
                                 index=["Producción", "Logística", "Infraestructura", "Laboratorio", "Frigorífico"].index(defaults.get("tipo")) if defaults else 0)
            estado = st.selectbox("Estado", ["Activo", "En revisión", "Fuera de servicio"],
                                  index=["Activo", "En revisión", "Fuera de servicio"].index(defaults.get("estado")) if defaults else 0)
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
            return data
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
        st.subheader("📋 Lista de activos técnicos")
        activos = list(coleccion.find())
        for a in activos:
            st.write(f"**{a['id_activo_tecnico']}** - {a['nombre']} ({a['estado']})")

    # Editar
    elif choice == "Editar":
        st.subheader("✏️ Editar activo técnico")
        activos = list(coleccion.find())
        opciones = {f"{a['id_activo_tecnico']} - {a['nombre']}": a for a in activos}
        seleccion = st.selectbox("Seleccionar activo", list(opciones.keys()))
        datos = opciones[seleccion]

        nuevos_datos = form_activo(defaults=datos)
        if nuevos_datos:
            coleccion.update_one({"_id": datos["_id"]}, {"$set": nuevos_datos})
            st.success("Activo técnico actualizado correctamente.")

    # Eliminar
    elif choice == "Eliminar":
        st.subheader("🗑️ Eliminar activo técnico")
        activos = list(coleccion.find())
        opciones = {f"{a['id_activo_tecnico']} - {a['nombre']}": a for a in activos}
        seleccion = st.selectbox("Seleccionar activo", list(opciones.keys()))
        datos = opciones[seleccion]
        if st.button("Eliminar definitivamente"):
            coleccion.delete_one({"_id": datos["_id"]})
            st.success("Activo técnico eliminado.")

if __name__ == "__main__":
    app()
