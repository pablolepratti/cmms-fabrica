import csv
import os
import pandas as pd
from datetime import datetime, timedelta

RUTA_CSV = os.path.join("data", "tareas.csv")

# Cargar tareas
def cargar_tareas():
    return pd.read_csv(RUTA_CSV)

# Guardar tareas
def guardar_tareas(df):
    df.to_csv(RUTA_CSV, index=False)

# Listar tareas por máquina
def listar_tareas_por_maquina(id_maquina):
    df = cargar_tareas()
    return df[df["id_maquina"] == id_maquina]

# Ver tareas pendientes
def ver_tareas_pendientes():
    df = cargar_tareas()
    return df[df["estado"] == "pendiente"]

# Marcar tarea como realizada
def marcar_como_realizada(id_tarea, fecha_realizacion=None):
    df = cargar_tareas()
    if fecha_realizacion is None:
        fecha_realizacion = datetime.today().strftime("%Y-%m-%d")
    if id_tarea in df["id_tarea"].values:
        df.loc[df["id_tarea"] == id_tarea, "estado"] = "cumplida"
        df.loc[df["id_tarea"] == id_tarea, "ultima_ejecucion"] = fecha_realizacion
        if df.loc[df["id_tarea"] == id_tarea, "origen"].values[0] == "mensual":
            proxima = datetime.strptime(fecha_realizacion, "%Y-%m-%d") + timedelta(days=30)
            df.loc[df["id_tarea"] == id_tarea, "proxima_ejecucion"] = proxima.strftime("%Y-%m-%d")
        guardar_tareas(df)
        return True
    return False

# Crear tarea reactiva
def crear_tarea_reactiva(tarea_dict):
    df = cargar_tareas()
    df = pd.concat([df, pd.DataFrame([tarea_dict])], ignore_index=True)
    guardar_tareas(df)

# Generar tareas mensuales automáticamente
def generar_tareas_mensuales(template_tareas):
    df = cargar_tareas()
    nuevas_tareas = pd.DataFrame(template_tareas)
    df = pd.concat([df, nuevas_tareas], ignore_index=True)
    guardar_tareas(df)

# Ver historial completo de tareas de una máquina
def historial_maquina(id_maquina):
    df = cargar_tareas()
    return df[df["id_maquina"] == id_maquina]
