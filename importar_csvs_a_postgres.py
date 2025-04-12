import os
import psycopg2
import pandas as pd
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Intentar usar DATABASE_URL directamente
DATABASE_URL = os.getenv("DATABASE_URL")

# Conexión
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Función para importar un CSV
def importar_csv(nombre_tabla, archivo_csv):
    print(f"📥 Importando '{archivo_csv}' a la tabla '{nombre_tabla}'...")
    df = pd.read_csv(archivo_csv)
    
    # Crear tabla (solo si no existe)
    columnas = ', '.join([f"{col} TEXT" for col in df.columns])
    cur.execute(f"CREATE TABLE IF NOT EXISTS {nombre_tabla} ({columnas})")

    # Borrar datos previos
    cur.execute(f"DELETE FROM {nombre_tabla}")

    # Insertar fila por fila
    for _, row in df.iterrows():
        valores = tuple(row.astype(str))
        placeholders = ', '.join(['%s'] * len(valores))
        cur.execute(f"INSERT INTO {nombre_tabla} VALUES ({placeholders})", valores)

    conn.commit()
    print(f"✅ Datos importados en '{nombre_tabla}'.")

# Rutas relativas
BASE = "cmms_data"
tablas_csv = {
    "usuarios": "usuarios.csv",
    "maquinas": "maquinas.csv",
    "tareas": "tareas.csv",
    "inventario": "inventario.csv",
    "observaciones": "observaciones.csv",
    "historial": "historial.csv"
}

for tabla, archivo in tablas_csv.items():
    ruta = os.path.join(BASE, archivo)
    if os.path.exists(ruta):
        importar_csv(tabla, ruta)
    else:
        print(f"⚠️ No se encontró el archivo {ruta}.")

cur.close()
conn.close()

