import os
import psycopg2
import pandas as pd
from dotenv import load_dotenv
import ssl
import urllib.parse as urlparse

# Cargar variables de entorno
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Parsear URL para conexión detallada
urlparse.uses_netloc.append("postgres")
url = urlparse.urlparse(DATABASE_URL)

# Conexión SSL segura
conn = psycopg2.connect(
    dbname=url.path[1:],
    user=url.username,
    password=url.password,
    host=url.hostname,
    port=url.port,
    sslmode='require',
    sslrootcert=None,
    sslcert=None,
    sslkey=None,
    sslcontext=ssl.create_default_context()
)

cur = conn.cursor()

# Función para importar CSV a tabla PostgreSQL
def importar_csv(nombre_tabla, archivo_csv):
    print(f"📥 Importando '{archivo_csv}' a la tabla '{nombre_tabla}'...")
    df = pd.read_csv(archivo_csv)

    # Crear tabla si no existe
    columnas = ", ".join([f'"{col}" TEXT' for col in df.columns])
    cur.execute(f'CREATE TABLE IF NOT EXISTS "{nombre_tabla}" ({columnas})')

    # Borrar registros anteriores
    cur.execute(f'DELETE FROM "{nombre_tabla}"')

    # Insertar fila por fila
    for row in df.itertuples(index=False, name=None):
        placeholders = ', '.join(['%s'] * len(row))
        cur.execute(f'INSERT INTO "{nombre_tabla}" VALUES ({placeholders})', row)

    conn.commit()
    print(f"✅ Tabla '{nombre_tabla}' actualizada.")

# Mapear nombres de archivo con nombres de tabla
archivos_tablas = {
    "usuarios": "cmms_data/usuarios.csv",
    "maquinas": "cmms_data/maquinas.csv",
    "tareas": "cmms_data/tareas.csv",
    "inventario": "cmms_data/inventario.csv",
    "observaciones": "cmms_data/observaciones.csv",
    "historial": "cmms_data/historial.csv"
}

# Ejecutar importación
for tabla, archivo in archivos_tablas.items():
    importar_csv(tabla, archivo)

cur.close()
conn.close()
print("🏁 Importación completa.")
