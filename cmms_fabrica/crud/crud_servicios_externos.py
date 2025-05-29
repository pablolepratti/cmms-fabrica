import streamlit as st
from datetime import datetime
from modulos.conexion_mongo import db

coleccion = db["servicios_externos"]

    def app():
    
    st.title("🏢 Proveedores y Servicios Externos")
    
    menu = ["Registrar Proveedor", "Ver Proveedores", "Editar Proveedor", "Eliminar Proveedor"]
    choice = st.sidebar.selectbox("Acción", menu)
    
    # Formulario proveedor externo
    def form_proveedor(defaults=None):
        with st.form("form_proveedor_externo"):
            id_proveedor = st.text_input("ID del Proveedor", value=defaults.get("id_proveedor") if defaults else f"PROV_{int(datetime.now().timestamp())}")
            nombre = st.text_input("Nombre o Razón Social", value=defaults.get("nombre") if defaults else "")
            especialidad = st.text_input("Especialidad o rubro", value=defaults.get("especialidad") if defaults else "")
            contacto = st.text_input("Nombre de contacto", value=defaults.get("contacto") if defaults else "")
            telefono = st.text_input("Teléfono", value=defaults.get("telefono") if defaults else "")
            correo = st.text_input("Correo electrónico", value=defaults.get("correo") if defaults else "")
            observaciones = st.text_area("Observaciones", value=defaults.get("observaciones") if defaults else "")
            submit = st.form_submit_button("Guardar Proveedor")
    
        if submit:
            data = {
                "id_proveedor": id_proveedor,
                "nombre": nombre,
                "especialidad": especialidad,
                "contacto": contacto,
                "telefono": telefono,
                "correo": correo,
                "observaciones": observaciones,
                "fecha_registro": datetime.now()
            }
            return data
        return None
    
    # Registrar nuevo
    if choice == "Registrar Proveedor":
        st.subheader("➕ Nuevo Proveedor Técnico")
        data = form_proveedor()
        if data:
            coleccion.insert_one(data)
            st.success("Proveedor registrado correctamente.")
    
    # Ver proveedores
    elif choice == "Ver Proveedores":
        st.subheader("📋 Servicios Externos Registrados")
        proveedores = list(coleccion.find().sort("nombre", 1))
        for p in proveedores:
            st.markdown(f"**{p['nombre']}** ({p['especialidad']})")
            st.write(f"Contacto: {p['contacto']} | Tel: {p['telefono']} | Correo: {p['correo']}")
            st.write(p.get("observaciones", ""))
            st.write("---")
    
    # Editar proveedor
    elif choice == "Editar Proveedor":
        st.subheader("✏️ Editar Proveedor Técnico")
        proveedores = list(coleccion.find())
        opciones = {f"{p['id_proveedor']} - {p['nombre']}": p for p in proveedores}
        seleccion = st.selectbox("Seleccionar proveedor", list(opciones.keys()))
        datos = opciones[seleccion]
    
        nuevos_datos = form_proveedor(defaults=datos)
        if nuevos_datos:
            coleccion.update_one({"_id": datos["_id"]}, {"$set": nuevos_datos})
            st.success("Proveedor actualizado correctamente.")
    
    # Eliminar proveedor
    elif choice == "Eliminar Proveedor":
        st.subheader("🗑️ Eliminar Proveedor Técnico")
        proveedores = list(coleccion.find())
        opciones = {f"{p['id_proveedor']} - {p['nombre']}": p for p in proveedores}
        seleccion = st.selectbox("Seleccionar proveedor", list(opciones.keys()))
        datos = opciones[seleccion]
        if st.button("Eliminar definitivamente"):
            coleccion.delete_one({"_id": datos["_id"]})
            st.success("Proveedor eliminado.")

if __name__ == "__main__":
    app()
