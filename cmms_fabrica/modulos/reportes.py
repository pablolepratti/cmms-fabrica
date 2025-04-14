import os
import pandas as pd
from fpdf import FPDF
from datetime import datetime

# Rutas a los CSV
DATA_PATH = "data"
RUTA_TAREAS = os.path.join(DATA_PATH, "tareas.csv")
RUTA_OBSERVACIONES = os.path.join(DATA_PATH, "observaciones.csv")
RUTA_SERVICIOS = os.path.join(DATA_PATH, "servicios.csv")
RUTA_HISTORIAL = os.path.join(DATA_PATH, "historial.csv")

# Ruta de salida de reportes
RUTA_SALIDA = "reportes"

class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "Reporte CMMS Fábrica", 0, 1, "C")

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Página {self.page_no()}", 0, 0, "C")

def generar_reporte_general(nombre="reporte_general.pdf"):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)

    secciones = {
        "TAREAS INTERNAS": RUTA_TAREAS,
        "OBSERVACIONES": RUTA_OBSERVACIONES,
        "SERVICIOS EXTERNOS": RUTA_SERVICIOS,
        "HISTORIAL DE EVENTOS": RUTA_HISTORIAL
    }

    for titulo, ruta in secciones.items():
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 10, titulo, ln=True)
        pdf.set_font("Arial", size=9)

        try:
            df = pd.read_csv(ruta)
            if df.empty:
                pdf.cell(0, 8, "Sin registros.", ln=True)
            else:
                for i, row in df.head(10).iterrows():  # muestra primeros 10 registros
                    linea = " | ".join(str(row[c]) for c in df.columns[:4])
                    pdf.multi_cell(0, 6, linea)
        except:
            pdf.cell(0, 8, "Error al leer los datos.", ln=True)

        pdf.ln(5)

    # Guardar PDF
    os.makedirs(RUTA_SALIDA, exist_ok=True)
    salida = os.path.join(RUTA_SALIDA, nombre)
    pdf.output(salida)

    return salida
