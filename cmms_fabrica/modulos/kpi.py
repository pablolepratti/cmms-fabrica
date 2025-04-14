import os
import pandas as pd
from datetime import datetime

RUTA_TAREAS = os.path.join("data", "tareas.csv")
RUTA_SERVICIOS = os.path.join("data", "servicios.csv")

# Cargar datasets
def cargar_tareas():
    return pd.read_csv(RUTA_TAREAS)

def cargar_servicios():
    return pd.read_csv(RUTA_SERVICIOS)

# KPI tareas internas
def resumen_tareas_internas():
    df = cargar_tareas()
    total = len(df)
    cumplidas = len(df[df["estado"] == "cumplida"])
    reactivas = len(df[df["origen"] == "reactiva"])
    pendientes = len(df[df["estado"] == "pendiente"])
    return {
        "total": total,
        "cumplidas": cumplidas,
        "pendientes": pendientes,
        "reactivas": reactivas,
        "cumplimiento_%": round((cumplidas / total) * 100, 2) if total else 0
    }

# KPI servicios externos
def resumen_servicios_externos():
    df = cargar_servicios()
    realizados = len(df[df["estado"] == "realizado"])
    pendientes = len(df[df["estado"] == "pendiente"])
    vencidos = len(df[df["estado"] == "vencido"])
    total = len(df)
    return {
        "total": total,
        "realizados": realizados,
        "pendientes": pendientes,
        "vencidos": vencidos,
        "cumplimiento_%": round((realizados / total) * 100, 2) if total else 0
    }

# Total intervenciones (internas + externas)
def kpi_total_intervenciones():
    tareas = cargar_tareas()
    servicios = cargar_servicios()
    total_tareas = len(tareas)
    total_servicios = len(servicios)
    return {
        "intervenciones_totales": total_tareas + total_servicios,
        "tareas_internas": total_tareas,
        "servicios_externos": total_servicios
    }

# Activos más intervenidos (tareas + servicios)
def activos_con_mas_movimiento(top_n=5):
    tareas = cargar_tareas()
    servicios = cargar_servicios()
    tareas_count = tareas["id_maquina"].value_counts()
    servicios_count = servicios["id_activo"].value_counts()
    total = (tareas_count.add(servicios_count, fill_value=0)).sort_values(ascending=False)
    return total.head(top_n).reset_index().rename(columns={"index": "id_activo", 0: "intervenciones"})
