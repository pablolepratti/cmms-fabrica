'''
📌 CRUD de Tareas Técnicas – CMMS Fábrica

Este módulo permite registrar, visualizar, editar y eliminar tareas técnicas de gestión, presupuestos u otras intervenciones no correctivas ni preventivas.
Se registran automáticamente en la colección `historial` para trazabilidad.

✅ Normas aplicables:
- ISO 9001:2015
- ISO 55001
'''

import streamlit as st
from datetime import datetime
from modulos.conexion_mongo import db
from crud.generador_historial import registrar_evento_historial

coleccion = db["tareas_tecnicas"]

def generar_id_tarea_tecnica():
    return f"TT-{int(datetime.now().timestamp())}"

def form_tecnica(defaults=None):
    with st.form("form_tarea_tecnica"):
        hoy = datetime.today()

        activos = list(db["activos_tecnicos"].find({}, {"_id": 0, "id_activo_tecnico": 1, "pertenece_a": 1}))
        id_map = {
            a["id_activo_tecnico"]: (
                f"{a['id_activo_tecnico']} (pertenece a {a['pertenece_a']})" if a.get("pertenece_a")
                else a["id_activo_tecnico"]
            )
            for a in activos if "id_activo_tecnico" in a
        }
        ids_visibles = [""] + sorted(id_map.values())
        id_default = defaults.get("id_activo_tecnico") if defaults else ""
        label_default = id_map.get(id_default, id_default)
        index_default = ids_visibles.index(label_default) if label_default in ids_visibles else 0

        seleccion_visible = st.selectbox("ID del Activo Técnico (opcional)", ids_visibles, index=index_default)

        proveedores = list(db["servicios_externos"].find({}, {"_id": 0, "nombre": 1}))
        nombres_proveedores = sorted([p["nombre"] for p in proveedores if "nombre" in p])
        proveedor_default = defaults.get("proveedor_externo") if defaults else ""
        index_proveedor = nombres_proveedores.index(proveedor_default) if proveedor_default in nombres_proveedores else 0 if nombres_proveedores else -1

        id_activo = ""
        if seleccion_visible and seleccion_visible in id_map.values():
            id_activo = next(k for k, v in id_map.items() if v == seleccion_visible)

        id_tarea = defaults.get("id_tarea_tecnica") if defaults else generar_id_tarea_tecnica()
        fecha_evento = st.date_input("Fecha del Evento", value=defaults.get("fecha_evento") if defaults else hoy)
        descripcion = st.text_area("Descripción Técnica", value=defaults.get("descripcion") if defaults else "")
        tipo_tecnica = st.selectbox("Tipo de Tarea Técnica", ["Presupuesto", "Consulta", "Gestión", "Otra"],
                                    index=["Presupuesto", "Consulta", "Gestión", "Otra"].index(defaults.get("tipo_tecnica")) if defaults else 0)
        responsable = st.text_input("Responsable", value=defaults.get("responsable") if defaults else "")
        proveedor_externo = st.selectbox("Proveedor Externo (si aplica)", nombres_proveedores, index=index_proveedor) if nombres_proveedores else ""
        estado = st.selectbox("Estado", ["Pendiente", "En curso", "Finalizada"],
                              index=["Pendiente", "En curso", "Finalizada"].index(defaults.get("estado")) if defaults else 0)
        usuario = st.text_input("Usuario que registra", value=defaults.get("usuario_registro") if defaults else "")
        observaciones = st.text_area("Observaciones adicionales", value=defaults.get("observaciones") if defaults else "")
        submit = st.form_submit_button("Guardar Tarea Técnica")

    if submit:
        if not responsable or not usuario:
            st.error("Debe completar los campos obligatorios: Responsable y Usuario.")
            return None

        return {
            "id_tarea_tecnica": id_tarea,
            "id_activo_tecnico": id_activo,
            "fecha_evento": str(fecha_evento),
            "descripcion": descripcion,
            "tipo_tecnica": tipo_tecnica,
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
    menu = ["Registrar Tarea", "Ver Tareas", "Editar Tarea", "Eliminar Tarea"]
    choice = st.sidebar.radio("Acción", menu)

    if choice == "Registrar Tarea":
        st.subheader("➕ Nueva Tarea Técnica")
        data = form_tecnica()
        if data:
            coleccion.insert_one(data)
            registrar_evento_historial(
                "Alta de tarea técnica",
                data.get("id_activo_tecnico", "Sin ID"),
                data["id_tarea_tecnica"],
                f"Tarea técnica: {data['descripcion'][:60]}...",
                data["usuario_registro"]
            )
            st.success("Tarea técnica registrada correctamente.")

    elif choice == "Ver Tareas":
        st.subheader("📋 Tareas Técnicas Registradas")
        tareas = list(coleccion.find().sort("fecha_evento", -1))
        if not tareas:
            st.info("No hay tareas técnicas registradas.")
            return
        for t in tareas:
            st.code(f"{t.get('id_tarea_tecnica')} | {t.get('id_activo_tecnico', '⛔ Sin ID')}", language="yaml")
            st.markdown(f"- 📅 **{t.get('fecha_evento')}** | 📌 **Estado:** {t.get('estado')}")
            st.markdown(f"- 📝 {t.get('descripcion', '')}")
            st.markdown("---")

    elif choice == "Editar Tarea":
        st.subheader("✏️ Editar Tarea Técnica")
        tareas = list(coleccion.find())
        opciones = {
            f"{t.get('id_tarea_tecnica')} | {t.get('id_activo_tecnico', '⛔')} - {t.get('descripcion', '')[:30]}": t
            for t in tareas
        }
        if opciones:
            seleccion = st.selectbox("Seleccionar tarea", list(opciones.keys()))
            datos = opciones.get(seleccion)
            if datos:
                nuevos_datos = form_tecnica(defaults=datos)
                if nuevos_datos:
                    coleccion.update_one({"_id": datos["_id"]}, {"$set": nuevos_datos})
                    registrar_evento_historial(
                        "Edición de tarea técnica",
                        nuevos_datos.get("id_activo_tecnico", "Sin ID"),
                        nuevos_datos["id_tarea_tecnica"],
                        f"Tarea editada: {nuevos_datos['descripcion'][:60]}...",
                        nuevos_datos["usuario_registro"]
                    )
                    st.success("Tarea técnica actualizada.")
        else:
            st.info("No hay tareas disponibles para editar.")

    elif choice == "Eliminar Tarea":
        st.subheader("🗑️ Eliminar Tarea Técnica")
        tareas = list(coleccion.find())
        opciones = {
            f"{t.get('id_tarea_tecnica')} | {t.get('id_activo_tecnico', '⛔')} - {t.get('descripcion', '')[:30]}": t
            for t in tareas
        }
        if opciones:
            seleccion = st.selectbox("Seleccionar tarea", list(opciones.keys()))
            datos = opciones.get(seleccion)
            if datos and st.button("Eliminar definitivamente"):
                coleccion.delete_one({"_id": datos["_id"]})
                registrar_evento_historial(
                    "Baja de tarea técnica",
                    datos.get("id_activo_tecnico", "Sin ID"),
                    datos.get("id_tarea_tecnica"),
                    f"Se eliminó tarea técnica: {datos.get('descripcion', '')[:60]}...",
                    datos.get("usuario_registro", "desconocido")
                )
                st.success("Tarea eliminada.")
        else:
            st.info("No hay tareas disponibles para eliminar.")

if __name__ == "__main__":
    app()
