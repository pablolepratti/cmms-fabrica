"""
🛠️ CRUD de Tareas Correctivas – CMMS Fábrica

Este módulo permite registrar, visualizar, editar y eliminar tareas correctivas originadas por fallas en activos técnicos.
Registra automáticamente en la colección `historial` cada evento para asegurar trazabilidad y análisis posterior.

✅ Normas aplicables:
- ISO 14224 (Clasificación de modos de falla y datos de mantenimiento)
- ISO 55001 (Gestión del ciclo de vida del activo – correctivos incluidos)
- ISO 9001:2015 (Gestión de no conformidades, análisis de causa raíz y acciones correctivas)
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from modulos.conexion_mongo import db
from crud.generador_historial import registrar_evento_historial
from modulos.utilidades_formularios import (
    select_activo_tecnico,
    select_proveedores_externos,
)


def crear_tarea_correctiva(data: dict, database=db):
    """Inserta una tarea correctiva y registra el evento."""
    if database is None:
        return None
    coleccion = database["tareas_correctivas"]
    coleccion.insert_one(data)
    registrar_evento_historial(
        "Alta de tarea correctiva",
        data["id_activo_tecnico"],
        data["id_tarea"],
        f"Tarea registrada por falla: {data['descripcion_falla'][:60]}...",
        data["usuario_registro"],
    )
    return data["id_tarea"]

def generar_id_tarea():
    return f"TC-{int(datetime.now().timestamp())}"

def form_tarea(defaults=None):
    with st.form("form_tarea_correctiva"):

        ids_activos = select_activo_tecnico(db)
        id_default = defaults.get("id_activo_tecnico") if defaults else None
        index_default = ids_activos.index(id_default) if id_default in ids_activos else 0 if ids_activos else -1

        id_activo = st.selectbox("ID del Activo Técnico", ids_activos, index=index_default) if ids_activos else st.text_input("ID del Activo Técnico")

        nombres_proveedores = select_proveedores_externos(db)
        proveedor_default = defaults.get("proveedor_externo") if defaults else None
        index_proveedor = nombres_proveedores.index(proveedor_default) if proveedor_default in nombres_proveedores else 0 if nombres_proveedores else -1

        id_tarea = defaults.get("id_tarea") if defaults else generar_id_tarea()
        fecha_evento = st.date_input("Fecha del Evento", value=defaults.get("fecha_evento") if defaults else datetime.today())
        descripcion_falla = st.text_area("Descripción de la Falla", value=defaults.get("descripcion_falla") if defaults else "")
        modo_falla = st.text_input("Modo de Falla", value=defaults.get("modo_falla") if defaults else "")
        rca_requerido = st.checkbox("¿Requiere Análisis de Causa Raíz?", value=defaults.get("rca_requerido") if defaults else False)
        rca_completado = st.checkbox("RCA Completado", value=defaults.get("rca_completado") if defaults else False)

        if rca_requerido:
            causa_raiz = st.text_input("Causa Raíz", value=defaults.get("causa_raiz") if defaults else "")
            metodo_rca = st.text_input("Método RCA", value=defaults.get("metodo_rca") if defaults else "")
            acciones_rca = st.text_area("Acciones Derivadas del RCA", value=defaults.get("acciones_rca") if defaults else "")
            usuario_rca = st.text_input("Usuario Responsable del RCA", value=defaults.get("usuario_rca") if defaults else "")
        else:
            causa_raiz = metodo_rca = acciones_rca = usuario_rca = ""

        responsable = st.text_input("Responsable de la Reparación", value=defaults.get("responsable") if defaults else "")
        tipo_ejecucion = st.radio("¿Quién ejecutó la tarea?", ["Interno", "Externo"],
                                  index=0 if defaults is None or defaults.get("proveedor_externo") in [None, ""] else 1)

        if tipo_ejecucion == "Externo":
            proveedor_externo = st.selectbox("Proveedor Externo (si aplica)", nombres_proveedores, index=index_proveedor) if nombres_proveedores else ""
        else:
            proveedor_externo = ""

        estado = st.selectbox("Estado", ["Abierta", "En proceso", "Cerrada"],
                              index=["Abierta", "En proceso", "Cerrada"].index(defaults.get("estado")) if defaults and defaults.get("estado") in ["Abierta", "En proceso", "Cerrada"] else 0)
        usuario = st.text_input("Usuario que registra", value=defaults.get("usuario_registro") if defaults else "")
        observaciones = st.text_area("Observaciones adicionales", value=defaults.get("observaciones") if defaults else "")
        submit = st.form_submit_button("Guardar Tarea")

    if submit:
        if not responsable or not usuario:
            st.error("Debe completar los campos obligatorios: Responsable y Usuario.")
            return None

        return {
            "id_tarea": id_tarea,
            "id_activo_tecnico": id_activo,
            "fecha_evento": str(fecha_evento),
            "descripcion_falla": descripcion_falla,
            "modo_falla": modo_falla,
            "rca_requerido": rca_requerido,
            "rca_completado": rca_completado,
            "causa_raiz": causa_raiz,
            "metodo_rca": metodo_rca,
            "acciones_rca": acciones_rca,
            "usuario_rca": usuario_rca,
            "responsable": responsable,
            "proveedor_externo": proveedor_externo,
            "estado": estado,
            "usuario_registro": usuario,
            "observaciones": observaciones,
            "fecha_registro": datetime.now(),
            "incompleto": False
        }
    return None

def app():
    if db is None:
        st.error("MongoDB no disponible")
        return
    coleccion = db["tareas_correctivas"]

    st.title("🛠️ Gestión de Tareas Correctivas")
    menu = ["Registrar Falla", "Ver Tareas", "Editar Tarea", "Eliminar Tarea"]
    choice = st.sidebar.radio("Acción", menu)

    if choice == "Registrar Falla":
        st.subheader("➕ Nueva Tarea Correctiva")
        data = form_tarea()
        if data:
            crear_tarea_correctiva(data, db)
            st.success("Tarea correctiva registrada correctamente.")

    elif choice == "Ver Tareas":
        st.subheader("📋 Tareas Correctivas por Activo Técnico")
        mostrar_incompletas = st.checkbox("🔧 Mostrar solo tareas incompletas")
        query_base = {"incompleto": True} if mostrar_incompletas else {}
        tareas = list(coleccion.find(query_base).sort("fecha_evento", -1))

        if not tareas:
            st.info("No hay tareas registradas.")
            return

        estados_existentes = sorted({t.get("estado", "⛔ Sin Estado") for t in tareas})
        estado_filtro = st.selectbox("Filtrar por estado", ["Todos"] + estados_existentes)
        texto_filtro = st.text_input("🔍 Buscar por descripción o ID")

        filtradas = []
        for t in tareas:
            coincide_estado = estado_filtro == "Todos" or t.get("estado") == estado_filtro
            texto = (
                t.get("descripcion_falla", "")
                + t.get("id_activo_tecnico", "")
                + t.get("id_tarea", "")
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
                    id_info = f"ID: {t.get('id_tarea', '')} | Activo: {t.get('id_activo_tecnico', '')}"
                    st.code(id_info, language="yaml")
                    st.markdown(
                        f"- **{t.get('descripcion_falla', '')[:80]}** ({t.get('fecha_evento', '')})"
                    )

    elif choice == "Editar Tarea":
        st.subheader("✏️ Editar Tarea Correctiva")
        mostrar_incompletas = st.checkbox("🔧 Mostrar solo tareas incompletas")
        query = {"incompleto": True} if mostrar_incompletas else {}
        tareas = list(coleccion.find(query))
        opciones = {
            f"{t.get('id_tarea', '❌')} | {t.get('id_activo_tecnico', '⛔')} - {t.get('descripcion_falla', '')[:30]}": t
            for t in tareas
        }

        if opciones:
            seleccion = st.selectbox("Seleccionar tarea", list(opciones.keys()))
            datos = opciones.get(seleccion)
            if datos:
                nuevos_datos = form_tarea(defaults=datos)
                if nuevos_datos:
                    coleccion.update_one({"_id": datos["_id"]}, {"$set": nuevos_datos})
                    registrar_evento_historial(
                        "Edición de tarea correctiva",
                        nuevos_datos["id_activo_tecnico"],
                        nuevos_datos["id_tarea"],
                        f"Tarea editada: {nuevos_datos['descripcion_falla'][:60]}...",
                        nuevos_datos["usuario_registro"],
                    )
                    st.success("Tarea actualizada correctamente.")
        else:
            st.info("No hay tareas disponibles para editar.")

    elif choice == "Eliminar Tarea":
        st.subheader("🗑️ Eliminar Tarea Correctiva")
        tareas = list(coleccion.find())
        opciones = {
            f"{t.get('id_tarea', '❌')} | {t.get('id_activo_tecnico', '⛔')} - {t.get('descripcion_falla', '')[:30]}": t
            for t in tareas
        }

        if opciones:
            seleccion = st.selectbox("Seleccionar tarea", list(opciones.keys()))
            datos = opciones.get(seleccion)
            if datos and st.button("Eliminar definitivamente"):
                coleccion.delete_one({"_id": datos["_id"]})
                registrar_evento_historial(
                    "Baja de tarea correctiva",
                    datos.get("id_activo_tecnico"),
                    datos.get("id_tarea"),
                    f"Se eliminó tarea: {datos.get('descripcion_falla', '')[:60]}...",
                    datos.get("usuario_registro", "desconocido"),
                )
                st.success("Tarea eliminada. Refrescá la vista para confirmar.")
        else:
            st.info("No hay tareas disponibles para eliminar.")

if __name__ == "__main__":
    app()
