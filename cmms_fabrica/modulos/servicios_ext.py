import csv
import os
import pandas as pd
from datetime import datetime, timedelta

RUTA_CSV = os.path.join("data", "servicios.csv")

# Cargar servicios
def cargar_servicios():
    return pd.read_csv(RUTA_CSV)

# Guardar servicios
def guardar_servicios(df):
    df.to_csv(RUTA_CSV, index=False)

# Registrar nuevo servicio
def registrar_servicio(servicio_dict):
    df = cargar_servicios()
    df = pd.concat([df, pd.DataFrame([servicio_dict])], ignore_index=True)
    guardar_servicios(df)

# Marcar servicio como realizado
def marcar_realizado(id_servicio, fecha_realizacion=None):
    df = cargar_servicios()
    if fecha_realizacion is None:
        fecha_realizacion = datetime.today().strftime("%Y-%m-%d")
    if id_servicio in df["id_servicio"].values:
        index = df[df["id_servicio"] == id_servicio].index[0]
        df.at[index, "fecha_realizacion"] = fecha_realizacion
        df.at[index, "estado"] = "realizado"
        periodicidad = df.at[index, "periodicidad"]
        if periodicidad != "única":
            dias = {
                "mensual": 30,
                "bimensual": 60,
                "trimestral": 90,
                "anual": 365
            }.get(periodicidad, 0)
            if dias:
                proxima_fecha = datetime.strptime(fecha_realizacion, "%Y-%m-%d") + timedelta(days=dias)
                df.at[index, "proxima_fecha"] = proxima_fecha.strftime("%Y-%m-%d")
        guardar_servicios(df)
        from modulos.historial import log_evento
        detalle = f"Servicio realizado por {df.at[index, 'empresa']} sobre {df.at[index, 'id_activo']}"
        log_evento("sistema", "Servicio externo realizado", id_servicio, "servicios", detalle)
        return True
    return False

# Verificar vencimientos
def verificar_vencimientos():
    df = cargar_servicios()
    hoy = datetime.today().date()
    vencidos = []
    for i, row in df.iterrows():
        if row["estado"] != "realizado" and row["proxima_fecha"]:
            try:
                proxima = datetime.strptime(row["proxima_fecha"], "%Y-%m-%d").date()
                if proxima < hoy:
                    vencidos.append(row)
            except:
                continue
    return pd.DataFrame(vencidos)

# Listar servicios por activo
def listar_por_activo(id_activo):
    df = cargar_servicios()
    return df[df["id_activo"] == id_activo]

# Listar servicios pendientes
def listar_pendientes():
    df = cargar_servicios()
    return df[df["estado"].isin(["pendiente", "vencido"])]
