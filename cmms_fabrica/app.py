import streamlit as st
st.set_page_config(page_title="CMMS Fábrica", layout="wide")

# 🔐 Login y cierre de sesión
from modulos.app_login import login_usuario, cerrar_sesion
from modulos.conexion_mongo import db

# 💄 Estilos responsive
from modulos.estilos import aplicar_estilos

# Nuevos módulos CRUD centrados en activos técnicos
from crud.crud_activos_tecnicos import app as crud_activos_tecnicos
from crud.crud_planes_preventivos import app as crud_planes_preventivos
from crud.crud_tareas_correctivas import app as crud_tareas_correctivas
from crud.crud_tareas_tecnicas import app as crud_tareas_tecnicas
from crud.crud_observaciones import app as crud_observaciones
from crud.crud_calibraciones_instrumentos import app as crud_calibraciones
from crud.crud_servicios_externos import app as crud_servicios
from crud.dashboard_kpi_historial import app as kpi_historial
from crud.crud_inventario import app_inventario

# Módulo de usuarios (admin)
from modulos.app_usuarios import app_usuarios

# Gestión de IDs manuales
from modulos.cambiar_ids import app as cambiar_ids

# Reportes técnicos
from modulos.app_reportes import app as app_reportes

# Asistentes GPT
from modulos.app_asistente_tecnico import app as asistente_tecnico
from modulos.app_mejora import app as asistente_mejora

# 📱 Estilos
aplicar_estilos()

# 🔐 Login de usuario
usuario, rol = login_usuario()
if not usuario:
    st.stop()

# 🚪 Botón de cerrar sesión
with st.sidebar:
    st.divider()
    st.markdown(f"👤 **{usuario}** ({rol})")
    st.button("Cerrar sesión", on_click=cerrar_sesion, use_container_width=True)

# 📋 Menú lateral
menu = [
    "🏠 Inicio",
    "🧱 Activos Técnicos",
    "📑 Planes Preventivos",
    "🚨 Tareas Correctivas",
    "📂 Tareas Técnicas",
    "🔍 Observaciones Técnicas",
    "📦 Inventario Técnico",
    "🧪 Calibraciones",
    "🏢 Servicios Técnicos",
    "📊 KPIs Globales",
    "📄 Reportes Técnicos",
    "🤖 Asistente Técnico",
    "🧰 Asistente de Mejora Continua",
    "🆔 Cambiar IDs manuales" if rol == "admin" else None,
    "👥 Usuarios" if rol == "admin" else None,
]
menu = [m for m in menu if m is not None]

opcion = st.sidebar.radio("Menú principal", menu)

# 🧭 Enrutamiento
if opcion == "🏠 Inicio":
    st.title("Bienvenido al CMMS de la Fábrica")
    kpi_historial()

    if rol == "admin":
        st.markdown("## 🧹 Mantenimiento de Almacenamiento (MongoDB)")
        from modulos.almacenamiento import (
            obtener_tamano_total_mb,
            listar_colecciones_ordenadas,
            limpiar_coleccion_mas_cargada
        )
        uso_actual = obtener_tamano_total_mb()
        st.markdown(f"**Uso actual estimado de la base de datos:** `{uso_actual:.2f} MB`")
        st.markdown("### 📁 Colecciones rotables ordenadas por carga:")
        datos = listar_colecciones_ordenadas()
        for nombre, cantidad, _ in datos:
            st.write(f"- `{nombre}` → {cantidad} documentos")
        if st.button("🧹 Ejecutar limpieza automática"):
            resultado = limpiar_coleccion_mas_cargada()
            if resultado:
                nombre, cantidad = resultado
                st.success(f"✅ Se eliminaron {cantidad} documentos antiguos de `{nombre}`.")
            else:
                st.info("ℹ️ No se requería limpieza: colecciones por debajo del mínimo.")

elif opcion == "🧱 Activos Técnicos":
    crud_activos_tecnicos()

elif opcion == "📑 Planes Preventivos":
    crud_planes_preventivos()

elif opcion == "🚨 Tareas Correctivas":
    crud_tareas_correctivas()

elif opcion == "📂 Tareas Técnicas":
    crud_tareas_tecnicas()

elif opcion == "🔍 Observaciones Técnicas":
    crud_observaciones()

elif opcion == "📦 Inventario Técnico":
    app_inventario(usuario)

elif opcion == "🧪 Calibraciones":
    crud_calibraciones()

elif opcion == "🏢 Servicios Técnicos":
    crud_servicios()

elif opcion == "📊 KPIs Globales":
    kpi_historial()

elif opcion == "📄 Reportes Técnicos":
    app_reportes()

elif opcion == "🤖 Asistente Técnico":
    asistente_tecnico()

elif opcion == "🧰 Asistente de Mejora Continua":
    asistente_mejora()

elif opcion == "🆔 Cambiar IDs manuales":
    cambiar_ids()

elif opcion == "👥 Usuarios" and rol == "admin":
    app_usuarios(usuario, rol)
