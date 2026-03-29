import pymongo
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "cmms")

client = None
db = None
mongo_error = None

if MONGO_URI:
    try:
        client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        client.server_info()
        db = client[DB_NAME]
    except Exception as e:
        client = None
        db = None
        mongo_error = f"{type(e).__name__}: {e}"
else:
    mongo_error = "Falta la variable de entorno MONGO_URI"
    db = None


def get_db():
    """Devuelve la instancia de base de datos activa, si está disponible."""
    return db
