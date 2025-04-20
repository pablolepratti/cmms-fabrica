import streamlit as st
from modulos.cambiar_ids_generales import cambiar_ids_generales

# Suponiendo que tenés otras funciones como: app_maquinas(), app_tareas(), etc.
# Podés agregarlas acá según lo que tengas en tu sistema

st.set_page_config(page_title="CMMS Fábrica", layout="wide")

menu = [
    "🏠 Inicio",
    "📋 Máquinas",
    "📅 Tareas",
    "✏️ Cambiar IDs manuales"
]

seleccion = st.sidebar.selectbox("Menú principal", menu)

if seleccion == "🏠 Inicio":
    st.title("Bienvenido al CMMS de la Fábrica")

elif seleccion == "📋 Máquinas":
    from modulos.app_maquinas import app_maquinas
    app_maquinas()

elif seleccion == "📅 Tareas":
    from modulos.app_tareas import app_tareas
    app_tareas()

elif seleccion == "✏️ Cambiar IDs manuales":
    cambiar_ids_generales()
