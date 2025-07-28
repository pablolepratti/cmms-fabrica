"""
📄 CRUD de Calibraciones de Instrumentos – CMMS Fábrica

Normas aplicables: ISO/IEC 17025 | ISO 9001:2015 | ISO 55001

Descripción: Permite registrar, visualizar, editar y eliminar eventos de calibración con trazabilidad completa y alertas por vencimiento.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from modulos.conexion_mongo import db
from crud.generador_historial import registrar_evento_historial
from modulos.utilidades_formularios import (
    select_activo_tecnico,
    select_proveedores_externos,
)


def crear_calibracion(data: dict, database=db):
    """Inserta un registro de calibración y registra el evento."""
    if database is None:
        return None
    coleccion = database["calibraciones"]
    coleccion.insert_one(data)
    registrar_evento_historial(
        "Alta de calibración",
        data["id_activo_tecnico"],
        data["id_calibracion"],
        f"Calibración registrada para {data['id_activo_tecnico']}",
        data["usuario_registro"],
    )
    return data["id_calibracion"]



def generar_id_calibracion():
    return f"CAL-{int(datetime.now().timestamp())}"

def form_calibracion(defaults=None):
    ids_activos = select_activo_tecnico(db)
    nombres_proveedores = select_proveedores_externos(db)

    if not ids_activos:
        st.warning("⚠️ No hay activos técnicos registrados.")
        return None

    with st.form("form_calibracion"):
        id_default = defaults.get("id_activo_tecnico") if defaults else ""
        index_default = ids_activos.index(id_default) if id_default in ids_activos else 0
        id_activo = st.selectbox("ID del Instrumento", ids_activos, index=index_default)

        id_calibracion = defaults.get("id_calibracion") if defaults else generar_id_calibracion()
        fecha_val = defaults.get("fecha_calibracion") if defaults else None
        fecha_cal = st.date_input("Fecha de Calibración", value=datetime.strptime(fecha_val, "%Y-%m-%d") if fecha_val else datetime.today())

        responsable = st.text_input("Responsable de Calibración", value=defaults.get("responsable") if defaults else "")

        proveedor_default = defaults.get("proveedor_externo") if defaults else ""
        usa_proveedor = st.checkbox("¿Participa un proveedor externo?", value=bool(proveedor_default))
        proveedor_externo = ""
        if usa_proveedor and nombres_proveedores:
            index_prov = nombres_proveedores.index(proveedor_default) if proveedor_default in nombres_proveedores else 0
            proveedor_externo = st.selectbox("Proveedor Externo", nombres_proveedores, index=index_prov)

        resultado_opciones = ["Correcta", "Desviación leve", "Desviación crítica"]
        resultado = st.selectbox("Resultado", resultado_opciones,
                                 index=resultado_opciones.index(defaults.get("resultado")) if defaults and defaults.get("resultado") in resultado_opciones else 0)

        acciones = st.text_area("Acciones Derivadas", value=defaults.get("acciones") if defaults else "")
        observaciones = st.text_area("Observaciones", value=defaults.get("observaciones") if defaults else "")

        prox_fecha = defaults.get("fecha_proxima") if defaults else None
        prox_valor = datetime.strptime(prox_fecha, "%Y-%m-%d") if prox_fecha else datetime.today() + timedelta(days=180)
        prox = st.date_input("Fecha Próxima Calibración", value=prox_valor)

        usuario = st.text_input("Usuario que registra", value=defaults.get("usuario_registro") if defaults else "")

        submit = st.form_submit_button("Guardar Calibración")

    if submit:
        if not responsable or not usuario:
            st.error("Debe completar los campos obligatorios: Responsable y Usuario.")
            return None
        if usa_proveedor and not proveedor_externo:
            st.error("Debe seleccionar un proveedor si se indica que es externo.")
            return None

        return {
            "id_calibracion": id_calibracion,
            "id_activo_tecnico": id_activo,
            "fecha_calibracion": str(fecha_cal),
            "fecha_proxima": str(prox),
            "responsable": responsable,
            "proveedor_externo": proveedor_externo if usa_proveedor else "",
            "resultado": resultado,
            "acciones": acciones,
            "observaciones": observaciones,
            "usuario_registro": usuario,
            "fecha_registro": datetime.now()
        }
    return None

def app():
    if db is None:
        st.error("MongoDB no disponible")
        return
    coleccion = db["calibraciones"]
    activos = db["activos_tecnicos"]
    proveedores = db["servicios_externos"]

    st.title("🧪 Gestión de Calibraciones de Instrumentos")
    menu = ["Registrar Calibración", "Ver Calibraciones", "Editar Calibración", "Eliminar Calibración"]
    choice = st.sidebar.radio("Acción", menu)

    if choice == "Registrar Calibración":
        st.subheader("➕ Nueva Calibración")
        data = form_calibracion()
        if data:
            crear_calibracion(data, db)
            st.success("✅ Calibración registrada correctamente.")

    elif choice == "Ver Calibraciones":
        st.subheader("📋 Calibraciones por Instrumento")
        registros = list(coleccion.find().sort("fecha_calibracion", -1))

        if not registros:
            st.info("No hay calibraciones registradas.")
            return

        df = pd.DataFrame(registros)
        df["fecha_proxima"] = pd.to_datetime(df["fecha_proxima"], errors="coerce")
        hoy = datetime.today()
        df_alerta = df[df["fecha_proxima"].notna() & (df["fecha_proxima"] <= hoy + timedelta(days=30))]

        st.markdown("### ⚠️ Calibraciones vencidas o próximas")
        if not df_alerta.empty:
            st.dataframe(
                df_alerta[["id_activo_tecnico", "fecha_proxima", "resultado", "observaciones"]],
                use_container_width=True,
            )
        else:
            st.success("Todas las calibraciones están al día ✅")

        activos = sorted({r.get("id_activo_tecnico", "⛔ Sin Activo") for r in registros})
        activo_filtro = st.selectbox("Filtrar por activo", ["Todos"] + activos)
        texto_filtro = st.text_input("🔍 Buscar por ID o resultado")

        filtrados = []
        for r in registros:
            coincide_activo = activo_filtro == "Todos" or r.get("id_activo_tecnico") == activo_filtro
            texto = (
                r.get("id_calibracion", "")
                + r.get("resultado", "")
                + r.get("observaciones", "")
            )
            coincide_texto = texto_filtro.lower() in texto.lower()
            if coincide_activo and coincide_texto:
                filtrados.append(r)

        if not filtrados:
            st.warning("No se encontraron registros con esos filtros.")
        else:
            agrupados = {}
            for r in filtrados:
                act = r.get("id_activo_tecnico", "⛔ Sin Activo")
                agrupados.setdefault(act, []).append(r)

            for act, lista in sorted(agrupados.items()):
                st.markdown(
                    f"<h4 style='text-align: left; margin-bottom: 0.5em;'>🔹 {act}</h4>",
                    unsafe_allow_html=True,
                )
                for r in lista:
                    st.code(f"ID Calibración: {r.get('id_calibracion', '')}", language="yaml")
                    st.markdown(
                        f"- **{r.get('resultado', '')}** ({r.get('fecha_calibracion', '')}) Próxima: {r.get('fecha_proxima', '-') }"
                    )

    elif choice == "Editar Calibración":
        st.subheader("✏️ Editar Calibración")
        registros = list(coleccion.find())
        opciones = {
            f"{r.get('id_calibracion', '❌')} | {r.get('id_activo_tecnico', 'Sin ID')} - {r.get('fecha_calibracion', 'Sin Fecha')}": r
            for r in registros
        }
        if not opciones:
            st.info("No hay calibraciones disponibles.")
            return
        seleccion = st.selectbox("Seleccionar calibración", list(opciones.keys()))
        datos = opciones[seleccion]
        nuevos = form_calibracion(defaults=datos)
        if nuevos:
            coleccion.update_one({"_id": datos["_id"]}, {"$set": nuevos})
            registrar_evento_historial(
                "Edición de calibración",
                nuevos["id_activo_tecnico"],
                nuevos["id_calibracion"],
                f"Edición de calibración ({nuevos['resultado']})",
                nuevos["usuario_registro"]
            )
            st.success("✅ Calibración actualizada correctamente.")

    elif choice == "Eliminar Calibración":
        st.subheader("🗑️ Eliminar Calibración")
        registros = list(coleccion.find())
        opciones = {
            f"{r.get('id_calibracion', '❌')} | {r.get('id_activo_tecnico', 'Sin ID')} - {r.get('fecha_calibracion', 'Sin Fecha')}": r
            for r in registros
        }
        if not opciones:
            st.info("No hay calibraciones disponibles.")
            return
        seleccion = st.selectbox("Seleccionar calibración", list(opciones.keys()))
        datos = opciones[seleccion]
        if st.button("Eliminar definitivamente"):
            coleccion.delete_one({"_id": datos["_id"]})
            registrar_evento_historial(
                "Baja de calibración",
                datos.get("id_activo_tecnico"),
                datos.get("id_calibracion"),
                f"Se eliminó calibración ({datos.get('resultado', '-')})",
                datos.get("usuario_registro", "desconocido")
            )
            st.success("🗑️ Calibración eliminada correctamente.")

if __name__ == "__main__":
    app()
