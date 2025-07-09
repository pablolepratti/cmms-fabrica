"""
📄 Reporte Técnico Mensual – CMMS Fábrica

Auditoría técnica por activo en un período elegido.
Incluye resumen por tipo de tarea (correctiva, técnica, preventiva, calibración)
y movimientos recientes en inventario.

✅ Normas aplicables:
- ISO 9001:2015 (trazabilidad y registros)
- ISO 55001 (ciclo de vida del activo técnico)
"""

import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime, date
from modulos.conexion_mongo import db
from io import BytesIO
import os

coleccion = db["historial"]
activos_tecnicos = db["activos_tecnicos"]
inventario = db["inventario"]

TIPOS = ["correctiva", "tecnica", "preventiva", "calibracion"]

class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, "Reporte Técnico Mensual – CMMS Fábrica", ln=True, align="C")
        self.ln(10)

    def tabla_resumen(self, df):
        self.set_font("Arial", "B", 10)
        headers = df.columns.tolist()
        for col in headers:
            self.cell(45, 8, col, border=1)
        self.ln()
        self.set_font("Arial", "", 10)
        for _, row in df.iterrows():
            for col in headers:
                self.cell(45, 8, str(row[col]), border=1)
            self.ln()
        self.ln(5)

    def tabla_detalle(self, df):
        for _, row in df.iterrows():
            self.set_font("Arial", "B", 10)
            self.multi_cell(0, 6, f"{row['fecha_evento']} – {row['tipo_evento']} – {row['id_activo_tecnico']}")
            self.set_font("Arial", "", 9)
            self.multi_cell(0, 6, f"Usuario: {row['usuario_registro']} | Proveedor: {row.get('proveedor_externo', '-')}")
            self.multi_cell(0, 6, f"Descripción: {row['descripcion']}")
            self.multi_cell(0, 6, f"Observaciones: {row['observaciones']}")
            self.ln(3)

    def tabla_inventario(self, df):
        self.set_font("Arial", "B", 10)
        headers = df.columns.tolist()
        for col in headers:
            self.cell(40, 8, col[:15], border=1)
        self.ln()
        self.set_font("Arial", "", 9)
        for _, row in df.iterrows():
            for col in headers:
                self.cell(40, 8, str(row[col])[:15], border=1)
            self.ln()

def app():
    st.title("📄 Reporte Técnico Mensual – Auditoría por Activo")

    with st.sidebar:
        fecha_desde = st.date_input("📆 Desde", value=date(2025, 6, 1))
        fecha_hasta = st.date_input("📆 Hasta", value=date(2025, 6, 30))
        tipos = st.multiselect("Tipo de evento", TIPOS, default=TIPOS)

    if fecha_desde > fecha_hasta:
        st.error("⚠️ Fechas inválidas.")
        return

    query = {
        "fecha_evento": {
            "$gte": datetime.combine(fecha_desde, datetime.min.time()),
            "$lte": datetime.combine(fecha_hasta, datetime.max.time())
        },
        "tipo_evento": {"$in": tipos}
    }
    eventos = list(coleccion.find(query, {"_id": 0}))
    if not eventos:
        st.warning("No hay eventos en ese período.")
        return

    df = pd.DataFrame(eventos)
    df["fecha_evento"] = pd.to_datetime(df["fecha_evento"])
    df["observaciones"] = df.get("observaciones", "-")
    df["usuario_registro"] = df.get("usuario_registro", df.get("usuario", "desconocido"))
    df["proveedor_externo"] = df.get("proveedor_externo", "-")

    resumen = []
    activos = df["id_activo_tecnico"].unique()
    for activo in activos:
        fila = {"Activo Técnico": activo}
        df_activo = df[df["id_activo_tecnico"] == activo]
        for tipo in TIPOS:
            df_tipo = df_activo[df_activo["tipo_evento"] == tipo]
            if not df_tipo.empty:
                cant = len(df_tipo)
                fecha_ult = df_tipo["fecha_evento"].max().strftime("%d/%m")
                fila[tipo.capitalize()] = f"{cant} ({fecha_ult})"
            else:
                fila[tipo.capitalize()] = "—"
        resumen.append(fila)

    df_resumen = pd.DataFrame(resumen)

    st.subheader("🧱 Resumen por Activo Técnico")
    st.dataframe(df_resumen, use_container_width=True)

    st.subheader("📋 Detalle completo de eventos")
    columnas = ["fecha_evento", "tipo_evento", "id_activo_tecnico", "usuario_registro",
                "proveedor_externo", "descripcion", "observaciones"]
    st.dataframe(df[columnas].sort_values("fecha_evento", ascending=False), use_container_width=True)

    st.subheader("📦 Movimientos recientes en Inventario")
    inventario_reciente = list(inventario.find({
        "ultima_actualizacion": {
            "$gte": fecha_desde.strftime("%Y-%m-%d"),
            "$lte": fecha_hasta.strftime("%Y-%m-%d")
        }
    }, {"_id": 0}))
    df_inv = pd.DataFrame(inventario_reciente)
    if not df_inv.empty:
        st.dataframe(df_inv, use_container_width=True)
    else:
        st.info("No hubo actualizaciones en inventario en ese período.")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("📥 Descargar Excel"):
            output = BytesIO()
            with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                df_resumen.to_excel(writer, sheet_name="Resumen_por_activo", index=False)
                df[columnas].to_excel(writer, sheet_name="Detalle_eventos", index=False)
                if not df_inv.empty:
                    df_inv.to_excel(writer, sheet_name="Inventario_actualizado", index=False)
            st.download_button(
                "⬇️ Descargar Excel",
                data=output.getvalue(),
                file_name="reporte_cmms.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    with col2:
        if st.button("🖨️ Generar PDF"):
            pdf = PDF()
            pdf.add_page()
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, f"Período: {fecha_desde.strftime('%d/%m/%Y')} al {fecha_hasta.strftime('%d/%m/%Y')}", ln=True)

            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, "Resumen por Activo", ln=True)
            pdf.tabla_resumen(df_resumen)

            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, "Detalle de Eventos", ln=True)
            pdf.tabla_detalle(df[columnas])

            if not df_inv.empty:
                pdf.set_font("Arial", "B", 12)
                pdf.cell(0, 10, "Movimientos en Inventario", ln=True)
                pdf.tabla_inventario(df_inv)

            output_pdf = BytesIO()
            pdf.output(output_pdf)
            st.download_button(
                "⬇️ Descargar PDF",
                data=output_pdf.getvalue(),
                file_name="reporte_cmms.pdf",
                mime="application/pdf"
            )

if __name__ == "__main__":
    app()
