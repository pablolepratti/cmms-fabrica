"""
📄 Módulo de Reportes Técnicos – CMMS Fábrica

Este módulo permite consultar y exportar reportes en PDF a partir de la colección `historial`.
Filtrado por tipo de evento y rango de fechas.

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

coleccion = db["historial"]

# 🧾 Clase PDF simplificada
class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, "📄 Reporte de Eventos Técnicos", ln=True, align="C")
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
                self.cell(38, 8, str(val)[:18], border=1)
            self.ln()

def generar_pdf(df, nombre):
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.chapter_title(f"Reporte generado el {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    pdf.chapter_body(df)
    os.makedirs("reportes", exist_ok=True)
    ruta = f"reportes/reporte_{nombre.lower().replace(' ', '_')}.pdf"
    pdf.output(ruta)
    return ruta

def app():
    st.title("📄 Reportes Técnicos del CMMS")

    with st.sidebar:
        st.markdown("### 📅 Filtros")
        fecha_desde = st.date_input("Desde", value=date(2024, 1, 1))
        fecha_hasta = st.date_input("Hasta", value=date.today())
        tipo_evento = st.multiselect("Tipo de Evento", ["preventiva", "correctiva", "tecnica", "observacion", "calibracion"],
                                     default=["preventiva", "correctiva", "tecnica", "observacion", "calibracion"])

    if fecha_desde > fecha_hasta:
        st.error("⚠️ La fecha 'desde' no puede ser posterior a la fecha 'hasta'.")
        return

    query = {
        "fecha_evento": {
            "$gte": datetime.combine(fecha_desde, datetime.min.time()),
            "$lte": datetime.combine(fecha_hasta, datetime.max.time())
        },
        "tipo_evento": {"$in": tipo_evento}
    }

    datos = list(coleccion.find(query, {"_id": 0}))
    if not datos:
        st.warning("No se encontraron datos para ese período.")
        return

    df = pd.DataFrame(datos)
    df["fecha_evento"] = pd.to_datetime(df["fecha_evento"])
    columnas = ["fecha_evento", "tipo_evento", "id_activo_tecnico", "descripcion", "usuario_registro"]
    st.dataframe(df[columnas].sort_values("fecha_evento", ascending=False), use_container_width=True)

    if st.button("📄 Generar PDF del reporte"):
        archivo = generar_pdf(df[columnas], "historial")
        with open(archivo, "rb") as f:
            st.download_button(
                label="⬇️ Descargar PDF",
                data=f,
                file_name=archivo.split("/")[-1],
                mime="application/pdf"
            )

if __name__ == "__main__":
    app()
