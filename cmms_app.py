import streamlit as st
import pandas as pd
import datetime
import hashlib
import os
import time
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
# Conexión a PostgreSQL segura con reintento
# -------------------------------
def get_connection():
    try:
        for intento in range(3):
            try:
                return psycopg2.connect(
                    host=DB_HOST,
                    dbname=DB_NAME,
                    user=DB_USER,
                    password=DB_PASSWORD,
                    port=DB_PORT,
                    cursor_factory=RealDictCursor,
                    sslmode="require"
                )
            except psycopg2.OperationalError:
                time.sleep(5)  # Espera 5 segundos antes de reintentar
        st.error("🔌 No se pudo conectar a la base tras varios intentos.")
        return None
    except Exception as e:
        st.error(f"❌ Error general al conectar: {e}")
        return None

def query_df(sql, params=None):
    conn = get_connection()
    if conn is None:
        return pd.DataFrame()
    with conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return pd.DataFrame(cur.fetchall())

def execute_query(sql, params=None):
    conn = get_connection()
    if conn is None:
        return
    with conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            conn.commit()

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

def inicializar_tabla(nombre_tabla, columnas_sql, archivo_csv=None):
    conn = get_connection()
    if conn is None:
        return
    with conn:
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

def inicializar_base():
    conn = get_connection()
    if conn is None:
        return
    with conn:
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

    inicializar_tabla("maquinas", "ID TEXT, Nombre TEXT, Sector TEXT, Estado TEXT", "cmms_data/maquinas.csv")
    inicializar_tabla("tareas", "ID TEXT, ID_maquina TEXT, Tarea TEXT, Periodicidad TEXT, Ultima_ejecucion TEXT", "cmms_data/tareas.csv")
    inicializar_tabla("inventario", "ID TEXT, Nombre TEXT, Tipo TEXT, Cantidad TEXT, Maquina_asociada TEXT", "cmms_data/inventario.csv")
    inicializar_tabla("observaciones", "ID TEXT, Maquina TEXT, Observacion TEXT, Fecha TEXT, Usuario TEXT", "cmms_data/observaciones.csv")
    inicializar_tabla("historial", "ID_maquina TEXT, Tarea TEXT, Fecha TEXT, Usuario TEXT", "cmms_data/historial.csv")

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

st.sidebar.markdown(f"👤 **{st.session_state.usuario}** ({st.session_state.rol})")
if st.sidebar.button("Cerrar sesión"):
    st.session_state.logueado = False
    st.rerun()

st.title("🛠️ Dashboard de Mantenimiento Preventivo")
menu = st.sidebar.radio("Ir a:", ["Inicio", "Tareas vencidas", "Cargar tarea realizada", "Observaciones técnicas"])

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
        st.warning("⚠️ No se pudieron cargar las métricas.")

elif menu == "Tareas vencidas":
    try:
        tareas = query_df("SELECT * FROM tareas")
        tareas["Ultima_ejecucion"] = pd.to_datetime(tareas["Ultima_ejecucion"], errors="coerce")
        vencidas = tareas[tareas["Ultima_ejecucion"] < (pd.Timestamp.today() - pd.Timedelta(days=30))]
        st.subheader("Tareas vencidas")
        st.dataframe(vencidas[["ID_maquina", "Tarea", "Periodicidad", "Ultima_ejecucion"]])
    except:
        st.error("❌ Error al cargar las tareas.")

elif menu == "Cargar tarea realizada":
    try:
        tareas = query_df("SELECT * FROM tareas")
        st.subheader("Registrar nueva ejecución de tarea")
        tarea = st.selectbox("Tarea a actualizar", tareas["Tarea"].unique())
        fecha = st.date_input("Fecha de realización", value=datetime.date.today())
        if st.button("Registrar ejecución"):
            execute_query("UPDATE tareas SET Ultima_ejecucion = %s WHERE Tarea = %s", (fecha, tarea))
            execute_query("INSERT INTO historial (ID_maquina, Tarea, Fecha, Usuario) VALUES (%s, %s, %s, %s)", 
                          (tareas[tareas["Tarea"] == tarea]["ID_maquina"].values[0], tarea, fecha, st.session_state.usuario))
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
            execute_query("INSERT INTO observaciones (ID, Maquina, Observacion, Fecha, Usuario) VALUES (%s, %s, %s, %s, %s)",
                          (str(datetime.datetime.now().timestamp()), maquina, observacion, datetime.date.today(), st.session_state.usuario))
            st.success("Observación registrada correctamente")

        st.subheader("Historial de observaciones")
        obs = query_df("SELECT * FROM observaciones")
        st.dataframe(obs)
    except:
        st.error("❌ Error al mostrar las observaciones.")
