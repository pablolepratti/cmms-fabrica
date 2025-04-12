import streamlit as st
import pandas as pd
import datetime
import hashlib
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# -------------------------------
# Cargar variables de entorno
# -------------------------------
load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = os.getenv("DB_PORT")

# -------------------------------
# Conexión a PostgreSQL
# -------------------------------
def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )

def query_df(sql, params=None):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, params)
            return pd.DataFrame(cur.fetchall())

def execute_query(sql, params=None):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            conn.commit()

# -------------------------------
# Hash de contraseña y login
# -------------------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verificar_login(usuario, password):
    hashed = hash_password(password)
    try:
        df = query_df("SELECT * FROM usuarios WHERE usuario = %s", (usuario,))
        if not df.empty and df.iloc[0]["hash_contraseña"] == hashed:
            return df.iloc[0]["rol"]
    except:
        pass
    return None

# -------------------------------
# Inicialización segura de tablas
# -------------------------------
def inicializar_tabla(nombre_tabla, columnas_sql, archivo_csv=None):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(f"CREATE TABLE IF NOT EXISTS {nombre_tabla} ({columnas_sql})")
            cur.execute(f"SELECT COUNT(*) FROM {nombre_tabla}")
            count = cur.fetchone()[0]

            if count == 0 and archivo_csv and os.path.exists(archivo_csv):
                df = pd.read_csv(archivo_csv)
                columnas = ", ".join(df.columns)
                placeholders = ", ".join(["%s"] * len(df.columns))
                for _, row in df.iterrows():
                    cur.execute(f"INSERT INTO {nombre_tabla} ({columnas}) VALUES ({placeholders})", tuple(row))
                conn.commit()
                print(f"✅ Datos cargados en {nombre_tabla}")

# -------------------------------
# Inicializar base completa
# -------------------------------
def inicializar_base():
    # Usuarios con valor inicial
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    usuario TEXT PRIMARY KEY,
                    hash_contraseña TEXT,
                    rol TEXT
                )
            """)
            cur.execute("SELECT COUNT(*) FROM usuarios")
            if cur.fetchone()[0] == 0:
                cur.execute("INSERT INTO usuarios VALUES (%s, %s, %s)", ("pablo", hash_password("admin123"), "admin"))
                conn.commit()
                print("✅ Usuario admin creado")

    # Otras tablas
    inicializar_tabla("maquinas", "ID TEXT, Nombre TEXT, Sector TEXT, Estado TEXT", "cmms_data/maquinas.csv")
    inicializar_tabla("tareas", "id_maquina TEXT, tarea TEXT, periodicidad TEXT, ultima_ejecucion TEXT", "cmms_data/tareas.csv")
    inicializar_tabla("inventario", "id TEXT, item TEXT, cantidad TEXT", "cmms_data/inventario.csv")
    inicializar_tabla("observaciones", "maquina TEXT, observacion TEXT, fecha TEXT, usuario TEXT", "cmms_data/observaciones.csv")
    inicializar_tabla("historial", "tarea TEXT, fecha TEXT, usuario TEXT", "cmms_data/historial.csv")

inicializar_base()

# -------------------------------
# Streamlit app
# -------------------------------
st.set_page_config(page_title="CMMS Fábrica", layout="wide")

if "logueado" not in st.session_state:
    st.session_state.logueado = False
    st.session_state.usuario = ""
    st.session_state.rol = ""

if not st.session_state.logueado:
    st.title("🔐 Iniciar sesión")
    usuario = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    if st.button("Ingresar"):
        rol = verificar_login(usuario, password)
        if rol:
            st.session_state.logueado = True
            st.session_state.usuario = usuario
            st.session_state.rol = rol
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos")
    st.stop()

# Sesión activa
st.sidebar.markdown(f"👤 **{st.session_state.usuario}** ({st.session_state.rol})")
if st.sidebar.button("Cerrar sesión"):
    st.session_state.logueado = False
    st.rerun()

st.title("🛠️ Dashboard de Mantenimiento Preventivo")

menu = st.sidebar.radio("Ir a:", [
    "Inicio", "Tareas vencidas", "Cargar tarea realizada",
    "Observaciones técnicas"])

if menu == "Inicio":
    try:
        maquinas = query_df("SELECT * FROM maquinas")
        tareas = query_df("SELECT * FROM tareas")
        inventario = query_df("SELECT * FROM inventario")
        st.subheader("Resumen general")
        st.metric("Máquinas registradas", len(maquinas))
        st.metric("Tareas programadas", len(tareas))
        st.metric("Stock total", len(inventario))
    except:
        st.warning("⚠️ No se pudieron cargar las métricas. Verificá si las tablas están vacías o si hay conexión con la base.")

elif menu == "Tareas vencidas":
    try:
        tareas = query_df("SELECT * FROM tareas")
        tareas["ultima_ejecucion"] = pd.to_datetime(tareas["ultima_ejecucion"], errors="coerce")
        vencidas = tareas[tareas["ultima_ejecucion"] < (pd.Timestamp.today() - pd.Timedelta(days=30))]
        st.subheader("Tareas vencidas")
        st.dataframe(vencidas[["id_maquina", "tarea", "periodicidad", "ultima_ejecucion"]])
    except:
        st.error("❌ Error al cargar las tareas.")

elif menu == "Cargar tarea realizada":
    try:
        tareas = query_df("SELECT * FROM tareas")
        st.subheader("Registrar nueva ejecución de tarea")
        tarea = st.selectbox("Tarea a actualizar", tareas["tarea"].unique())
        fecha = st.date_input("Fecha de realización", value=datetime.date.today())
        if st.button("Registrar ejecución"):
            execute_query("UPDATE tareas SET ultima_ejecucion = %s WHERE tarea = %s", (fecha, tarea))
            execute_query("INSERT INTO historial (tarea, fecha, usuario) VALUES (%s, %s, %s)", (tarea, fecha, st.session_state.usuario))
            st.success(f"Tarea '{tarea}' actualizada a {fecha}")
    except:
        st.error("❌ No se pudo registrar la ejecución.")

elif menu == "Observaciones técnicas":
    try:
        maquinas = query_df("SELECT * FROM maquinas")
        st.subheader("Registrar observación técnica")
        maquina = st.selectbox("Máquina", maquinas["Nombre"])
        observacion = st.text_area("Observación")
        if st.button("Guardar observación"):
            execute_query("INSERT INTO observaciones (maquina, observacion, fecha, usuario) VALUES (%s, %s, %s, %s)",
                          (maquina, observacion, datetime.date.today(), st.session_state.usuario))
            st.success("Observación registrada correctamente")

        st.subheader("Historial de observaciones")
        obs = query_df("SELECT * FROM observaciones")
        st.dataframe(obs)
    except:
        st.error("❌ Error al mostrar las observaciones.")
