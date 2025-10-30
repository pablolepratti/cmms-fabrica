import pymongo
from pymongo import errors
import os
from dotenv import load_dotenv

# 🔐 Cargar variables de entorno desde .env
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "cmms")

client = None
db = None
if MONGO_URI:
    try:
        client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        client.server_info()
        db = client[DB_NAME]
    except Exception:
        # Entorno de pruebas o base no disponible
        client = None
        db = None
else:
    # MODO TEST sin variables de entorno
    db = None


def get_db():
    """Devuelve la instancia de base de datos activa, si está disponible."""
    return db
