"""
📄 CRUD de Tareas Técnicas – CMMS Fábrica

Descripción: Este módulo permite registrar, visualizar, editar y eliminar tareas técnicas no preventivas ni correctivas.
Cada acción se registra automáticamente en la colección `historial` para trazabilidad completa.

Normas aplicables: ISO 9001:2015 | ISO 55001 | ISO 14224

"""

import streamlit as st
import pandas as pd
from datetime import datetime
from cmms_fabrica.modulos.conexion_mongo import db
from cmms_fabrica.crud.generador_historial import registrar_evento_historial
from cmms_fabrica.modulos.utilidades_formularios import (
    select_activo_tecnico,
    select_proveedores_externos,
)


def crear_tarea_tecnica(data: dict, database=db):
    """Inserta una tarea técnica y registra el evento."""
    if database is None:
        return None
    coleccion = database["tareas_tecnicas"]
    coleccion.insert_one(data)
    registrar_evento_historial(
        tipo_evento="Alta de tarea técnica",
        id_activo=data.get("id_activo_tecnico", "Sin ID"),
        descripcion=f"Tarea técnica: {data['descripcion'][:60]}...",
        usuario=data["usuario_registro"],
        id_origen=data["id_tarea_tecnica"],
    )
    return data["id_tarea_tecnica"]

estados_posibles = ["Pendiente", "En curso", "Finalizada"]
tipos_tecnica = ["Presupuesto", "Consulta", "Gestión", "Otra"]

def generar_id_tarea_tecnica():
    return f"TT-{int(datetime.now().timestamp())}"

def form_tecnica(defaults=None):
    with st.form("form_tarea_tecnica"):
        hoy = datetime.today()

        # Activos técnicos
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
        id_activo = next((k for k, v in id_map.items() if v == seleccion_visible), "") if seleccion_visible else ""

        # Proveedores externos
        nombres_proveedores = select_proveedores_externos(db)
        proveedor_default = defaults.get("proveedor_externo") if defaults else ""
        index_proveedor = nombres_proveedores.index(proveedor_default) if proveedor_default in nombres_proveedores else 0

        # Campos principales
        id_tarea = defaults.get("id_tarea_tecnica") if defaults else generar_id_tarea_tecnica()
        fecha_evento = st.date_input("Fecha del Evento", value=datetime.strptime(defaults.get("fecha_evento"), "%Y-%m-%d") if defaults else hoy)
        descripcion = st.text_area("Descripción Técnica", value=defaults.get("descripcion") if defaults else "")
        tipo_tecnica = st.selectbox("Tipo de Tarea Técnica", tipos_tecnica,
                                    index=tipos_tecnica.index(defaults.get("tipo_tecnica")) if defaults and defaults.get("tipo_tecnica") in tipos_tecnica else 0)
        responsable = st.text_input("Responsable", value=defaults.get("responsable") if defaults else "")

        # Proveedor externo opcional
        proveedor_externo = ""
        usa_proveedor = st.checkbox("¿Participa un proveedor externo?", value=bool(proveedor_default))
        if usa_proveedor and nombres_proveedores:
            proveedor_externo = st.selectbox("Proveedor Externo", nombres_proveedores, index=index_proveedor)

        estado_default = defaults.get("estado") if defaults else ""
        estado_index = estados_posibles.index(estado_default) if estado_default in estados_posibles else 0
        estado = st.selectbox("Estado", estados_posibles, index=estado_index)
        usuario = st.text_input("Usuario que registra", value=defaults.get("usuario_registro") if defaults else "")
        observaciones = st.text_area("Observaciones adicionales", value=defaults.get("observaciones") if defaults else "")

        submit = st.form_submit_button("Guardar Tarea Técnica")

    if submit:
        if not responsable or not usuario:
            st.error("Debe completar los campos obligatorios: Responsable y Usuario.")
            return None
        if usa_proveedor and not proveedor_externo:
            st.error("Debe seleccionar un proveedor si indicó que participa un externo.")
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
    if db is None:
        st.error("MongoDB no disponible")
        return
    coleccion = db["tareas_tecnicas"]

    st.title("🧾 Gestión de Tareas Técnicas")
    menu = ["Registrar Tarea", "Ver Tareas", "Editar Tarea", "Eliminar Tarea"]
    choice = st.sidebar.radio("Acción", menu)

    if choice == "Registrar Tarea":
        st.subheader("➕ Alta de Tarea Técnica")
        data = form_tecnica()
        if data:
            crear_tarea_tecnica(data, db)
            st.success("✅ Tarea técnica registrada correctamente.")

    elif choice == "Ver Tareas":
        st.subheader("📋 Tareas Técnicas Registradas")
        tareas = list(coleccion.find().sort("fecha_evento", -1))
        if not tareas:
            st.info("No hay tareas técnicas registradas.")
            return

        estados = sorted({t.get("estado", "⛔ Sin Estado") for t in tareas})
        estado_filtro = st.selectbox("Filtrar por estado", ["Todos"] + estados)
        texto_filtro = st.text_input("🔍 Buscar por descripción o ID")

        filtradas = []
        for t in tareas:
            coincide_estado = estado_filtro == "Todos" or t.get("estado") == estado_filtro
            texto = (
                t.get("descripcion", "")
                + t.get("id_activo_tecnico", "")
                + t.get("id_tarea_tecnica", "")
            )
            coincide_texto = texto_filtro.lower() in texto.lower()
            if coincide_estado and coincide_texto:
                filtradas.append(t)

        if not filtradas:
            st.warning("No se encontraron registros con esos filtros.")
        else:
            agrupados = {}
            for t in filtradas:
                clave = t.get("estado", "⛔ Sin Estado")
                agrupados.setdefault(clave, []).append(t)

            for estado, lista in sorted(agrupados.items()):
                st.markdown(
                    f"<h4 style='text-align: left; margin-bottom: 0.5em;'>🔹 {estado}</h4>",
                    unsafe_allow_html=True,
                )
                for t in lista:
                    id_info = f"ID: {t.get('id_tarea_tecnica', '')} | Activo: {t.get('id_activo_tecnico', '')}"
                    st.code(id_info, language="yaml")
                    st.markdown(
                        f"- **{t.get('descripcion', '')[:80]}** ({t.get('fecha_evento', '')})"
                    )

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
                        tipo_evento="Edición de tarea técnica",
                        id_activo=nuevos_datos.get("id_activo_tecnico", "Sin ID"),
                        descripcion=f"Tarea editada: {nuevos_datos['descripcion'][:60]}...",
                        usuario=nuevos_datos["usuario_registro"],
                        id_origen=nuevos_datos["id_tarea_tecnica"],
                    )
                    st.success("✅ Tarea técnica actualizada.")
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
                    tipo_evento="Baja de tarea técnica",
                    id_activo=datos.get("id_activo_tecnico", "Sin ID"),
                    descripcion=f"Se eliminó tarea técnica: {datos.get('descripcion', '')[:60]}...",
                    usuario=datos.get("usuario_registro", "desconocido"),
                    id_origen=datos.get("id_tarea_tecnica"),
                )
                st.success("🗑️ Tarea eliminada correctamente.")
        else:
            st.info("No hay tareas disponibles para eliminar.")

if __name__ == "__main__":
    app()
