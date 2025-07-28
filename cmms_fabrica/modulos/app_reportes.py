"""
📄 Módulo de Reportes Técnicos – CMMS Fábrica

Este módulo permite consultar y exportar reportes a partir de la colección `historial`
y los movimientos recientes en `inventario`, con filtros por tipo de evento, fechas y activo técnico.

✅ Normas aplicadas:
- ISO 9001:2015 (Trazabilidad documental)
- ISO 55001 (Gestión del mantenimiento basada en activos)
"""

import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime, date
from modulos.conexion_mongo import db
import os
from io import BytesIO

# 🔗 Colecciones MongoDB
coleccion = db["historial"]
activos_tecnicos = db["activos_tecnicos"]
inventario = db["inventario"]

# 🔐 Función para eliminar caracteres no soportados por PDF
def safe_text(text):
    if not isinstance(text, str):
        text = str(text)
    return text.encode("latin-1", "ignore").decode("latin-1")

# 📄 Clase PDF personalizada
class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, safe_text("Reporte de Actividades Técnicas – CMMS Fábrica"), ln=True, align="C")
        self.ln(5)

    def chapter_body(self, titulo, df):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, safe_text(titulo), ln=True)
        self.set_font("Arial", "", 10)
        self.ln(2)
        for _, row in df.iterrows():
            self.multi_cell(0, 6, safe_text(f"Activo técnico: {row.get('id_activo_tecnico', '-')}"), 0)
            self.multi_cell(0, 6, safe_text(f"Fecha: {row.get('fecha_evento', '-').strftime('%Y-%m-%d %H:%M')}"), 0)
            self.multi_cell(0, 6, safe_text(f"Tipo de evento: {row.get('tipo_evento', '-')}"), 0)
            origen = row.get('id_origen') or "HUÉRFANO"
            self.multi_cell(0, 6, safe_text(f"ID de origen: {origen}"), 0)
            self.multi_cell(0, 6, safe_text(f"Usuario: {row.get('usuario_registro', '-')}"), 0)
            self.set_font("Arial", "B", 10)
            self.multi_cell(0, 6, safe_text("Descripción:"), 0)
            self.set_font("Arial", "", 10)
            self.multi_cell(0, 6, safe_text(row.get("descripcion", "-")), 0)
            self.multi_cell(0, 6, safe_text(f"Observaciones: {row.get('observaciones', '-')}"), 0)
            self.ln(3)

# 📤 Generador de PDF
def generar_pdf(df_eventos, df_inventario, nombre):
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    if not df_eventos.empty:
        pdf.chapter_body("Últimos eventos técnicos por activo", df_eventos)
    else:
        pdf.set_font("Arial", "I", 10)
        pdf.cell(0, 10, safe_text("No se registraron eventos técnicos en este período."), ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, safe_text("Movimientos recientes en Inventario"), ln=True)
    pdf.ln(2)
    if not df_inventario.empty:
        pdf.set_font("Arial", "", 10)
        for _, row in df_inventario.iterrows():
            fecha = row['fecha_evento'].strftime('%Y-%m-%d')
            pdf.multi_cell(0, 6, safe_text(f"{fecha} – {row.get('id_item', '-')} – {row.get('descripcion', '-')}"), 0)
    else:
        pdf.set_font("Arial", "I", 10)
        pdf.cell(0, 10, safe_text("No hubo movimientos en inventario."), ln=True)
    os.makedirs("reportes", exist_ok=True)
    ruta = f"reportes/reporte_{nombre.lower().replace(' ', '_')}.pdf"
    pdf.output(ruta)
    return ruta

# 📥 Generador de Excel
def generar_excel(df_eventos, df_inventario):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        if not df_eventos.empty:
            df_eventos.to_excel(writer, sheet_name="Eventos Técnicos", index=False)
        if not df_inventario.empty:
            df_inventario.to_excel(writer, sheet_name="Inventario", index=False)
    output.seek(0)
    return output

# 🔍 Filtrar última actualización por tarea y activo técnico
def filtrar_ultimo_por_tarea_y_activo(df):
    """Devuelve la última entrada por combinación de activo técnico y tarea."""
    if "id_origen" not in df or "id_activo_tecnico" not in df or "fecha_evento" not in df:
        return df
    df_ordenado = df.sort_values("fecha_evento", ascending=False)
    idx = df_ordenado.groupby(["id_activo_tecnico", "id_origen"])["fecha_evento"].idxmax()
    return df_ordenado.loc[idx].reset_index(drop=True)

# Compatibilidad con versiones anteriores
def filtrar_ultimo_por_activo(df):
    """Mantiene compatibilidad con versiones que agrupaban solo por tarea."""
    return filtrar_ultimo_por_tarea_y_activo(df)

