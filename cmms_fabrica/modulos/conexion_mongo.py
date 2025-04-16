import pymongo
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# URI de conexión
MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise Exception("❌ No se encontró la URI de MongoDB. Verifica tu archivo .env")

# Cliente de MongoDB
client = pymongo.MongoClient(MONGO_URI)

# Base de datos
db = client["cmms"]  # Asegurate que este sea exactamente el nombre en Atlas
