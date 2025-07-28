"""
🏢 CRUD de Servicios Externos – CMMS Fábrica

Este módulo permite registrar, visualizar, editar y eliminar proveedores técnicos o servicios externos utilizados en la fábrica.
Cada cambio se documenta automáticamente en la colección `historial`.

✅ Normas aplicables:
- ISO 9001:2015
- ISO 55001
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from modulos.conexion_mongo import db
from crud.generador_historial import registrar_evento_historial


def crear_proveedor(data: dict, database=db):
    """Inserta un proveedor externo y registra el evento."""
    if database is None:
        return None
    coleccion = database["servicios_externos"]
    coleccion.insert_one(data)
    registrar_evento_historial(
        "Alta de proveedor externo",
        None,
        data["id_proveedor"],
        f"Alta de proveedor {data['nombre']}",
        data["usuario_registro"],
    )
    return data["id_proveedor"]

def app():
    if db is None:
        st.error("MongoDB no disponible")
        return
    coleccion = db["servicios_externos"]

    st.title("🏢 Proveedores y Servicios Externos")

    menu = ["Registrar Proveedor", "Ver Proveedores", "Editar Proveedor", "Eliminar Proveedor"]
    choice = st.sidebar.radio("Acción", menu)

    def form_proveedor(defaults=None):
        with st.form("form_proveedor_externo"):
            id_proveedor = st.text_input("ID del Proveedor", value=defaults.get("id_proveedor") if defaults else f"PROV_{int(datetime.now().timestamp())}")
            nombre = st.text_input("Nombre o Razón Social", value=defaults.get("nombre") if defaults else "")
            especialidad = st.text_input("Especialidad o rubro", value=defaults.get("especialidad") if defaults else "")
            contacto = st.text_input("Nombre de contacto", value=defaults.get("contacto") if defaults else "")
            telefono = st.text_input("Teléfono", value=defaults.get("telefono") if defaults else "")
            correo = st.text_input("Correo electrónico", value=defaults.get("correo") if defaults else "")
            observaciones = st.text_area("Observaciones", value=defaults.get("observaciones") if defaults else "")
            usuario = st.text_input("Usuario que registra", value=defaults.get("usuario_registro") if defaults else "")
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
                "usuario_registro": usuario,
                "fecha_registro": datetime.now()
            }
            return data
        return None

    if choice == "Registrar Proveedor":
        st.subheader("➕ Nuevo Proveedor Técnico")
        data = form_proveedor()
        if data:
            crear_proveedor(data, db)
            st.success("Proveedor registrado correctamente.")

    elif choice == "Ver Proveedores":
        st.subheader("📋 Servicios Externos Registrados")
        proveedores = list(coleccion.find().sort("nombre", 1))
        if not proveedores:
            st.info("No hay proveedores cargados.")
            return

        texto_filtro = st.text_input("🔍 Buscar por nombre o ID")

        filtrados = []
        for p in proveedores:
            texto = (
                p.get("nombre", "")
                + p.get("id_proveedor", "")
                + p.get("especialidad", "")
            )
            if texto_filtro.lower() in texto.lower():
                filtrados.append(p)

        if not filtrados:
            st.warning("No se encontraron registros con esos filtros.")
        else:
            for p in filtrados:
                st.code(f"ID Proveedor: {p.get('id_proveedor', '')}", language="yaml")
                st.markdown(
                    f"- **{p.get('nombre', '')}** ({p.get('especialidad', '')})"
                )

    elif choice == "Editar Proveedor":
        st.subheader("✏️ Editar Proveedor Técnico")
        proveedores = list(coleccion.find())
        opciones = {f"{p['id_proveedor']} - {p['nombre']}": p for p in proveedores}
        if not opciones:
            st.info("No hay proveedores para editar.")
            return
        seleccion = st.selectbox("Seleccionar proveedor", list(opciones.keys()))
        datos = opciones[seleccion]
        nuevos_datos = form_proveedor(defaults=datos)
        if nuevos_datos:
            coleccion.update_one({"_id": datos["_id"]}, {"$set": nuevos_datos})
            registrar_evento_historial(
                "Edición de proveedor externo",
                None,
                nuevos_datos["id_proveedor"],
                f"Se actualizó proveedor {nuevos_datos['nombre']}",
                nuevos_datos["usuario_registro"],
            )
            st.success("Proveedor actualizado correctamente.")

    elif choice == "Eliminar Proveedor":
        st.subheader("🗑️ Eliminar Proveedor Técnico")
        proveedores = list(coleccion.find())
        opciones = {f"{p['id_proveedor']} - {p['nombre']}": p for p in proveedores}
        if not opciones:
            st.info("No hay proveedores para eliminar.")
            return
        seleccion = st.selectbox("Seleccionar proveedor", list(opciones.keys()))
        datos = opciones[seleccion]
        if st.button("Eliminar definitivamente"):
            coleccion.delete_one({"_id": datos["_id"]})
            registrar_evento_historial(
                "Baja de proveedor externo",
                None,
                datos.get("id_proveedor"),
                f"Se eliminó al proveedor {datos['nombre']}",
                datos.get("usuario_registro", "desconocido"),
            )
            st.success("Proveedor eliminado. Actualizá la vista para confirmar.")

if __name__ == "__main__":
    app()
