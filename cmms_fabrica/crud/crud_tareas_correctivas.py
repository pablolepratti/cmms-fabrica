"""
🛠️ CRUD de Tareas Correctivas – CMMS Fábrica

Este módulo permite registrar, visualizar, editar y eliminar tareas correctivas originadas por fallas en activos técnicos.
Registra automáticamente en la colección `historial` cada evento para asegurar trazabilidad y análisis posterior.

✅ Normas aplicables:
- ISO 14224 (Clasificación de modos de falla y datos de mantenimiento)
- ISO 55001 (Gestión del ciclo de vida del activo – correctivos incluidos)
- ISO 9001:2015 (Gestión de no conformidades, análisis de causa raíz y acciones correctivas)
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, List, Optional

import pandas as pd
import streamlit as st

from modulos.conexion_mongo import get_db
from modulos.repository import CMMSRepository, HistorialEvent
from modulos.utilidades_formularios import (
    select_activo_tecnico,
    select_proveedores_externos,
)


def generar_id_tarea():
    return f"TC-{int(datetime.now().timestamp())}"

def _to_date(value: Optional[object]) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value).date()
        except ValueError:
            pass
    return datetime.today().date()


def _to_datetime(value: Optional[object]) -> datetime:
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            pass
    return datetime.utcnow()


def shared_section(title: str, subtitle: Optional[str] = None):
    st.markdown(f"### {title}")
    if subtitle:
        st.caption(subtitle)
    return st.container()


def form_tarea(database, defaults: Optional[Dict[str, Any]] = None):
    defaults = defaults or {}
    with st.form("form_tarea_correctiva"):
        ids_activos: List[str] = select_activo_tecnico(database)
        id_default = defaults.get("id_activo_tecnico")

        if ids_activos:
            index_default = ids_activos.index(id_default) if id_default in ids_activos else 0
            id_activo = st.selectbox(
                "ID del Activo Técnico",
                ids_activos,
                index=index_default,
            )
        else:
            st.warning("No hay activos técnicos cargados. Ingrese el ID manualmente o registre un activo.")
            id_activo = st.text_input("ID del Activo Técnico").strip()

        proveedores = select_proveedores_externos(database)
        proveedor_default = defaults.get("proveedor_externo") or ""
        index_proveedor = proveedores.index(proveedor_default) if proveedor_default in proveedores else 0

        id_tarea = defaults.get("id_tarea") or generar_id_tarea()
        fecha_evento_valor = st.date_input(
            "Fecha del Evento",
            value=_to_date(defaults.get("fecha_evento")),
        )
        descripcion_falla = st.text_area(
            "Descripción de la Falla",
            value=defaults.get("descripcion_falla", ""),
        ).strip()
        modo_falla = st.text_input(
            "Modo de Falla",
            value=defaults.get("modo_falla", ""),
        ).strip()
        rca_requerido = st.checkbox(
            "¿Requiere Análisis de Causa Raíz?",
            value=defaults.get("rca_requerido", False),
        )
        rca_completado = st.checkbox(
            "RCA Completado",
            value=defaults.get("rca_completado", False),
        )

        if rca_requerido:
            causa_raiz = st.text_input("Causa Raíz", value=defaults.get("causa_raiz", "")).strip()
            metodo_rca = st.text_input("Método RCA", value=defaults.get("metodo_rca", "")).strip()
            acciones_rca = st.text_area(
                "Acciones Derivadas del RCA",
                value=defaults.get("acciones_rca", ""),
            ).strip()
            usuario_rca = st.text_input(
                "Usuario Responsable del RCA",
                value=defaults.get("usuario_rca", ""),
            ).strip()
        else:
            causa_raiz = metodo_rca = acciones_rca = usuario_rca = ""

        responsable = st.text_input(
            "Responsable de la Reparación",
            value=defaults.get("responsable", ""),
        ).strip()
        tipo_ejecucion = st.radio(
            "¿Quién ejecutó la tarea?",
            ["Interno", "Externo"],
            index=0 if not proveedor_default else 1,
            horizontal=True,
        )

        if tipo_ejecucion == "Externo" and proveedores:
            proveedor_externo = st.selectbox(
                "Proveedor Externo (si aplica)",
                proveedores,
                index=index_proveedor,
            )
        elif tipo_ejecucion == "Externo":
            proveedor_externo = st.text_input("Proveedor externo").strip()
        else:
            proveedor_externo = ""

        estados = ["Abierta", "En proceso", "Cerrada"]
        estado = st.selectbox(
            "Estado",
            estados,
            index=estados.index(defaults.get("estado")) if defaults.get("estado") in estados else 0,
        )
        usuario = st.text_input(
            "Usuario que registra",
            value=defaults.get("usuario_registro", ""),
        ).strip()
        observaciones = st.text_area(
            "Observaciones adicionales",
            value=defaults.get("observaciones", ""),
        ).strip()
        submit = st.form_submit_button("Guardar Tarea")

    if submit:
        if not id_activo:
            st.error("Debes indicar el ID del activo técnico para asegurar trazabilidad.")
            return None
        if not responsable or not usuario:
            st.error("Debe completar los campos obligatorios: Responsable y Usuario.")
            return None

        fecha_evento_dt = datetime.combine(fecha_evento_valor, datetime.min.time())
        return {
            "id_tarea": id_tarea,
            "id_activo_tecnico": id_activo,
            "fecha_evento": fecha_evento_dt,
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
            "fecha_registro": _to_datetime(defaults.get("fecha_registro")),
            "incompleto": False,
        }
    return None

def app():
    database = get_db()
    if database is None:
        st.error("MongoDB no disponible")
        return

    repository = CMMSRepository("tareas_correctivas", database=database)
    coleccion = repository.collection

    st.title("🛠️ Gestión de Tareas Correctivas")
    menu = ["Registrar Falla", "Ver Tareas", "Editar Tarea", "Eliminar Tarea"]
    choice = st.sidebar.radio("Acción", menu)

    if choice == "Registrar Falla":
        container = shared_section(
            "➕ Nueva Tarea Correctiva",
            "Registra correctivos y garantiza que queden trazados en historial.",
        )
        with container:
            data = form_tarea(database)
            if data:
                try:
                    repository.insert_with_log(
                        data,
                        event=HistorialEvent(
                            tipo_evento="Alta de tarea correctiva",
                            descripcion=f"Tarea registrada por falla: {data['descripcion_falla'][:120]}",
                            usuario=data["usuario_registro"],
                            id_origen=data.get("id_tarea"),
                            proveedor_externo=data.get("proveedor_externo") or None,
                            observaciones=data.get("observaciones") or None,
                        ),
                    )
                except ValueError as exc:
                    st.error(str(exc))
                else:
                    st.success("Tarea correctiva registrada correctamente.")
        st.divider()

    elif choice == "Ver Tareas":
        container = shared_section(
            "📋 Tareas Correctivas por Activo Técnico",
            "Filtra por estado o texto libre para auditar acciones correctivas.",
        )
        with container:
            mostrar_incompletas = st.checkbox("🔧 Mostrar solo tareas incompletas")
            query_base: Dict[str, Any] = {"incompleto": True} if mostrar_incompletas else {}
            tareas = list(coleccion.find(query_base).sort("fecha_evento", -1))

            if not tareas:
                st.info("No hay tareas registradas.")
            else:
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
                    df = pd.DataFrame(
                        [
                            {
                                "ID tarea": t.get("id_tarea"),
                                "Activo": t.get("id_activo_tecnico"),
                                "Estado": t.get("estado"),
                                "Descripción": t.get("descripcion_falla"),
                                "Fecha evento": t.get("fecha_evento"),
                                "Responsable": t.get("responsable"),
                            }
                            for t in filtradas
                        ]
                    )
                    st.dataframe(df, use_container_width=True)
        st.divider()

    elif choice == "Editar Tarea":
        container = shared_section(
            "✏️ Editar Tarea Correctiva",
            "Actualiza los correctivos y deja constancia en el historial.",
        )
        with container:
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
                    nuevos_datos = form_tarea(database, defaults=datos)
                    if nuevos_datos:
                        try:
                            repository.update_with_log(
                                {"_id": datos["_id"]},
                                nuevos_datos,
                                event=HistorialEvent(
                                    tipo_evento="Edición de tarea correctiva",
                                    descripcion=f"Tarea editada: {nuevos_datos['descripcion_falla'][:120]}",
                                    usuario=nuevos_datos["usuario_registro"],
                                    id_origen=nuevos_datos.get("id_tarea"),
                                    proveedor_externo=nuevos_datos.get("proveedor_externo") or None,
                                    observaciones=nuevos_datos.get("observaciones") or None,
                                ),
                            )
                        except ValueError as exc:
                            st.error(str(exc))
                        except LookupError:
                            st.error("No se encontró la tarea seleccionada. Actualice la vista.")
                        else:
                            st.success("Tarea actualizada correctamente.")
            else:
                st.info("No hay tareas disponibles para editar.")
        st.divider()

    elif choice == "Eliminar Tarea":
        container = shared_section(
            "🗑️ Eliminar Tarea Correctiva",
            "Confirma la eliminación registrando el usuario responsable.",
        )
        with container:
            tareas = list(coleccion.find())
            opciones = {
                f"{t.get('id_tarea', '❌')} | {t.get('id_activo_tecnico', '⛔')} - {t.get('descripcion_falla', '')[:30]}": t
                for t in tareas
            }

            if opciones:
                seleccion = st.selectbox("Seleccionar tarea", list(opciones.keys()))
                datos = opciones.get(seleccion)
                usuario_confirma = st.text_input("Usuario que confirma la eliminación").strip()
                if datos and st.button("Eliminar definitivamente", type="primary"):
                    if not usuario_confirma:
                        st.error("Debe indicar el usuario que confirma la eliminación.")
                    else:
                        try:
                            repository.delete_with_log(
                                {"_id": datos["_id"]},
                                event=HistorialEvent(
                                    tipo_evento="Baja de tarea correctiva",
                                    descripcion=f"Se eliminó tarea: {datos.get('descripcion_falla', '')[:120]}",
                                    usuario=usuario_confirma,
                                    id_origen=datos.get("id_tarea"),
                                    proveedor_externo=datos.get("proveedor_externo") or None,
                                    observaciones=datos.get("observaciones") or None,
                                ),
                                document=datos,
                            )
                        except ValueError as exc:
                            st.error(str(exc))
                        else:
                            st.success("Tarea eliminada. Refrescá la vista para confirmar.")
            else:
                st.info("No hay tareas disponibles para eliminar.")
        st.divider()

if __name__ == "__main__":
    app()
