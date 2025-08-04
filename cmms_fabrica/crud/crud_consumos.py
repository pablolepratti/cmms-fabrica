"""
⚡ CRUD de Consumos Técnicos – CMMS Fábrica

Este módulo permite registrar, visualizar, editar y eliminar consumos técnicos
(energía, agua y horas de compresores). Cada acción se registra en la
colección ``historial`` para asegurar trazabilidad conforme a ISO 9001.
"""

from datetime import datetime, timedelta
import pandas as pd
import streamlit as st

from modulos.conexion_mongo import db
from modulos.estilos import aplicar_estilos
from crud.generador_historial import registrar_evento_historial

TIPOS_CONSUMO = ["UTE", "OSE", "Schulz SRP 3040", "Atlas Copco GX7"]
UNIDADES = ["kWh", "m³", "h"]


def generar_id_consumo() -> str:
    """Genera un identificador único para un consumo."""
    return f"CON-{int(datetime.now().timestamp())}"


def form_consumo(usuario: str, defaults: dict | None = None) -> dict | None:
    """Formulario para crear o editar un consumo."""
    hoy = datetime.today().date()
    tipo_idx = (
        TIPOS_CONSUMO.index(defaults.get("tipo_consumo"))
        if defaults and defaults.get("tipo_consumo") in TIPOS_CONSUMO
        else 0
    )
    unidad_idx = (
        UNIDADES.index(defaults.get("unidad"))
        if defaults and defaults.get("unidad") in UNIDADES
        else 0
    )
    fecha_default = (
        datetime.strptime(defaults.get("fecha"), "%Y-%m-%d").date()
        if defaults and defaults.get("fecha")
        else hoy
    )
    valor_default = float(defaults.get("valor", 0)) if defaults else 0.0
    fuente_default = defaults.get("fuente", "") if defaults else ""
    obs_default = defaults.get("observaciones", "") if defaults else ""

    with st.form("form_consumo"):
        tipo_consumo = st.selectbox("Tipo de consumo", TIPOS_CONSUMO, index=tipo_idx)
        fecha = st.date_input("Fecha", value=fecha_default)
        valor = st.number_input("Valor", value=valor_default, step=0.01)
        unidad = st.selectbox("Unidad", UNIDADES, index=unidad_idx)
        fuente = st.text_input("Fuente", value=fuente_default)
        observaciones = st.text_area("Observaciones", value=obs_default)
        submit = st.form_submit_button("Guardar")

    if submit:
        return {
            "id_consumo": defaults.get("id_consumo") if defaults else generar_id_consumo(),
            "fecha": str(fecha),
            "tipo_consumo": tipo_consumo,
            "valor": float(valor),
            "unidad": unidad,
            "fuente": fuente,
            "observaciones": observaciones,
            "usuario_registro": usuario,
        }
    return None


