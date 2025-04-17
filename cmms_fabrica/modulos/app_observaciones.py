import streamlit as st
import pandas as pd
from datetime import datetime
from modulos.conexion_mongo import db

def cargar_observaciones():
    return list(db["observaciones"].find())

def guardar_observacion(obs):
    db["observaciones"].insert_one(obs)

def actualizar_observacion(id_obs, nuevos_datos):
    db["observaciones"].update_one({"id_obs": id_obs}, {"$set": nuevos_datos})

def crear_tarea_automatica(id_obs, id_maquina, descripcion):
    hoy = datetime.today().strftime("%Y-%m-%d")
    count = db["tareas"].count_documents({})
    nuevo_id_tarea = f"TAR{count + 1:04d}"

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
    db["tareas"].insert_one(nueva_tarea)
    st.success(f"🛠️ Tarea {nuevo_id_tarea} creada automáticamente desde la observación.")

def app_observaciones():
    st.subheader("📝 Observaciones Técnicas")

    data = cargar_observaciones()
    df = pd.DataFrame(data)
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
                if not id_maquina or not descripcion or not autor:
                    st.error("⚠️ Completá todos los campos obligatorios: Máquina, Descripción y Autor.")
                elif id_obs in df["id_obs"].values:
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
                    guardar_observacion(nueva_obs)
                    st.success("✅ Observación agregada correctamente.")

                    if crear_tarea == "sí":
                        crear_tarea_automatica(id_obs, id_maquina, descripcion)

                    st.experimental_rerun()

            if not df.empty:
                st.divider()
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
                    nuevos_datos = {
                        "id_maquina": id_maquina,
                        "descripcion": descripcion,
                        "criticidad": criticidad,
                        "estado": estado,
                        "crear_tarea": crear_tarea,
                        "tarea_relacionada": tarea_relacionada,
                        "autor": autor
                    }
                    actualizar_observacion(id_sel, nuevos_datos)
                    st.success("✅ Observación actualizada correctamente.")
                    st.rerun()
        else:
            st.info("👁️ Solo técnicos o administradores pueden agregar o editar observaciones.")
