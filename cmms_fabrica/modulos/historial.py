import csv
import os
from datetime import datetime

RUTA_CSV = os.path.join("data", "historial.csv")

# Registrar evento en historial
def log_evento(usuario, evento, id_referencia, tipo_origen, detalle):
    fila = {
        "fecha": datetime.today().strftime("%Y-%m-%d"),
        "usuario": usuario,
        "evento": evento,
        "id_referencia": id_referencia,
        "tipo_origen": tipo_origen,
        "detalle": detalle
    }
    archivo_existe = os.path.isfile(RUTA_CSV)
    with open(RUTA_CSV, mode="a", newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fila.keys())
        if not archivo_existe:
            writer.writeheader()
        writer.writerow(fila)
