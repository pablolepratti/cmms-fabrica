import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import calplot
from datetime import datetime, timedelta
from modulos.conexion_mongo import db

coleccion_plan = db["plan_semana"]
coleccion_tareas = db["tareas"]
coleccion_mantenimientos = db["mantenimientos"]
coleccion_tecnicas = db["tareas_tecnicas"]

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
    tecnicas_abiertas = pd.DataFrame(list(coleccion_tecnicas.find({"estado": {"$ne": "Finalizada"}}, {"_id": 0})))

    for df in [plan, tareas_pendientes, mantenimientos, tecnicas_abiertas]:
        for col in df.columns:
            if "id" in col.lower():
                df[col] = df[col].astype(str)

    tabs = st.tabs(["📄 Ver Semana", "🛠️ Planificar Semana", "📆 Calendario Mensual"])

    # TAB 1: Ver planificación
    with tabs[0]:
        st.markdown("### 📆 Semana actual")
        df_semana = plan[plan["fecha"].isin(fechas)]
        if df_semana.empty:
            st.info("No hay actividades cargadas para esta semana.")
        else:
            st.dataframe(df_semana.sort_values("fecha"), use_container_width=True)

            st.divider()
            st.markdown("### 🗑️ Eliminar planificación")
            df_semana["opcion"] = df_semana["fecha"] + " – " + df_semana["actividad"]
            selected = st.selectbox("Seleccionar planificación", df_semana["opcion"].tolist())
            if st.button("Eliminar planificación seleccionada"):
                fila = df_semana[df_semana["opcion"] == selected].iloc[0]
                coleccion_plan.delete_one({"fecha": fila["fecha"], "actividad": fila["actividad"]})
                st.success("🗑️ Planificación eliminada correctamente.")
                st.rerun()

    # TAB 2: Planificar tareas correctivas, preventivas y técnicas
    with tabs[1]:
        # Tareas correctivas
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
                        st.rerun()

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
                        st.rerun()

        st.markdown("---")
        st.markdown("### 🧠 Agendar tareas técnicas abiertas")

        if tecnicas_abiertas.empty:
            st.info("No hay tareas técnicas abiertas.")
        else:
            tecnicas_abiertas = tecnicas_abiertas.reset_index(drop=True)
            seleccionadas_tec = st.multiselect(
                "Seleccionar tareas técnicas a planificar",
                tecnicas_abiertas.index,
                format_func=lambda i: f"{tecnicas_abiertas.loc[i, 'id_tarea']} – {tecnicas_abiertas.loc[i, 'descripcion'][:40]}"
            )

            if seleccionadas_tec:
                with st.form("form_planificar_tec"):
                    fecha_tec = st.selectbox("Día para asignar tareas técnicas", fechas, format_func=lambda x: f"{x} ({dias_semana[fechas.index(x)]})")
                    responsable_tec = st.text_input("Responsable para tareas técnicas")
                    notas_tec = st.text_area("Observaciones generales para tareas técnicas")
                    confirmar_tec = st.form_submit_button("✅ Agendar tareas técnicas seleccionadas")

                if confirmar_tec:
                    if not responsable_tec:
                        st.error("⚠️ Debes ingresar un responsable.")
                    else:
                        nuevas = []
                        for i in seleccionadas_tec:
                            tec = tecnicas_abiertas.loc[i]
                            nuevas.append({
                                "fecha": fecha_tec,
                                "dia": dias_semana[fechas.index(fecha_tec)],
                                "actividad": f"[TECNICA] {tec['tipo']} – {tec['descripcion'][:40]}",
                                "equipo": tec.get("equipo_asociado", "-"),
                                "estado": "pendiente",
                                "notas": f"ID: {tec['id_tarea']} – Responsable: {responsable_tec} – {notas_tec}"
                            })
                        coleccion_plan.insert_many(nuevas)
                        st.success(f"✅ {len(nuevas)} tarea(s) técnica(s) planificadas correctamente.")
                        st.rerun()

    # TAB 3: Calendario mensual visual
    with tabs[2]:
        st.markdown("### 📆 Calendario mensual de planificación")

        if plan.empty:
            st.info("No hay actividades planificadas.")
        else:
            df_cal = plan.copy()
            df_cal["fecha"] = pd.to_datetime(df_cal["fecha"])
            df_cal["conteo"] = 1
            resumen = df_cal.groupby("fecha").count()

            fig, ax = calplot.calplot(
                resumen["conteo"],
                cmap="YlGnBu",
                colorbar=False,
                suptitle="Días con actividades planificadas",
                figsize=(10, 3)
            )
            st.pyplot(fig)
