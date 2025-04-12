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
    print("🔐 Contraseña recibida:", repr(password))
    if os.path.exists(usuarios_path):
        usuarios = pd.read_csv(usuarios_path)
        hashed = hash_password(password)

        # DEBUG - Mostrar para ver por qué no valida
        print("🧪 DEBUG LOGIN")
        print("Usuario ingresado:", repr(usuario))
        print("Hash generado:", hashed)
        print("Usuarios en CSV:")
        print(usuarios.to_dict(orient="records"))

        match = usuarios[
            (usuarios["usuario"].str.strip() == usuario.strip()) &
            (usuarios["hash_contraseña"].str.strip() == hashed.strip())
        ]
        if not match.empty:
            return match.iloc[0]["rol"]
    return None


# -------------------------------
# Cargar datos desde archivos CSV
# -------------------------------
DATA_FOLDER = "cmms_data"
maquinas_path = os.path.join(DATA_FOLDER, "maquinas.csv")
tareas_path = os.path.join(DATA_FOLDER, "tareas.csv")
inventario_path = os.path.join(DATA_FOLDER, "inventario.csv")
usuarios_path = os.path.join(DATA_FOLDER, "usuarios.csv")
historial_path = os.path.join(DATA_FOLDER, "historial.csv")
observaciones_path = os.path.join(DATA_FOLDER, "observaciones.csv")

# -------------------------------
# Login y control de sesión
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

# -------------------------------
# Si está logueado, mostrar sistema
# -------------------------------
st.sidebar.markdown(f"👤 **{st.session_state.usuario}** ({st.session_state.rol})")
if st.sidebar.button("Cerrar sesión"):
    st.session_state.logueado = False
    st.session_state.usuario = ""
    st.session_state.rol = ""
    st.rerun()

# Crear nuevos usuarios (solo admin Pablo)
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

# Cargar datos
maquinas = pd.read_csv(maquinas_path) if os.path.exists(maquinas_path) else pd.DataFrame()
tareas = pd.read_csv(tareas_path) if os.path.exists(tareas_path) else pd.DataFrame()
inventario = pd.read_csv(inventario_path) if os.path.exists(inventario_path) else pd.DataFrame()
historial = pd.read_csv(historial_path) if os.path.exists(historial_path) else pd.DataFrame(columns=["Tarea", "Fecha", "Usuario"])
observaciones = pd.read_csv(observaciones_path) if os.path.exists(observaciones_path) else pd.DataFrame(columns=["Máquina", "Observación", "Fecha", "Usuario"])

st.title("🛠️ Dashboard de Mantenimiento Preventivo")

menu = st.sidebar.radio("Ir a:", [
    "Inicio", "Máquinas", "Tareas de mantenimiento", "Tareas vencidas",
    "Cargar tarea realizada", "Inventario", "Observaciones técnicas",
    "Agregar registros", "Exportar PDF"])

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
    tareas["Última ejecución"] = pd.to_datetime(tareas["Última ejecución"])
    vencidas = tareas[tareas["Última ejecución"] < (pd.Timestamp(hoy) - pd.Timedelta(days=30))]
    st.dataframe(vencidas)

elif menu == "Cargar tarea realizada":
    st.subheader("Registrar nueva ejecución de tarea")
    tarea = st.selectbox("Tarea a actualizar", tareas["Tarea"])
    fecha = st.date_input("Fecha de realización", value=datetime.date.today())
    if st.button("Registrar"):
        tareas.loc[tareas["Tarea"] == tarea, "Última ejecución"] = fecha
        tareas.to_csv(tareas_path, index=False)

        nuevo_log = pd.DataFrame([[tarea, fecha, st.session_state.usuario]], columns=["Tarea", "Fecha", "Usuario"])
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
        nueva = pd.DataFrame([[maquina, observacion, datetime.date.today(), st.session_state.usuario]], columns=observaciones.columns)
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
        id_maquina = st.selectbox("Máquina", maquinas["ID"])
        tarea = st.text_input("Tarea")
        frecuencia = st.text_input("Frecuencia (ej: semanal, mensual, 1200h)")
        ultima = st.date_input("Última ejecución", value=datetime.date.today())
        if st.button("Agregar tarea"):
            nueva = pd.DataFrame([[id_maquina, tarea, frecuencia, ultima]], columns=tareas.columns)
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
            nuevo = pd.DataFrame([[repuesto, tipo, cantidad, ubicacion]], columns=["Repuesto", "Tipo", "Cantidad", "Ubicación"])
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
                linea = f"{row['Repuesto']} - Cantidad: {row['Cantidad']} - Ubicación: {row['Ubicación']}"
                pdf.cell(200, 10, txt=linea, ln=True)

            pdf_path = os.path.join(DATA_FOLDER, f"stock_{tipo_seleccionado}.pdf")
            pdf.output(pdf_path)
            with open(pdf_path, "rb") as f:
                st.download_button("📥 Descargar PDF", f, file_name=f"stock_{tipo_seleccionado}.pdf")