# 🚀 Interfaz principal
def app():
    st.title("📄 Reportes Técnicos del CMMS")

    with st.sidebar:
        st.markdown("### 📅 Filtros")
        fecha_desde = st.date_input("Desde", value=date(2025, 6, 1))
        fecha_hasta = st.date_input("Hasta", value=date.today())
        tipo_evento = st.multiselect("Tipo de Evento", ["preventiva", "correctiva", "tecnica", "calibracion", "observacion"],
                                     default=["preventiva", "correctiva", "tecnica", "calibracion"])
        activos = list(activos_tecnicos.find({}, {"_id": 0, "id_activo_tecnico": 1, "pertenece_a": 1}))
        opciones = ["Todos"] + sorted([
            f"{a['id_activo_tecnico']} (pertenece a {a['pertenece_a']})" if a.get("pertenece_a") else a["id_activo_tecnico"]
            for a in activos
        ])
        seleccion = st.selectbox("Activo Técnico (con subactivos)", opciones)
        id_activo = seleccion.split(" ")[0] if seleccion != "Todos" else None

    if fecha_desde > fecha_hasta:
        st.error("⚠️ Rango de fechas inválido.")
        return

    query = {
        "fecha_evento": {
            "$gte": datetime.combine(fecha_desde, datetime.min.time()),
            "$lte": datetime.combine(fecha_hasta, datetime.max.time())
        },
        "tipo_evento": {"$in": tipo_evento}
    }
    if id_activo:
        subactivos = [a["id_activo_tecnico"] for a in activos if a.get("pertenece_a") == id_activo]
        ids = [id_activo] + subactivos
        query["id_activo_tecnico"] = {"$in": ids}
        st.sidebar.success(f"Incluye {len(subactivos)} subactivo(s)")

    datos = list(coleccion.find(query, {"_id": 0}))
    if not datos:
        st.warning("No se encontraron eventos técnicos en este período.")
        return

    df = pd.DataFrame(datos)
    df["fecha_evento"] = pd.to_datetime(df["fecha_evento"])
    for campo in ["usuario_registro", "descripcion", "observaciones", "id_origen"]:
        if campo not in df.columns:
            df[campo] = "" if campo == "id_origen" else "-"
    df["usuario_registro"] = df["usuario_registro"].fillna("desconocido")
    df["id_origen"] = df["id_origen"].replace("-", "").fillna("HUÉRFANO")

    df_filtrado = filtrar_ultimo_por_tarea_y_activo(df)

    columnas = ["fecha_evento", "tipo_evento", "id_activo_tecnico", "id_origen", "descripcion", "usuario_registro", "observaciones"]
    for col in columnas:
        if col not in df_filtrado.columns:
            df_filtrado[col] = "HUÉRFANO" if col == "id_origen" else "-"
    if "id_origen" in df_filtrado.columns:
        df_filtrado["id_origen"] = df_filtrado["id_origen"].replace("-", "").fillna("HUÉRFANO")
    st.markdown("### ✅ Última actualización por tarea y activo técnico")
    st.dataframe(df_filtrado[columnas].sort_values("fecha_evento", ascending=False), use_container_width=True)

    st.markdown("### 📦 Movimientos recientes en Inventario")
    df_inv = pd.DataFrame(list(inventario.find({
        "ultima_actualizacion": {
            "$gte": fecha_desde.strftime("%Y-%m-%d"),
            "$lte": fecha_hasta.strftime("%Y-%m-%d")
        }
    }, {"_id": 0, "id_item": 1, "descripcion": 1, "ultima_actualizacion": 1})))

    if not df_inv.empty:
        df_inv["fecha_evento"] = pd.to_datetime(df_inv["ultima_actualizacion"])
        st.dataframe(df_inv[["fecha_evento", "id_item", "descripcion"]])
    else:
        st.markdown(
            (
                "<div style='text-align:center;color:#21ba45;font-weight:bold;'>"
                "✅ No hubo movimientos recientes. Todo está en orden."
                "</div>"
            ),
            unsafe_allow_html=True,
        )

    deshabilitar_export = df_filtrado.empty

    col1, col2 = st.columns(2)
    with col1:
        if st.button("📄 Generar PDF", disabled=deshabilitar_export):
            archivo = generar_pdf(df_filtrado[columnas], df_inv, nombre="reporte")
            with open(archivo, "rb") as f:
                st.download_button("⬇️ Descargar PDF", data=f, file_name=os.path.basename(archivo), mime="application/pdf")
    with col2:
        if st.button("📥 Descargar Excel", disabled=deshabilitar_export):
            excel = generar_excel(df_filtrado[columnas], df_inv)
            st.download_button("⬇️ Descargar Excel", data=excel, file_name="reporte.xlsx",
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

if __name__ == "__main__":
    app()
