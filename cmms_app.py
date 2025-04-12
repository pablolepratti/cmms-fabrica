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
# Conexión a PostgreSQL segura
# -------------------------------
def get_connection():
    try:
        return psycopg2.connect(
            host=DB_HOST,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT,
            cursor_factory=RealDictCursor
        )
    except Exception as e:
        st.error(f"❌ Error al conectar a la base de datos: {e}")
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
# Inicialización de tablas y CSV
# -------------------------------
def inicializar_tabla(nombre_tabla, columnas_sql, archivo_csv=None):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(f"CREATE TABLE IF NOT EXISTS {nombre_tabla} ({columnas_sql})")
            cur.execute(f"SELECT COUNT(*) FROM {nombre_tabla}")
            count = cur.fetchone()[0]

            if count == 0:
                if archivo_csv and os.path.exists(archivo_csv):
                    df = pd.read_csv(archivo_csv)
                    columnas = ", ".join(df.columns)
                    placeholders = ", ".join(["%s"] * len(df.columns))
                    for _, row in df.iterrows():
                        cur.execute(f"INSERT INTO {nombre_tabla} ({columnas}) VALUES ({placeholders})", tuple(row))
                    conn.commit()
                    print(f"✅ Datos cargados en {nombre_tabla}")
                else:
                    print(f"⚠️ CSV no encontrado: {archivo_csv}")

def inicializar_base():
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

    inicializar_tabla("maquinas", "ID TEXT, Nombre TEXT, Sector TEXT, Estado TEXT", "cmms_data/maquinas.csv")
    inicializar_tabla("tareas", "ID TEXT, ID_maquina TEXT, Tarea TEXT, Periodicidad TEXT, Ultima_ejecucion TEXT", "cmms_data/tareas.csv")
    inicializar_tabla("inventario", "ID TEXT, Nombre TEXT, Tipo TEXT, Cantidad TEXT, Maquina_asociada TEXT", "cmms_data/inventario.csv")
    inicializar_tabla("observaciones", "ID TEXT, Maquina TEXT, Observacion TEXT, Fecha TEXT, Usuario TEXT", "cmms_data/observaciones.csv")
    inicializar_tabla("historial", "id_maquina TEXT, tarea TEXT, fecha TEXT, usuario TEXT", "cmms_data/historial.csv")

# -------------------------------
# Interfaz de usuario
# -------------------------------
st.set_page_config(page_title="CMMS Fábrica", layout="wide")

if "logueado" not in st.session_state:
    st.session_state.logueado = False
    st.session_state.usuario = ""
    st.session_state.rol = ""

if st.sidebar.button("🔄 Inicializar Base de Datos"):
    inicializar_base()
    st.success("Base de datos inicializada")

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
            id_maquina = tareas[tareas["Tarea"] == tarea]["ID_maquina"].values[0]
            execute_query("UPDATE tareas SET Ultima_ejecucion = %s WHERE Tarea = %s", (fecha, tarea))
            execute_query("INSERT INTO historial (id_maquina, tarea, fecha, usuario) VALUES (%s, %s, %s, %s)",
                          (id_maquina, tarea, fecha, st.session_state.usuario))
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
            execute_query("INSERT INTO observaciones (Maquina, Observacion, Fecha, Usuario) VALUES (%s, %s, %s, %s)",
                          (maquina, observacion, datetime.date.today(), st.session_state.usuario))
            st.success("Observación registrada correctamente")

        st.subheader("Historial de observaciones")
        obs = query_df("SELECT * FROM observaciones")
        st.dataframe(obs)
    except:
        st.error("❌ Error al mostrar las observaciones.")
