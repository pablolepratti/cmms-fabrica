import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from modulos.conexion_mongo import db

coleccion_plan = db["plan_semana"]
coleccion_tareas = db["tareas"]
coleccion_mantenimientos = db["mantenimientos"]

def obtener_semana_actual():
    hoy = datetime.today()
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    dias = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado"]
    return [(inicio_semana + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(6)], dias

def app_semana():
    st.subheader("📅 Planificación de Semana Laboral")

    fechas, dias_semana = obtener_semana_actual()
    plan = pd.DataFrame(list(coleccion_plan.find({}, {"_id": 0})))
    tareas_pendientes = pd.DataFrame(list(coleccion_tareas.find({"estado": "pendiente"}, {"_id": 0})))
    mantenimientos = pd.DataFrame(list(coleccion_mantenimientos.find({}, {"_id": 0})))

    tabs = st.tabs(["📄 Ver Semana", "🛠️ Planificar Semana"])

    # --- TAB 1: VISUALIZACIÓN ---
    with tabs[0]:
        st.markdown("### 📆 Semana actual")
        df_semana = plan[plan["fecha"].isin(fechas)]
        if df_semana.empty:
            st.info("No hay actividades cargadas para esta semana.")
        else:
            st.dataframe(df_semana.sort_values("fecha"), use_container_width=True)

    # --- TAB 2: PLANIFICACIÓN ---
    with tabs[1]:
        st.markdown("### 🛠️ Agendar tareas correctivas")

        if tareas_pendientes.empty:
            st.info("No hay tareas pendientes registradas.")
        else:
            tareas_pendientes = tareas_pendientes.reset_index(drop=True)
            seleccionadas_tareas = st.multiselect(
                "Seleccionar tareas a planificar",
                tareas_pendientes.index,
                format_func=lambda i: f"{tareas_pendientes.loc[i, 'id_tarea']} – {tareas_pendientes.loc[i, 'descripcion'][:40]}"
            )

            if seleccionadas_tareas:
                with st.form("form_planificar_tareas"):
                    fecha_tarea = st.selectbox("Día para asignar tareas", fechas, format_func=lambda x: f"{x} ({dias_semana[fechas.index(x)]})")
                    responsable = st.text_input("Responsable para tareas")
                    notas_tarea = st.text_area("Observaciones generales para tareas")
                    confirmar_tareas = st.form_submit_button("✅ Agendar tareas seleccionadas")

                if confirmar_tareas:
                    if not responsable:
                        st.error("⚠️ Debes ingresar un responsable.")
                    else:
                        nuevas = []
                        for i in seleccionadas_tareas:
                            tarea = tareas_pendientes.loc[i]
                            nuevas.append({
                                "fecha": fecha_tarea,
                                "dia": dias_semana[fechas.index(fecha_tarea)],
                                "actividad": f"[TAREA] {tarea['descripcion']}",
                                "equipo": tarea["id_maquina"],
                                "estado": "pendiente",
                                "notas": f"ID: {tarea['id_tarea']} – Responsable: {responsable} – {notas_tarea}"
                            })
                        coleccion_plan.insert_many(nuevas)
                        st.success(f"✅ {len(nuevas)} tarea(s) planificadas correctamente.")
                        st.experimental_rerun()

        st.markdown("---")
        st.markdown("### 🧰 Agendar mantenimientos programados")

        if mantenimientos.empty:
            st.info("No hay mantenimientos registrados.")
        else:
            mantenimientos = mantenimientos.reset_index(drop=True)
            seleccionados_mant = st.multiselect(
                "Seleccionar mantenimientos a planificar",
                mantenimientos.index,
                format_func=lambda i: f"{mantenimientos.loc[i, 'id_mantenimiento']} – {mantenimientos.loc[i, 'activo'][:40]}"
            )

            if seleccionados_mant:
                with st.form("form_planificar_mant"):
                    fecha_mant = st.selectbox("Día para asignar mantenimientos", fechas, format_func=lambda x: f"{x} ({dias_semana[fechas.index(x)]})")
                    responsable_m = st.text_input("Responsable para mantenimientos")
                    notas_mant = st.text_area("Observaciones generales para mantenimientos")
                    confirmar_mant = st.form_submit_button("✅ Agendar mantenimientos seleccionados")

                if confirmar_mant:
                    if not responsable_m:
                        st.error("⚠️ Debes ingresar un responsable.")
                    else:
                        nuevas = []
                        for i in seleccionados_mant:
                            mant = mantenimientos.loc[i]
                            nuevas.append({
                                "fecha": fecha_mant,
                                "dia": dias_semana[fechas.index(fecha_mant)],
                                "actividad": f"[MANTENIMIENTO] {mant['modo']} – {mant['tipo_activo']}",
                                "equipo": mant["activo"],
                                "estado": "pendiente",
                                "notas": f"ID: {mant['id_mantenimiento']} – Responsable: {responsable_m} – {notas_mant}"
                            })
                        coleccion_plan.insert_many(nuevas)
                        st.success(f"✅ {len(nuevas)} mantenimiento(s) planificados correctamente.")
                        st.experimental_rerun()
