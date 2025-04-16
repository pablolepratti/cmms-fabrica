import streamlit as st
import pandas as pd
import os
from datetime import datetime

DATA_PATH = "data/observaciones.csv"
TAREAS_PATH = "data/tareas.csv"

def cargar_observaciones():
    columnas = [
        "id_obs", "id_maquina", "fecha", "descripcion", "autor",
        "criticidad", "crear_tarea", "estado", "tarea_relacionada"
    ]
    if os.path.exists(DATA_PATH):
        return pd.read_csv(DATA_PATH)
    else:
        return pd.DataFrame(columns=columnas)

def guardar_observaciones(df):
    df.to_csv(DATA_PATH, index=False)

def crear_tarea_automatica(id_obs, id_maquina, descripcion):
    if os.path.exists(TAREAS_PATH):
        df_tareas = pd.read_csv(TAREAS_PATH)
    else:
        df_tareas = pd.DataFrame(columns=[
            "id_tarea", "id_maquina", "descripcion", "tipo_tarea", "origen",
            "ultima_ejecucion", "proxima_ejecucion", "estado", "observaciones"
        ])
    
    nuevo_id_tarea = f"TAR{len(df_tareas)+1:04d}"
    hoy = datetime.today().strftime("%Y-%m-%d")

    nueva_tarea = {
        "id_tarea": nuevo_id_tarea,
        "id_maquina": id_maquina,
        "descripcion": f"[Desde observación {id_obs}] {descripcion}",
        "tipo_tarea": "correctiva",
        "origen": "observacion",
        "ultima_ejecucion": hoy,
        "proxima_ejecucion": hoy,
        "estado": "pendiente",
        "observaciones": f"Generada automáticamente desde observación {id_obs}"
    }

    df_tareas = pd.concat([df_tareas, pd.DataFrame([nueva_tarea])], ignore_index=True)
    df_tareas.to_csv(TAREAS_PATH, index=False)
    st.success(f"🛠️ Tarea {nuevo_id_tarea} creada automáticamente desde la observación.")

def app_observaciones():
    st.subheader("📝 Observaciones Técnicas")

    df = cargar_observaciones()
    rol = st.session_state.get("rol", "invitado")
    tabs = st.tabs(["📄 Ver Observaciones", "🛠️ Administrar Observaciones"])

    with tabs[0]:
        if df.empty:
            st.warning("No hay observaciones registradas.")
        else:
            crit = st.selectbox("Filtrar por criticidad", ["Todas", "baja", "media", "alta"])
            estado = st.selectbox("Filtrar por estado", ["Todas", "pendiente", "resuelta", "descartada"])

            df_filtrado = df.copy()
            if crit != "Todas":
                df_filtrado = df_filtrado[df_filtrado["criticidad"] == crit]
            if estado != "Todas":
                df_filtrado = df_filtrado[df_filtrado["estado"] == estado]

            st.dataframe(df_filtrado.sort_values("fecha", ascending=False), use_container_width=True)

    with tabs[1]:
        if rol in ["admin", "tecnico"]:
            st.markdown("### ➕ Agregar nueva observación")

            nuevo_id = f"OBS{len(df)+1:04d}"
            with st.form("form_nueva_obs"):
                col1, col2 = st.columns(2)
                with col1:
                    st.text_input("ID de observación", value=nuevo_id, disabled=True)
                    id_obs = nuevo_id
                    id_maquina = st.text_input("Máquina o sistema")
                    descripcion = st.text_area("Descripción")
                    criticidad = st.selectbox("Criticidad", ["baja", "media", "alta"])
                with col2:
                    estado = st.selectbox("Estado actual", ["pendiente", "resuelta", "descartada"])
                    crear_tarea = st.selectbox("¿Convertir en tarea correctiva?", ["no", "sí"])
                    tarea_relacionada = st.text_input("ID de tarea relacionada (opcional)")
                    autor = st.text_input("Autor")

                submitted = st.form_submit_button("Agregar observación")

            if submitted:
                if id_obs in df["id_obs"].values:
                    st.error("⚠️ Ya existe una observación con ese ID.")
                else:
                    nueva_obs = {
                        "id_obs": id_obs,
                        "id_maquina": id_maquina,
                        "fecha": datetime.today().strftime("%Y-%m-%d"),
                        "descripcion": descripcion,
                        "autor": autor,
                        "criticidad": criticidad,
                        "crear_tarea": crear_tarea,
                        "estado": estado,
                        "tarea_relacionada": tarea_relacionada
                    }
                    df = pd.concat([df, pd.DataFrame([nueva_obs])], ignore_index=True)
                    guardar_observaciones(df)
                    st.success("✅ Observación agregada correctamente.")

                    if crear_tarea == "sí":
                        crear_tarea_automatica(id_obs, id_maquina, descripcion)

            if not df.empty:
                st.markdown("### ✏️ Editar observación existente")
                id_sel = st.selectbox("Seleccionar observación por ID", df["id_obs"].tolist())
                datos = df[df["id_obs"] == id_sel].iloc[0]

                with st.form("editar_obs"):
                    id_maquina = st.text_input("Máquina o sistema", value=datos["id_maquina"])
                    descripcion = st.text_area("Descripción", value=datos["descripcion"])
                    criticidad = st.selectbox("Criticidad", ["baja", "media", "alta"], index=["baja", "media", "alta"].index(datos["criticidad"]))
                    estado = st.selectbox("Estado", ["pendiente", "resuelta", "descartada"], index=["pendiente", "resuelta", "descartada"].index(datos["estado"]))
                    crear_tarea = st.selectbox("¿Convertir en tarea?", ["no", "sí"], index=0 if datos["crear_tarea"] == "no" else 1)
                    tarea_relacionada = st.text_input("Tarea relacionada", value=datos["tarea_relacionada"])
                    autor = st.text_input("Autor", value=datos["autor"])
                    update = st.form_submit_button("Actualizar")

                if update:
                    df.loc[df["id_obs"] == id_sel, "id_maquina"] = id_maquina
                    df.loc[df["id_obs"] == id_sel, "descripcion"] = descripcion
                    df.loc[df["id_obs"] == id_sel, "criticidad"] = criticidad
                    df.loc[df["id_obs"] == id_sel, "estado"] = estado
                    df.loc[df["id_obs"] == id_sel, "crear_tarea"] = crear_tarea
                    df.loc[df["id_obs"] == id_sel, "tarea_relacionada"] = tarea_relacionada
                    df.loc[df["id_obs"] == id_sel, "autor"] = autor
                    guardar_observaciones(df)
                    st.success("✅ Observación actualizada correctamente.")
        else:
            st.info("👁️ Solo técnicos o administradores pueden agregar o editar observaciones.")

