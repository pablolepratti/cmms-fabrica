from pymongo import MongoClient
from datetime import datetime
import os

# Conexión a MongoDB
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client.get_database("cmms_fabrica")

def obtener_tareas_activas():
    return list(db.tareas.find({"estado": "pendiente"}))

def obtener_tareas_tecnicas():
    return list(db.tareas_tecnicas.find({"estado": "pendiente"}))

def obtener_observaciones():
    return list(db.observaciones.find().sort("fecha", -1).limit(10))

def contar_kpis():
    hoy = datetime.today().strftime("%Y-%m-%d")
    pendientes = db.tareas.count_documents({"estado": "pendiente"})
    hechas_hoy = db.tareas.count_documents({"estado": "realizada", "fecha_realizada": hoy})
    return {"pendientes": pendientes, "hechas_hoy": hechas_hoy}
