import pymongo
from pymongo import errors
import os
from dotenv import load_dotenv

# 🔐 Cargar variables de entorno desde .env
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "cmms")

if not MONGO_URI:
    raise Exception("❌ No se encontró la URI de MongoDB. Verifica tu archivo .env")

# 🚀 Conexión a MongoDB
try:
    client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    client.server_info()
except errors.ServerSelectionTimeoutError as e:
    raise Exception("❌ Error de conexión a MongoDB") from e

db = client[DB_NAME]
