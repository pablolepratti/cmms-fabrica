
import os
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = os.getenv("DB_PORT")

conn = psycopg2.connect(
    host=DB_HOST,
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    port=DB_PORT
)

def importar_csv(nombre_tabla, archivo_csv):
    df = pd.read_csv(archivo_csv)
    columnas = ', '.join(df.columns)
    valores = [tuple(x) for x in df.to_numpy()]
    with conn.cursor() as cur:
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {nombre_tabla} (
                {', '.join([col + ' TEXT' for col in df.columns])}
            )
        """)
        cur.execute(f"DELETE FROM {nombre_tabla}")
        execute_values(cur, f"INSERT INTO {nombre_tabla} ({columnas}) VALUES %s", valores)
    print(f"✅ {nombre_tabla} importada desde {archivo_csv}")

archivos = {
    "usuarios": "cmms_data/usuarios.csv",
    "maquinas": "cmms_data/maquinas.csv",
    "tareas": "cmms_data/tareas.csv",
    "inventario": "cmms_data/inventario.csv",
    "observaciones": "cmms_data/observaciones.csv",
    "historial": "cmms_data/historial.csv"
}

for tabla, archivo in archivos.items():
    if os.path.exists(archivo):
        importar_csv(tabla, archivo)
    else:
        print(f"⚠️ Archivo no encontrado: {archivo}")

conn.commit()
conn.close()
print("🎉 Importación finalizada.")
