from typing import Any, Dict, List

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
from crud.crud_consumos import app as crud_consumos
from crud.dashboard_kpi_historial import app as kpi_historial
from crud.crud_inventario import app_inventario

# Módulo de usuarios (admin)
from modulos.app_usuarios import app_usuarios

# Reportes técnicos
from modulos.app_reportes import app as app_reportes

# Visualización de grafo CMMS
from modulos.app_grafo_cmms import app as app_grafo_cmms

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

# Verificamos la conexión a la base de datos
if db is None:
    st.error("Error: No se pudo conectar a la base de datos MongoDB.")
    st.stop()

def render_home(context: Dict[str, Any]) -> None:
    st.title("Bienvenido al CMMS de la Fábrica")
    kpi_historial()

    if context["rol"] == "admin":
        st.markdown("## 🧹 Mantenimiento de Almacenamiento (MongoDB)")
        from modulos.almacenamiento import (
            listar_colecciones_ordenadas,
            limpiar_coleccion_mas_cargada,
            obtener_tamano_total_mb,
        )

        uso_actual = obtener_tamano_total_mb()
        st.markdown(f"**Uso actual estimado de la base de datos:** `{uso_actual:.2f} MB`")
        st.markdown("### 📁 Colecciones rotables ordenadas por carga:")
        datos = listar_colecciones_ordenadas()
        for nombre, cantidad, campo_fecha, es_critica in datos:
            st.write(f"- `{nombre}` → {cantidad} documentos")
        if st.button("🧹 Ejecutar limpieza automática"):
            resultado = limpiar_coleccion_mas_cargada()
            if resultado:
                nombre, cantidad = resultado
                st.success(f"✅ Se eliminaron {cantidad} documentos antiguos de `{nombre}`.")
            else:
                st.info("ℹ️ No se requería limpieza: colecciones por debajo del mínimo.")

def _render_inventario(context: Dict[str, Any]) -> None:
    app_inventario(context["usuario"])

def _render_consumos(context: Dict[str, Any]) -> None:
    crud_consumos(db, context["usuario"])

def _render_usuarios(context: Dict[str, Any]) -> None:
    app_usuarios(context["usuario"], context["rol"])

MenuEntry = Dict[str, Any]

MENU_CONFIG: List[MenuEntry] = [
    {"label": "🏠 Inicio", "callback": render_home},
    {"label": "🧱 Activos Técnicos", "callback": lambda ctx: crud_activos_tecnicos()},
    {"label": "📑 Planes Preventivos", "callback": lambda ctx: crud_planes_preventivos()},
    {"label": "🚨 Tareas Correctivas", "callback": lambda ctx: crud_tareas_correctivas()},
    {"label": "📂 Tareas Técnicas", "callback": lambda ctx: crud_tareas_tecnicas()},
    {"label": "🔍 Observaciones Técnicas", "callback": lambda ctx: crud_observaciones()},
    {"label": "📦 Inventario Técnico", "callback": _render_inventario},
    {"label": "🧪 Calibraciones", "callback": lambda ctx: crud_calibraciones()},
    {"label": "🏢 Servicios Técnicos", "callback": lambda ctx: crud_servicios()},
    {"label": "⚡ Consumos Técnicos", "callback": _render_consumos},
    {"label": "📊 KPIs Globales", "callback": lambda ctx: kpi_historial()},
    {"label": "📄 Reportes Técnicos", "callback": lambda ctx: app_reportes()},
    {"label": "🗺️ Grafo CMMS", "callback": lambda ctx: app_grafo_cmms()},
    {"label": "🤖 Asistente Técnico", "callback": lambda ctx: asistente_tecnico()},
    {"label": "🧰 Asistente de Mejora Continua", "callback": lambda ctx: asistente_mejora()},
    {"label": "👥 Usuarios", "callback": _render_usuarios, "roles": {"admin"}},
]

def _allowed(entry: MenuEntry, context: Dict[str, Any]) -> bool:
    roles = entry.get("roles")
    if not roles:
        return True
    return context["rol"] in roles

context = {"usuario": usuario, "rol": rol}
menu_entries = [entry for entry in MENU_CONFIG if _allowed(entry, context)]
labels = [entry["label"] for entry in menu_entries]

opcion = st.sidebar.radio("Menú principal", labels)

for entry in menu_entries:
    if entry["label"] == opcion:
        entry["callback"](context)
        break
