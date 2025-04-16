from datetime import datetime
from modulos.conexion_mongo import db

# Referencia a la colección 'historial' en la base cmms_fabrica
coleccion_historial = db["historial"]

def log_evento(usuario, evento, id_referencia, tipo_origen, detalle):
    fila = {
        "fecha": datetime.now(),
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
