"""
🗓️ CRUD de Planes Preventivos – CMMS Fábrica

Este módulo permite registrar, visualizar, editar y eliminar planes preventivos asociados a activos técnicos.
Cada acción se registra en la colección `historial` para trazabilidad operativa y auditorías.

✅ Normas aplicables:
- ISO 55001 (Gestión del ciclo de vida del activo)
- ISO 9001:2015 (Planificación y control operacional)
- ISO 14224 (Estructura y datos de mantenimiento)
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


def crear_plan_preventivo(data: dict, database=db):
    """Inserta un plan preventivo y registra el evento."""
    if database is None:
        return None
    coleccion = database["planes_preventivos"]
    coleccion.insert_one(data)
    registrar_evento_historial(
        "Alta de plan preventivo",
        data["id_activo_tecnico"],
        data["id_plan"],
        f"Alta de plan para activo: {data['id_activo_tecnico']}",
        data["usuario_registro"],
    )
    return data["id_plan"]

def generar_id_plan():
    return f"PP-{int(datetime.now().timestamp())}"

def app():
    if db is None:
        st.error("MongoDB no disponible")
        return
    coleccion = db["planes_preventivos"]

    st.title("🗓️ Gestión de Planes Preventivos")
    menu = ["Registrar Plan", "Ver Planes", "Editar Plan", "Eliminar Plan"]
    choice = st.sidebar.radio("Acción", menu)

    def form_plan(defaults=None):
        with st.form("form_plan_preventivo"):
            id_plan = st.text_input("ID del Plan", value=defaults.get("id_plan") if defaults else generar_id_plan())

            activos_lista = list(db["activos_tecnicos"].find({}, {"_id": 0, "id_activo_tecnico": 1, "nombre": 1}))
            opciones = [f"{a['id_activo_tecnico']} – {a.get('nombre', 'Sin nombre')}" for a in activos_lista]
            map_id = {f"{a['id_activo_tecnico']} – {a.get('nombre', 'Sin nombre')}": a["id_activo_tecnico"] for a in activos_lista}

            default_id = defaults.get("id_activo_tecnico") if defaults else None
            default_label = next((k for k, v in map_id.items() if v == default_id), opciones[0] if opciones else "")
            index_default = opciones.index(default_label) if default_label in opciones else 0

            id_activo = st.selectbox("Activo Técnico asociado", opciones, index=index_default)
            id_activo_tecnico = map_id.get(id_activo)

            frecuencia = st.number_input("Frecuencia", min_value=1, value=defaults.get("frecuencia") if defaults else 1)
            unidad_frecuencia = st.selectbox("Unidad", ["días", "semanas", "meses"], index=["días", "semanas", "meses"].index(defaults.get("unidad_frecuencia")) if defaults else 0)
            proxima_fecha = st.date_input("Próxima Ejecución", value=datetime.strptime(defaults.get("proxima_fecha"), "%Y-%m-%d") if defaults and defaults.get("proxima_fecha") else datetime.today())
            ultima_fecha = st.date_input("Última Ejecución", value=datetime.strptime(defaults.get("ultima_fecha"), "%Y-%m-%d") if defaults and defaults.get("ultima_fecha") else datetime.today())
            responsable = st.text_input("Responsable", value=defaults.get("responsable") if defaults else "")

            tipo_ejecucion = st.radio("¿Quién ejecuta la tarea preventiva?", ["Interno", "Externo"],
                                      index=0 if defaults is None or defaults.get("proveedor_externo") in [None, ""] else 1)

            nombres_proveedores = select_proveedores_externos(db)
            proveedor_default = defaults.get("proveedor_externo") if defaults else None
            index_proveedor = nombres_proveedores.index(proveedor_default) if proveedor_default in nombres_proveedores else 0 if nombres_proveedores else -1

            if tipo_ejecucion == "Externo":
                proveedor_externo = st.selectbox("Proveedor Externo", nombres_proveedores, index=index_proveedor) if nombres_proveedores else ""
            else:
                proveedor_externo = ""

            estado = st.selectbox("Estado", ["Activo", "Suspendido", "Finalizado"],
                                  index=["Activo", "Suspendido", "Finalizado"].index(defaults.get("estado")) if defaults else 0)

            adjunto_plan = st.text_input("Documento o Link del Plan", value=defaults.get("adjunto_plan") if defaults else "")
            usuario = st.text_input("Usuario que registra", value=defaults.get("usuario_registro") if defaults else "")
            observaciones = st.text_area("Observaciones", value=defaults.get("observaciones") if defaults else "")
            submit = st.form_submit_button("Guardar")

        if submit:
            if not responsable or not usuario:
                st.error("Debe completar los campos obligatorios: Responsable y Usuario.")
                return None

            return {
                "id_plan": id_plan,
                "id_activo_tecnico": id_activo_tecnico,
                "frecuencia": frecuencia,
                "unidad_frecuencia": unidad_frecuencia,
                "proxima_fecha": str(proxima_fecha),
                "ultima_fecha": str(ultima_fecha),
                "responsable": responsable,
                "proveedor_externo": proveedor_externo,
                "estado": estado,
                "adjunto_plan": adjunto_plan,
                "usuario_registro": usuario,
                "observaciones": observaciones,
                "fecha_registro": datetime.now()
            }
        return None

    if choice == "Registrar Plan":
        st.subheader("➕ Alta de Plan Preventivo")
        data = form_plan()
        if data:
            crear_plan_preventivo(data, db)
            st.success("✅ Plan preventivo registrado correctamente.")

    elif choice == "Ver Planes":
        st.subheader("📋 Planes Preventivos Registrados")
        planes = list(coleccion.find().sort("proxima_fecha", 1))
        if not planes:
            st.info("No hay planes cargados.")
            return

        estados = sorted({p.get("estado", "⛔ Sin Estado") for p in planes})
        estado_filtro = st.selectbox("Filtrar por estado", ["Todos"] + estados)
        query = st.text_input("🔍 Buscar por ID o activo")

        filtrados = []
        for p in planes:
            coincide_estado = estado_filtro == "Todos" or p.get("estado") == estado_filtro
            coincide_texto = (
                query.lower() in p.get("id_plan", "").lower()
                or query.lower() in p.get("id_activo_tecnico", "").lower()
            )
            if coincide_estado and coincide_texto:
                filtrados.append(p)

        if not filtrados:
            st.warning("No se encontraron registros con esos filtros.")
        else:
            agrupados = {}
            for p in filtrados:
                act = p.get("id_activo_tecnico", "⛔ Sin Activo")
                agrupados.setdefault(act, []).append(p)

            for act, lista in sorted(agrupados.items()):
                st.markdown(
                    f"<h4 style='text-align: left; margin-bottom: 0.5em;'>🔹 {act}</h4>",
                    unsafe_allow_html=True,
                )
                for p in lista:
                    st.code(f"ID del Plan: {p.get('id_plan', '')}", language="yaml")
                    freq = f"{p.get('frecuencia')} {p.get('unidad_frecuencia')}"
                    st.markdown(
                        f"- **{freq}** (Próxima: {p.get('proxima_fecha', '-')}, Estado: {p.get('estado', '-')})"
                    )

    elif choice == "Editar Plan":
        st.subheader("✏️ Editar Plan Preventivo")
        planes = list(coleccion.find())
        opciones = {
            f"{p['id_plan']} | {p['id_activo_tecnico']}": p for p in planes
        }
        if opciones:
            seleccion = st.selectbox("Seleccionar plan", list(opciones.keys()))
            datos = opciones.get(seleccion)
            if datos:
                nuevos_datos = form_plan(defaults=datos)
                if nuevos_datos:
                    coleccion.update_one({"_id": datos["_id"]}, {"$set": nuevos_datos})
                    registrar_evento_historial(
                        "Edición de plan preventivo",
                        nuevos_datos["id_activo_tecnico"],
                        nuevos_datos["id_plan"],
                        f"Edición de plan para activo: {nuevos_datos['id_activo_tecnico']}",
                        nuevos_datos["usuario_registro"]
                    )
                    st.success("✅ Plan actualizado correctamente.")
        else:
            st.info("No hay planes para editar.")

    elif choice == "Eliminar Plan":
        st.subheader("🗑️ Eliminar Plan Preventivo")
        planes = list(coleccion.find())
        opciones = {
            f"{p['id_plan']} | {p['id_activo_tecnico']}": p for p in planes
        }
        if opciones:
            seleccion = st.selectbox("Seleccionar plan", list(opciones.keys()))
            datos = opciones.get(seleccion)
            if datos and st.button("Eliminar definitivamente"):
                coleccion.delete_one({"_id": datos["_id"]})
                registrar_evento_historial(
                    "Baja de plan preventivo",
                    datos["id_activo_tecnico"],
                    datos["id_plan"],
                    f"Eliminación del plan asociado al activo: {datos['id_activo_tecnico']}",
                    datos["usuario_registro"]
                )
                st.success("🗑️ Plan eliminado correctamente.")
        else:
            st.info("No hay planes para eliminar.")

if __name__ == "__main__":
    app()
