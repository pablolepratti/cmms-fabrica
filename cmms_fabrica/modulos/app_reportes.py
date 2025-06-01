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
from modulos.conexion_mongo import db
import os
from io import BytesIO

coleccion = db["historial"]
activos_tecnicos = db["activos_tecnicos"]

# 🧾 Clase PDF simplificada
class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, "Reporte de Eventos Técnicos", ln=True, align="C")
        self.ln(5)

    def chapter_title(self, title):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, title, ln=True)
        self.ln(2)

    def chapter_body(self, df):
        self.set_font("Arial", "B", 9)
        for col in df.columns[:5]:
            self.cell(38, 8, str(col)[:18], border=1)
        self.ln()

        self.set_font("Arial", "", 9)
        for _, row in df.iterrows():
            for val in row[:5]:
                clean_val = str(val).encode('ascii', 'ignore').decode('ascii')
                self.cell(38, 8, clean_val[:18], border=1)
            self.ln()

def generar_pdf(df, nombre):
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.chapter_title("Reporte generado el " + datetime.now().strftime("%Y-%m-%d %H:%M"))
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

def app():
    st.title("📄 Reportes Técnicos del CMMS")

    # Filtros
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

    # Construcción del query
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

    # Procesamiento de DataFrame
    df = pd.DataFrame(datos)
    df["fecha_evento"] = pd.to_datetime(df["fecha_evento"])
    if "usuario_registro" not in df.columns and "usuario" in df.columns:
        df["usuario_registro"] = df["usuario"]
    elif "usuario_registro" not in df.columns:
        df["usuario_registro"] = "desconocido"

    columnas = ["fecha_evento", "tipo_evento", "id_activo_tecnico", "descripcion", "usuario_registro"]

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
