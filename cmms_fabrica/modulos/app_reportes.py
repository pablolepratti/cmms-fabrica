"""
📄 Módulo de Reportes Técnicos – CMMS Fábrica

Este módulo permite consultar y exportar reportes en PDF y Excel a partir de la colección `historial`.
Filtrado por tipo de evento, rango de fechas y activo técnico.

✅ Normas aplicables:
- ISO 9001:2015 (Trazabilidad documental y registros)
- ISO 55001 (Control de mantenimiento y soporte documental)
"""

import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime, date
from .conexion_mongo import db
import os
from io import BytesIO

coleccion = db["historial"] if db is not None else None
activos_tecnicos = db["activos_tecnicos"] if db is not None else None

# 📄 Clase PDF con descripciones legibles
class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, "Reporte de Eventos Técnicos", ln=True, align="C")
        self.ln(5)

    def chapter_body(self, df):
        self.set_font("Arial", "", 10)
        for _, row in df.iterrows():
            self.multi_cell(0, 6, f"Fecha: {row['fecha_evento'].strftime('%Y-%m-%d')}", 0)
            self.multi_cell(0, 6, f"Tipo de evento: {row['tipo_evento']}", 0)
            self.multi_cell(0, 6, f"Activo: {row['id_activo_tecnico']}", 0)
            self.multi_cell(0, 6, f"Usuario: {row['usuario_registro']}", 0)
            self.set_font("Arial", "B", 10)
            self.multi_cell(0, 6, "Descripción:", 0)
            self.set_font("Arial", "", 10)
            self.multi_cell(0, 6, f"{row.get('descripcion', '-')}", 0)
            self.set_font("Arial", "B", 10)
            self.multi_cell(0, 6, "Observaciones:", 0)
            self.set_font("Arial", "", 10)
            self.multi_cell(0, 6, f"{row.get('observaciones', '-')}", 0)
            self.ln(5)

def generar_pdf(df, nombre):
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.chapter_body(df)
    os.makedirs("reportes", exist_ok=True)
    ruta = f"reportes/reporte_{nombre.lower().replace(' ', '_')}.pdf"
    pdf.output(ruta)
    return ruta

def generar_excel(df, nombre):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name="Historial", index=False)
    output.seek(0)
    return output


def filtrar_ultimo_por_activo(df: pd.DataFrame, key: str = "id_origen") -> pd.DataFrame:
    """Devuelve el registro m\u00e1s reciente agrupado por ``key``.

    Por defecto se utiliza ``id_origen`` para mostrar solo la \u00faltima
    actualizaci\u00f3n de cada evento, mejorando la trazabilidad seg\u00fan las
    directrices de ISO 9001:2015.
    """
    if key not in df.columns or "fecha_evento" not in df.columns:
        return df
    ordenado = df.sort_values("fecha_evento", ascending=False)
    idx = ordenado.groupby(key)["fecha_evento"].idxmax()
    return ordenado.loc[idx].reset_index(drop=True)

def app():
    st.title("📄 Reportes Técnicos del CMMS")

    with st.sidebar:
        st.markdown("### 📅 Filtros")
        fecha_desde = st.date_input("Desde", value=date(2024, 1, 1))
        fecha_hasta = st.date_input("Hasta", value=date.today())
        tipo_evento = st.multiselect("Tipo de Evento", ["preventiva", "correctiva", "tecnica", "observacion", "calibracion"],
                                     default=["preventiva", "correctiva", "tecnica", "observacion", "calibracion"])

        activos = list(activos_tecnicos.find({}, {"_id": 0, "id_activo_tecnico": 1, "pertenece_a": 1}))
        opciones = ["Todos"] + sorted([
            f"{a['id_activo_tecnico']} (pertenece a {a['pertenece_a']})" if a.get("pertenece_a") else a["id_activo_tecnico"]
            for a in activos
        ])
        seleccion = st.selectbox("Activo Técnico (con subactivos)", opciones)
        id_activo = seleccion.split(" ")[0] if seleccion != "Todos" else None

    if fecha_desde > fecha_hasta:
        st.error("⚠️ La fecha 'desde' no puede ser posterior a la fecha 'hasta'.")
        return

    # Filtrado por fecha_evento según la definición en docs/estructura_sistema.md
    # (sección "Timestamps")
    query = {
        "fecha_evento": {
            "$gte": datetime.combine(fecha_desde, datetime.min.time()),
            "$lte": datetime.combine(fecha_hasta, datetime.max.time())
        },
        "tipo_evento": {"$in": tipo_evento}
    }

    if id_activo:
        subactivos = [a["id_activo_tecnico"] for a in activos if a.get("pertenece_a") == id_activo]
        ids_filtrados = [id_activo] + subactivos
        query["id_activo_tecnico"] = {"$in": ids_filtrados}
        st.sidebar.success(f"Incluyendo {len(subactivos)} subactivo(s) de '{id_activo}'")

    datos = list(coleccion.find(query, {"_id": 0}))
    if not datos:
        st.warning("No se encontraron datos para ese período.")
        return

    df = pd.DataFrame(datos)
    df["fecha_evento"] = pd.to_datetime(df["fecha_evento"])
    if "usuario_registro" not in df.columns and "usuario" in df.columns:
        df["usuario_registro"] = df["usuario"]
    elif "usuario_registro" not in df.columns:
        df["usuario_registro"] = "desconocido"
    if "observaciones" not in df.columns:
        df["observaciones"] = "-"

    df = filtrar_ultimo_por_activo(df)

    columnas = ["fecha_evento", "tipo_evento", "id_activo_tecnico", "descripcion", "observaciones", "usuario_registro"]

    st.markdown("### 📊 Vista Previa del Reporte")
    st.dataframe(df[columnas].sort_values("fecha_evento", ascending=False), use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("📄 Generar PDF del reporte"):
            nombre_base = id_activo if id_activo else "historial"
            df_clean = df[columnas].applymap(lambda x: str(x).encode('ascii', 'ignore').decode('ascii') if isinstance(x, str) else x)
            archivo = generar_pdf(df_clean, nombre_base)
            with open(archivo, "rb") as f:
                st.download_button(
                    label="⬇️ Descargar PDF",
                    data=f,
                    file_name=os.path.basename(archivo),
                    mime="application/pdf"
                )

    with col2:
        if st.button("📥 Descargar Excel del reporte"):
            nombre_base = id_activo if id_activo else "historial"
            excel_buffer = generar_excel(df[columnas], nombre_base)
            st.download_button(
                label="⬇️ Descargar Excel",
                data=excel_buffer,
                file_name=f"reporte_{nombre_base}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

if __name__ == "__main__":
    app()
