import streamlit as st
import pandas as pd
import os
from fpdf import FPDF
from datetime import datetime, date
from modulos.conexion_mongo import db

# 🔍 Colecciones disponibles para reporte
FUENTES = {
    "Tareas": db["tareas"],
    "Observaciones": db["observaciones"],
    "Servicios": db["servicios"],
    "Mantenimiento Preventivo": db["mantenimientos"],
    "Semana Laboral": db["plan_semana"],
    "Historial": db["historial"],
    "Calibraciones": db["calibraciones"],
    "Tareas Técnicas": db["tareas_tecnicas"]  # ⬅️ NUEVA
}

# 🕒 Mapeo automático del campo de fecha por colección
CAMPOS_FECHA = {
    "Tareas": "proxima_ejecucion",
    "Mantenimiento Preventivo": "proxima_ejecucion",
    "Semana Laboral": "fecha",
    "Observaciones": "fecha",
    "Servicios": "fecha",
    "Historial": "fecha",
    "Calibraciones": "fecha_inicio",
    "Tareas Técnicas": "fecha_inicio"
}

# 🧾 Clase para generar PDF
class PDF(FPDF):
    def header(self):
        try:
            self.image("logo_fabrica.png", x=10, y=8, w=30)
        except:
            pass
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, "Reporte del Sistema CMMS", ln=True, align="C")
        self.ln(10)

    def chapter_title(self, title):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, title, ln=True)
        self.ln(2)

    def chapter_body(self, df):
        self.set_font("Arial", "B", 9)
        for col in df.columns[:6]:
            self.cell(32, 8, str(col)[:15], border=1)
        self.ln()

        self.set_font("Arial", "", 9)
        for _, row in df.iterrows():
            for val in row[:6]:
                self.cell(32, 8, str(val)[:15], border=1)
            self.ln()

def generar_pdf(nombre_reporte, df):
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.chapter_title(f"Reporte: {nombre_reporte}")
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 10, f"Generado el: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True)
    pdf.ln(5)
    pdf.chapter_body(df)

    nombre_archivo = f"reporte_{nombre_reporte.lower().replace(' ', '_')}.pdf"
    path = os.path.join("reportes", nombre_archivo)
    os.makedirs("reportes", exist_ok=True)
    pdf.output(path)
    return path

def mostrar_reportes():
    st.subheader("📄 Reportes del Sistema CMMS")

    opcion = st.selectbox("Seleccionar fuente de datos", list(FUENTES.keys()))
    coleccion = FUENTES[opcion]

    col1, col2 = st.columns(2)
    with col1:
        fecha_desde = st.date_input("📅 Desde", value=date(2024, 1, 1))
    with col2:
        fecha_hasta = st.date_input("📅 Hasta", value=date.today())

    if fecha_desde > fecha_hasta:
        st.error("⚠️ La fecha 'desde' no puede ser posterior a la fecha 'hasta'.")
        return

    campo_fecha = CAMPOS_FECHA.get(opcion, None)

    if campo_fecha:
        datos = list(coleccion.find({
            campo_fecha: {
                "$gte": str(fecha_desde),
                "$lte": str(fecha_hasta)
            }
        }, {"_id": 0}))
    else:
        datos = list(coleccion.find({}, {"_id": 0}))

    if not datos:
        st.warning("No hay datos para ese rango.")
        return

    df = pd.DataFrame(datos)
    for col in df.columns:
        if "id" in col.lower():
            df[col] = df[col].astype(str)

    st.dataframe(df.sort_values(by=campo_fecha, ascending=False) if campo_fecha else df.tail(20), use_container_width=True)

    if st.button("📄 Generar PDF de todo el reporte"):
        archivo = generar_pdf(opcion, df)
        with open(archivo, "rb") as f:
            st.download_button(
                label="⬇️ Descargar PDF",
                data=f,
                file_name=os.path.basename(archivo),
                mime="application/pdf"
            )

def app_reportes():
    mostrar_reportes()