def app(database=db, usuario: str = ""):
    """Punto de entrada principal del CRUD de consumos."""
    aplicar_estilos()
    if database is None:
        st.error("MongoDB no disponible")
        return
    coleccion = database["consumos"]

    st.title("⚡ Gestión de Consumos Técnicos")
    menu = ["Registrar", "Ver", "Editar", "Eliminar"]
    choice = st.sidebar.radio("Acción", menu)

    if choice == "Registrar":
        st.subheader("➕ Registrar nuevo consumo")
        data = form_consumo(usuario)
        if data:
            coleccion.insert_one(data)
            registrar_evento_historial(
                "consumo",
                None,
                f"Se registró consumo de {data['tipo_consumo']}: {data['valor']} {data['unidad']}",
                data["usuario_registro"],
                id_origen=data["id_consumo"],
            )
            st.success("Consumo registrado correctamente.")

    elif choice == "Ver":
        st.subheader("📋 Registros de Consumo")
        consumos = list(coleccion.find().sort("fecha", -1))
        if not consumos:
            st.info("No hay consumos registrados.")
            return

        tipos = sorted({c.get("tipo_consumo", "") for c in consumos})
        tipo_filtro = st.selectbox("Filtrar por tipo", ["Todos"] + tipos)
        col1, col2 = st.columns(2)
        with col1:
            fecha_desde = st.date_input("Desde", value=datetime.today().date() - timedelta(days=30))
        with col2:
            fecha_hasta = st.date_input("Hasta", value=datetime.today().date())

        filtrados = []
        for c in consumos:
            fecha_c = datetime.strptime(c.get("fecha"), "%Y-%m-%d").date()
            coincide_tipo = tipo_filtro == "Todos" or c.get("tipo_consumo") == tipo_filtro
            coincide_fecha = fecha_desde <= fecha_c <= fecha_hasta
            if coincide_tipo and coincide_fecha:
                filtrados.append(c)

        if filtrados:
            df = pd.DataFrame(filtrados)
            df = df[
                [
                    "id_consumo",
                    "fecha",
                    "tipo_consumo",
                    "valor",
                    "unidad",
                    "fuente",
                    "observaciones",
                    "usuario_registro",
                ]
            ]
            st.dataframe(df)
        else:
            st.warning("No se encontraron registros con esos filtros.")

        # KPIs de consumo
        df_all = pd.DataFrame(consumos)
        df_all["fecha"] = pd.to_datetime(df_all["fecha"])
        hoy = datetime.today()
        df_30 = df_all[df_all["fecha"] >= hoy - timedelta(days=30)]
        df_12 = df_all[df_all["fecha"] >= hoy - timedelta(days=365)]

        daily = (
            df_30.groupby(["tipo_consumo", df_30["fecha"].dt.date])["valor"].sum().reset_index()
        )
        daily_avg = daily.groupby("tipo_consumo")["valor"].mean()

        monthly = (
            df_12.groupby(["tipo_consumo", df_12["fecha"].dt.to_period("M")])["valor"]
            .sum()
            .reset_index()
        )
        monthly_avg = monthly.groupby("tipo_consumo")["valor"].mean()

        st.subheader("📈 KPIs de Consumo")
        for tipo in tipos:
            unidad = (
                df_all[df_all["tipo_consumo"] == tipo]["unidad"].mode()[0]
                if not df_all[df_all["tipo_consumo"] == tipo].empty
                else ""
            )
            col1, col2 = st.columns(2)
            daily_val = daily_avg.get(tipo, float("nan"))
            monthly_val = monthly_avg.get(tipo, float("nan"))
            col1.metric(
                f"{tipo} – Promedio diario",
                f"{daily_val:.2f} {unidad}" if pd.notna(daily_val) else "N/A",
            )
            col2.metric(
                f"{tipo} – Promedio mensual",
                f"{monthly_val:.2f} {unidad}" if pd.notna(monthly_val) else "N/A",
            )

    elif choice == "Editar":
        st.subheader("✏️ Editar consumo")
        consumos = list(coleccion.find())
        opciones = {
            f"{c['id_consumo']} - {c['tipo_consumo']} ({c['fecha']})": c for c in consumos
        }
        if not opciones:
            st.info("No hay consumos para editar.")
            return
        seleccion = st.selectbox("Seleccionar consumo", list(opciones.keys()))
        datos = opciones[seleccion]
        nuevos_datos = form_consumo(usuario, defaults=datos)
        if nuevos_datos:
            coleccion.update_one({"_id": datos["_id"]}, {"$set": nuevos_datos})
            registrar_evento_historial(
                "consumo",
                None,
                f"Se editó consumo de {nuevos_datos['tipo_consumo']}: {nuevos_datos['valor']} {nuevos_datos['unidad']}",
                usuario,
                id_origen=nuevos_datos["id_consumo"],
            )
            st.success("Consumo actualizado correctamente.")

    elif choice == "Eliminar":
        st.subheader("🗑️ Eliminar consumo")
        consumos = list(coleccion.find())
        opciones = {
            f"{c['id_consumo']} - {c['tipo_consumo']} ({c['fecha']})": c for c in consumos
        }
        if not opciones:
            st.info("No hay consumos para eliminar.")
            return
        seleccion = st.selectbox("Seleccionar consumo", list(opciones.keys()))
        datos = opciones[seleccion]
        if st.button("Eliminar definitivamente"):
            coleccion.delete_one({"_id": datos["_id"]})
            registrar_evento_historial(
                "consumo",
                None,
                f"Se eliminó consumo {datos['id_consumo']}",
                usuario,
                id_origen=datos["id_consumo"],
            )
            st.success("Consumo eliminado. Actualizá la vista para confirmar.")

