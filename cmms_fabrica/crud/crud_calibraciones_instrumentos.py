"""
🧪 CRUD de Calibraciones de Instrumentos – CMMS Fábrica

Este módulo combina trazabilidad completa con seguimiento operativo.
Permite registrar, visualizar, editar y eliminar calibraciones, mostrando alertas por vencimientos y filtros por tipo/estado.

✅ Normas aplicables:
- ISO/IEC 17025 (Requisitos para laboratorios de calibración)
- ISO 9001:2015 (Control de equipos de medición y trazabilidad)
- ISO 55001 (Ciclo de vida de activos)
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from modulos.conexion_mongo import db
from crud.generador_historial import registrar_evento_historial
import time

coleccion = db["calibraciones"]
activos = db["activos_tecnicos"]

def generar_id_calibracion():
    return f"CAL-{int(datetime.now().timestamp())}"


def form_calibracion(defaults=None):
    ids_activos = [d["id_activo_tecnico"] for d in activos.find({}, {"_id": 0, "id_activo_tecnico": 1})]
    if not ids_activos:
        st.warning("⚠️ No hay activos técnicos registrados.")
        return None

    with st.form("form_calibracion"):
        id_activo = st.selectbox("ID del Instrumento", ids_activos,
                                 index=ids_activos.index(defaults["id_activo_tecnico"]) if defaults and defaults.get("id_activo_tecnico") in ids_activos else 0)
        id_calibracion = defaults.get("id_calibracion") if defaults else generar_id_calibracion()

        fecha_cal = st.date_input("Fecha de Calibración", value=defaults.get("fecha_calibracion") if defaults else datetime.today())
        responsable = st.text_input("Responsable de Calibración", value=defaults.get("responsable") if defaults else "")
        proveedor = st.text_input("Proveedor Externo (si aplica)", value=defaults.get("proveedor_externo") if defaults else "")
        resultado = st.selectbox("Resultado", ["Correcta", "Desviación leve", "Desviación crítica"],
                                 index=["Correcta", "Desviación leve", "Desviación crítica"].index(defaults.get("resultado")) if defaults else 0)
        acciones = st.text_area("Acciones Derivadas", value=defaults.get("acciones") if defaults else "")
        observaciones = st.text_area("Observaciones", value=defaults.get("observaciones") if defaults else "")
        prox = st.date_input("Fecha Próxima Calibración", value=defaults.get("fecha_proxima") if defaults else datetime.today() + timedelta(days=180))
        usuario = st.text_input("Usuario que registra", value=defaults.get("usuario_registro") if defaults else "")
        submit = st.form_submit_button("Guardar Calibración")

    if submit:
        return {
            "id_calibracion": id_calibracion,
            "id_activo_tecnico": id_activo,
            "fecha_calibracion": str(fecha_cal),
            "fecha_proxima": str(prox),
            "responsable": responsable,
            "proveedor_externo": proveedor,
            "resultado": resultado,
            "acciones": acciones,
            "observaciones": observaciones,
            "usuario_registro": usuario,
            "fecha_registro": datetime.now()
        }
    return None

def app():
    st.title("🧪 Gestión de Calibraciones de Instrumentos")

    datos = list(coleccion.find({}, {"_id": 0}))
    df = pd.DataFrame(datos)

    if not df.empty:
        df["fecha_proxima"] = pd.to_datetime(df.get("fecha_proxima"), errors='coerce')
        hoy = datetime.today()
        df_alerta = df[df["fecha_proxima"].notna() & (df["fecha_proxima"] <= hoy + timedelta(days=30))]

        st.markdown("### ⚠️ Calibraciones vencidas o próximas")
        if not df_alerta.empty:
            st.dataframe(df_alerta[["id_activo_tecnico", "fecha_proxima", "resultado", "observaciones"]])
        else:
            st.success("Todas las calibraciones están al día ✅")

    menu = ["Registrar Calibración", "Ver Calibraciones", "Editar Calibración", "Eliminar Calibración"]
    choice = st.sidebar.radio("Acción", menu)

    if choice == "Registrar Calibración":
        st.subheader("➕ Nueva Calibración")
        data = form_calibracion()
        if data:
            coleccion.insert_one(data)
            registrar_evento_historial(
                "Alta de calibración",
                data["id_activo_tecnico"],
                data["id_calibracion"],
                f"Calibración registrada con resultado '{data['resultado']}'",
                data["usuario_registro"],
            )
            st.success("Calibración registrada correctamente. Refrescar la página para ver los cambios.")

    elif choice == "Ver Calibraciones":
        st.subheader("📋 Calibraciones por Instrumento")
        registros = list(coleccion.find().sort("fecha_calibracion", -1))

        if not registros:
            st.info("No hay calibraciones registradas.")
            return

        df = pd.DataFrame(registros)
        texto = st.text_input("🔍 Buscar por ID, resultado o responsable")
        filtrado = df[df.apply(lambda x: texto.lower() in str(x.values).lower(), axis=1)] if texto else df

        for instrumento in sorted(filtrado["id_activo_tecnico"].unique()):
            st.markdown(f"### 🏷️ Instrumento: `{instrumento}`")
            for _, c in filtrado[filtrado["id_activo_tecnico"] == instrumento].iterrows():
                st.code(f"ID Calibración: {c.get('id_calibracion', '❌ No definido')}", language="yaml")
                st.markdown(f"- 📅 **{c['fecha_calibracion']}** | 🧪 **Resultado:** {c['resultado']} | 👤 **Responsable:** {c['responsable']}")
                st.write(c.get("observaciones", ""))
            st.markdown("---")

    elif choice == "Editar Calibración":
        st.subheader("✏️ Editar Calibración")
        registros = list(coleccion.find())
        opciones = {
            f"{r.get('id_calibracion', '❌')} | {r.get('id_activo_tecnico', 'Sin ID')} - {r.get('fecha_calibracion', 'Sin Fecha')}": r
            for r in registros
        }
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
                nuevos["usuario_registro"],
            )
            st.success("Calibración actualizada correctamente. Refrescar la página para ver los cambios.")

    elif choice == "Eliminar Calibración":
        st.subheader("🗑️ Eliminar Calibración")
        registros = list(coleccion.find())
        opciones = {
            f"{r.get('id_calibracion', '❌')} | {r.get('id_activo_tecnico', 'Sin ID')} - {r.get('fecha_calibracion', 'Sin Fecha')}": r
            for r in registros
        }
        seleccion = st.selectbox("Seleccionar calibración", list(opciones.keys()))
        datos = opciones[seleccion]
        if st.button("Eliminar definitivamente"):
            coleccion.delete_one({"_id": datos["_id"]})
            registrar_evento_historial(
                "Baja de calibración",
                datos.get("id_activo_tecnico"),
                datos.get("id_calibracion"),
                f"Se eliminó calibración ({datos.get('resultado', '-')})",
                datos.get("usuario_registro", "desconocido"),
            )
            st.success("Calibración eliminada. Refrescar la página para ver los cambios.")

if __name__ == "__main__":
    app()
