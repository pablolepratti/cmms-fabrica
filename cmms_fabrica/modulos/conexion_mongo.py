import pymongo
import os
from dotenv import load_dotenv

# 🔐 Cargar variables de entorno desde .env
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise Exception("❌ No se encontró la URI de MongoDB. Verifica tu archivo .env")

# 🚀 Conexión a MongoDB
client = pymongo.MongoClient(MONGO_URI)
db = client["cmms"]  
