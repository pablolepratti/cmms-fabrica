from datetime import datetime
from modulos.conexion_mongo import db

coleccion_historial = db["historial"]

def log_evento(usuario, evento, id_referencia, tipo_origen, detalle):
    if not usuario or not evento:
        print("[ADVERTENCIA] Registro omitido por falta de usuario o evento.")
        return

    fila = {
        "fecha": datetime.now().isoformat(),
        "usuario": usuario,
        "evento": evento,
        "id_referencia": id_referencia,
        "tipo_origen": tipo_origen,
        "detalle": detalle
    }

    try:
        coleccion_historial.insert_one(fila)
    except Exception as e:
        print(f"[ERROR] No se pudo registrar en historial (Mongo): {e}")

