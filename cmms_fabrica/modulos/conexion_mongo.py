import pymongo
import os
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise Exception("❌ No se encontró la URI de MongoDB")

client = pymongo.MongoClient(MONGO_URI)
db = client["cmms_fabrica"]  # 🔄 Nombre correcto de tu base de datos
