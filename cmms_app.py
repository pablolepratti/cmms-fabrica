import streamlit as st
import pandas as pd
import datetime
import hashlib
import os
from fpdf import FPDF

# -------------------------------
# Funciones de login
# -------------------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verificar_login(usuario, password):
    if os.path.exists(usuarios_path):
        usuarios = pd.read_csv(usuarios_path)
        hashed = hash_password(password)
        match = usuarios[
            (usuarios["usuario"].str.strip() == usuario.strip()) &
            (usuarios["hash_contraseña"].str.strip() == hashed.strip())
        ]
        if not match.empty:
            return match.iloc[0]["rol"]
    return None

# -------------------------------
# Rutas de datos
# -------------------------------
DATA_FOLDER = "cmms_data"
maquinas_path = os.path.join(DATA_FOLDER, "maquinas.csv")
tareas_path = os.path.join(DATA_FOLDER, "tareas.csv")
inventario_path = os.path.join(DATA_FOLDER, "inventario.csv")
usuarios_path = os.path.join(DATA_FOLDER, "usuarios.csv")
historial_path = os.path.join(DATA_FOLDER, "historial.csv")
observaciones_path = os.path.join(DATA_FOLDER, "observaciones.csv")

# -------------------------------
# Configuración de la app
# -------------------------------
st.set_page_config(page_title="CMMS Fábrica", layout="wide")

# -------------------------------
# Login
# -------------------------------
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

# -------------------------------
# Cierre de sesión
# -------------------------------
st.sidebar.markdown(f"👤 **{st.session_state.usuario}** ({st.session_state.rol})")
if st.sidebar.button("Cerrar sesión"):
    st.session_state.logueado = False
    st.rerun()

# -------------------------------
# Crear nuevo usuario (solo Pablo)
# -------------------------------
if st.session_state.usuario == "pablo" and st.session_state.rol == "admin":
    with st.sidebar.expander("➕ Crear nuevo usuario"):
        nuevo_user = st.text_input("Nuevo usuario")
        nueva_pass = st.text_input("Contraseña", type="password", key="crear_usuario_pass")
        nuevo_rol = st.selectbox("Rol", ["tecnico", "supervisor"])
        if st.button("Crear usuario"):
            usuarios = pd.read_csv(usuarios_path)
            nuevo = pd.DataFrame([[nuevo_user, hash_password(nueva_pass), nuevo_rol]], columns=usuarios.columns)
            usuarios = pd.concat([usuarios, nuevo], ignore_index=True)
            usuarios.to_csv(usuarios_path, index=False)
            st.success(f"Usuario '{nuevo_user}' creado exitosamente")

# -------------------------------
# Cargar archivos
# -------------------------------
def cargar_csv(path, columnas):
    if not os.path.exists(path):
        df = pd.DataFrame(columns=columnas)
        df.to_csv(path, index=False)
    return pd.read_csv(path)

maquinas = cargar_csv(maquinas_path, ["ID", "Nombre", "Sector", "Estado"])
tareas = cargar_csv(tareas_path, ["ID", "ID_maquina", "Tarea", "Periodicidad", "Última_ejecucion"])
inventario = cargar_csv(inventario_path, ["ID", "Nombre", "Tipo", "Cantidad", "Máquina_asociada"])
usuarios = cargar_csv(usuarios_path, ["usuario", "hash_contraseña", "rol"])
historial = cargar_csv(historial_path, ["ID_maquina", "Tarea", "Fecha", "Usuario"])
observaciones = cargar_csv(observaciones_path, ["ID", "Máquina", "Observacion", "Fecha", "Usuario"])

# -------------------------------
# Menú lateral
# -------------------------------
st.title("🛠️ Dashboard de Mantenimiento Preventivo")
st.markdown("""
<div style='text-align: right;'>
    <a href="https://cmms-mobile.onrender.com" target="_blank" style="text-decoration: none;">
        📱 Ir a la versión Mobile
    </a>
</div>
""", unsafe_allow_html=True)
menu = st.sidebar.radio("Ir a:", [
    "Inicio", "Máquinas", "Tareas de mantenimiento", "Tareas vencidas",
    "Cargar tarea realizada", "Inventario", "Observaciones técnicas",
    "Agregar registros", "Exportar PDF"])

# -------------------------------
# Páginas
# -------------------------------
if menu == "Inicio":
    st.subheader("Resumen general")
    st.metric("Máquinas registradas", len(maquinas))
    st.metric("Tareas programadas", len(tareas))
    st.metric("Stock total", len(inventario))

elif menu == "Máquinas":
    st.subheader("Listado de máquinas")
    st.dataframe(maquinas)

elif menu == "Tareas de mantenimiento":
    st.subheader("Tareas activas")
    st.dataframe(tareas)

elif menu == "Tareas vencidas":
    st.subheader("Tareas vencidas")
    hoy = datetime.date.today()
    tareas["Última_ejecucion"] = pd.to_datetime(tareas["Última_ejecucion"], errors="coerce")
    vencidas = tareas[tareas["Última_ejecucion"] < (pd.Timestamp(hoy) - pd.Timedelta(days=30))]
    st.dataframe(vencidas)

elif menu == "Cargar tarea realizada":
    st.subheader("Registrar nueva ejecución de tarea")
    tarea = st.selectbox("Tarea a actualizar", tareas["Tarea"])
    fecha = st.date_input("Fecha de realización", value=datetime.date.today())

    if st.button("Registrar"):
        idx = tareas[tareas["Tarea"] == tarea].index[0]
        tareas.at[idx, "Última_ejecucion"] = fecha
        tareas.to_csv(tareas_path, index=False)

        id_maquina = tareas.at[idx, "ID_maquina"]
        nuevo_log = pd.DataFrame([[id_maquina, tarea, fecha, st.session_state.usuario]], columns=historial.columns)
        historial = pd.concat([historial, nuevo_log], ignore_index=True)
        historial.to_csv(historial_path, index=False)

        st.success(f"Tarea '{tarea}' actualizada a {fecha}")

elif menu == "Inventario":
    st.subheader("Stock general por tipo")
    if "Tipo" in inventario.columns:
        for tipo in inventario["Tipo"].unique():
            st.markdown(f"### {tipo}")
            st.dataframe(inventario[inventario["Tipo"] == tipo])
    else:
        st.warning("El archivo de inventario no contiene la columna 'Tipo'")
        st.dataframe(inventario)

elif menu == "Observaciones técnicas":
    st.subheader("Registrar observación técnica")
    maquina = st.selectbox("Máquina", maquinas["Nombre"])
    observacion = st.text_area("Observación")
    if st.button("Guardar observación"):
        nueva = pd.DataFrame([[len(observaciones)+1, maquina, observacion, datetime.date.today(), st.session_state.usuario]],
                             columns=observaciones.columns)
        observaciones = pd.concat([observaciones, nueva], ignore_index=True)
        observaciones.to_csv(observaciones_path, index=False)
        st.success("Observación registrada correctamente")
    st.subheader("Historial de observaciones")
    st.dataframe(observaciones)

elif menu == "Agregar registros":
    st.subheader("Agregar nuevos registros al sistema")
    tab1, tab2, tab3 = st.tabs(["➕ Nueva máquina", "➕ Nueva tarea", "➕ Nuevo repuesto"])

    with tab1:
        st.markdown("### Nueva máquina")
        new_id = st.text_input("ID de máquina")
        new_nombre = st.text_input("Nombre")
        new_sector = st.text_input("Sector")
        new_estado = st.selectbox("Estado", ["Operativa", "En mantenimiento", "Fuera de servicio"])
        if st.button("Agregar máquina"):
            nueva = pd.DataFrame([[new_id, new_nombre, new_sector, new_estado]], columns=maquinas.columns)
            maquinas = pd.concat([maquinas, nueva], ignore_index=True)
            maquinas.to_csv(maquinas_path, index=False)
            st.success(f"Máquina '{new_nombre}' agregada correctamente")

    with tab2:
        st.markdown("### Nueva tarea de mantenimiento")
        id_maquina = st.selectbox("Máquina (ID)", maquinas["ID"])
        tarea = st.text_input("Tarea")
        frecuencia = st.text_input("Frecuencia (ej: semanal, mensual, 1200h)")
        ultima = st.date_input("Última ejecución", value=datetime.date.today())
        if st.button("Agregar tarea"):
            nueva = pd.DataFrame([[len(tareas)+1, id_maquina, tarea, frecuencia, ultima]], columns=tareas.columns)
            tareas = pd.concat([tareas, nueva], ignore_index=True)
            tareas.to_csv(tareas_path, index=False)
            st.success(f"Tarea '{tarea}' agregada a máquina {id_maquina}")

    with tab3:
        st.markdown("### Nuevo repuesto o lubricante")
        repuesto = st.text_input("Nombre del repuesto")
        tipo = st.selectbox("Tipo", ["Repuesto", "Insumo", "Consumible"])
        cantidad = st.number_input("Cantidad", min_value=1, step=1)
        ubicacion = st.text_input("Ubicación física")
        if st.button("Agregar repuesto"):
            nuevo = pd.DataFrame([[len(inventario)+1, repuesto, tipo, cantidad, ubicacion]], columns=inventario.columns)
            inventario = pd.concat([inventario, nuevo], ignore_index=True)
            inventario.to_csv(inventario_path, index=False)
            st.success(f"Repuesto '{repuesto}' agregado al inventario")

elif menu == "Exportar PDF":
    st.subheader("Exportar stock a PDF")
    if "Tipo" in inventario.columns:
        tipo_seleccionado = st.selectbox("Seleccionar tipo de stock a exportar", inventario["Tipo"].unique())
        df = inventario[inventario["Tipo"] == tipo_seleccionado]

        if st.button("Generar PDF"):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt=f"Stock: {tipo_seleccionado}", ln=True, align='C')
            pdf.cell(200, 10, txt=f"Fecha: {datetime.date.today()}", ln=True, align='C')
            pdf.ln(10)

            for index, row in df.iterrows():
                linea = f"{row['Nombre']} - Cantidad: {row['Cantidad']} - Ubicación: {row['Máquina_asociada']}"
                pdf.cell(200, 10, txt=linea, ln=True)

            pdf_path = os.path.join(DATA_FOLDER, f"stock_{tipo_seleccionado}.pdf")
            pdf.output(pdf_path)
            with open(pdf_path, "rb") as f:
                st.download_button("📥 Descargar PDF", f, file_name=f"stock_{tipo_seleccionado}.pdf")

