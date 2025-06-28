"""
🗓️ CRUD de Planes Preventivos – CMMS Fábrica

Este módulo permite registrar, visualizar, editar y eliminar planes preventivos asociados a activos técnicos.
Soporta activos jerárquicos mediante el campo `pertenece_a`, reflejando relaciones funcionales entre equipos.
Cada acción se registra en la colección `historial` para trazabilidad operativa y auditorías.

✅ Normas aplicables:
- ISO 55001 (Gestión del ciclo de vida del activo)
- ISO 9001:2015 (Gestión de planificación, ejecución y control)
- ISO 14224 (Mantenimiento preventivo documentado y rastreable)
"""

import streamlit as st
from datetime import datetime
from modulos.conexion_mongo import db
from crud.generador_historial import generar_id, registrar_evento_historial

coleccion = db["planes_preventivos"]

def app():
    st.title("🗓️ Gestión de Planes Preventivos")

    menu = ["Registrar Plan", "Ver Planes", "Editar Plan", "Eliminar Plan"]
    choice = st.sidebar.radio("Acción", menu)

    def form_plan(defaults=None):
        with st.form("form_plan_preventivo"):
            id_plan = st.text_input(
                "ID del Plan",
                value=defaults.get("id_plan") if defaults else generar_id("PP"),
            )

            activos = db["activos_tecnicos"]
            activos_lista = list(activos.find({}, {"_id": 0, "id_activo_tecnico": 1, "nombre": 1, "pertenece_a": 1}))
            opciones = []
            map_id = {}
            for a in activos_lista:
                label = f"{a['id_activo_tecnico']} - {a.get('nombre', '')}"
                if "pertenece_a" in a:
                    label += f" (pertenece a {a['pertenece_a']})"
                opciones.append(label)
                map_id[label] = a["id_activo_tecnico"]

            activo_default = None
            if defaults and defaults.get("id_activo_tecnico"):
                for k, v in map_id.items():
                    if v == defaults["id_activo_tecnico"]:
                        activo_default = k
                        break

            id_activo_label = st.selectbox("ID del Activo Técnico", opciones, index=opciones.index(activo_default) if activo_default else 0)
            id_activo = map_id[id_activo_label]

            frecuencia = st.number_input("Frecuencia", min_value=1, value=defaults.get("frecuencia") if defaults else 30)
            unidad = st.selectbox("Unidad de Frecuencia", ["días", "semanas", "meses"],
                                  index=["días", "semanas", "meses"].index(defaults.get("unidad_frecuencia")) if defaults else 2)
            proxima_fecha = st.date_input("Próxima Fecha", value=defaults.get("proxima_fecha") if defaults else datetime.today())
            ultima_fecha = st.date_input("Última Fecha", value=defaults.get("ultima_fecha") if defaults else datetime.today())
            responsable = st.text_input("Responsable", value=defaults.get("responsable") if defaults else "")
            estado = st.selectbox("Estado del Plan", ["Activo", "Suspendido", "Cerrado"],
                                  index=["Activo", "Suspendido", "Cerrado"].index(defaults.get("estado")) if defaults else 0)
            adjunto = st.text_input("Nombre de archivo adjunto (Excel externo)", value=defaults.get("adjunto_plan") if defaults else "")
            proveedor_externo = st.text_input("Proveedor Externo (si aplica)", value=defaults.get("proveedor_externo") if defaults else "")
            observaciones = st.text_area("Observaciones", value=defaults.get("observaciones") if defaults else "")
            usuario = st.text_input("Usuario que registra", value=defaults.get("usuario_registro") if defaults else "")
            submit = st.form_submit_button("Guardar Plan")

        if submit:
            data = {
                "id_plan": id_plan,
                "id_activo_tecnico": id_activo,
                "frecuencia": frecuencia,
                "unidad_frecuencia": unidad,
                "proxima_fecha": str(proxima_fecha),
                "ultima_fecha": str(ultima_fecha),
                "responsable": responsable,
                "estado": estado,
                "adjunto_plan": adjunto,
                "proveedor_externo": proveedor_externo,
                "observaciones": observaciones,
                "usuario_registro": usuario,
                "fecha_registro": datetime.now()
            }
            return data
        return None

    if choice == "Registrar Plan":
        st.subheader("➕ Nuevo Plan Preventivo")
        data = form_plan()
        if data:
            coleccion.insert_one(data)
            registrar_evento_historial(
                "Alta de plan preventivo",
                data["id_activo_tecnico"],
                data["id_plan"],
                f"Plan '{data['id_plan']}' registrado con frecuencia {data['frecuencia']} {data['unidad_frecuencia']}",
                data["usuario_registro"],
            )
            st.success("Plan preventivo registrado correctamente.")

    elif choice == "Ver Planes":
        st.subheader("📋 Planes Preventivos por Activo Técnico")

        planes = list(coleccion.find().sort("proxima_fecha", 1))
        hoy = datetime.today().date()

        if not planes:
            st.info("No hay planes preventivos registrados.")
            return

        estados_existentes = sorted(set(p.get("estado", "Activo") for p in planes))
        estado_filtro = st.selectbox("Filtrar por estado del plan", ["Todos"] + estados_existentes)
        texto_filtro = st.text_input("🔍 Buscar por ID de activo, ID de plan o texto")

        filtrados = []
        for p in planes:
            coincide_estado = (estado_filtro == "Todos") or (p.get("estado") == estado_filtro)
            coincide_texto = texto_filtro.lower() in p.get("id_activo_tecnico", "").lower() or \
                             texto_filtro.lower() in p.get("id_plan", "").lower() or \
                             texto_filtro.lower() in p.get("observaciones", "").lower()
            if coincide_estado and coincide_texto:
                filtrados.append(p)

        if not filtrados:
            st.warning("No se encontraron planes con esos filtros.")
            return

        activos = sorted(set(str(p.get("id_activo_tecnico") or "⛔ Sin ID") for p in filtrados))
        for activo in activos:
            st.markdown(f"### 🏷️ Activo Técnico: `{activo}`")
            planes_activo = [p for p in filtrados if str(p.get("id_activo_tecnico") or "⛔ Sin ID") == activo]

            for p in planes_activo:
                id_plan = p.get("id_plan", "Sin ID")
                estado = p.get("estado", "Sin Estado")
                proxima_fecha = p.get("proxima_fecha", "Sin Fecha")
                observaciones = p.get("observaciones", "")

                try:
                    fecha_obj = datetime.strptime(proxima_fecha, "%Y-%m-%d").date() if isinstance(proxima_fecha, str) else proxima_fecha
                except:
                    fecha_obj = None

                vencido = fecha_obj and fecha_obj < hoy

                st.code(f"ID del Plan: {id_plan}", language="yaml")
                if vencido:
                    st.markdown(
                        f"<span style='color:red; font-weight:bold'>🚨 {id_plan} ({estado}) - VENCIDO el {proxima_fecha}</span>",
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(f"**{id_plan}** ({estado}) - Próxima: {proxima_fecha}")
                st.write(observaciones)
            st.markdown("---")

    elif choice == "Editar Plan":
        st.subheader("✏️ Editar Plan Preventivo")
        planes = list(coleccion.find())
        opciones = {f"{p['id_plan']} - {p['id_activo_tecnico']}": p for p in planes}
        if not opciones:
            st.warning("No hay planes para editar.")
            return
        seleccion = st.selectbox("Seleccionar plan", list(opciones.keys()))
        datos = opciones[seleccion]
        nuevos_datos = form_plan(defaults=datos)
        if nuevos_datos:
            coleccion.update_one({"_id": datos["_id"]}, {"$set": nuevos_datos})
            registrar_evento_historial(
                "Edición de plan preventivo",
                nuevos_datos["id_activo_tecnico"],
                nuevos_datos["id_plan"],
                f"Plan '{nuevos_datos['id_plan']}' fue editado",
                nuevos_datos["usuario_registro"],
            )
            st.success("Plan actualizado correctamente.")

    elif choice == "Eliminar Plan":
        st.subheader("🗑️ Eliminar Plan Preventivo")
        planes = list(coleccion.find())
        opciones = {f"{p['id_plan']} - {p['id_activo_tecnico']}": p for p in planes}
        if not opciones:
            st.warning("No hay planes para eliminar.")
            return
        seleccion = st.selectbox("Seleccionar plan", list(opciones.keys()))
        datos = opciones[seleccion]
        if st.button("Eliminar definitivamente"):
            coleccion.delete_one({"_id": datos["_id"]})
            registrar_evento_historial(
                "Baja de plan preventivo",
                datos.get("id_activo_tecnico"),
                datos.get("id_plan"),
                f"Se eliminó el plan '{datos.get('id_plan', '')}'",
                datos.get("usuario_registro", "desconocido"),
            )
            st.success("Plan eliminado. Actualizá la vista para confirmar.")

if __name__ == "__main__":
    app()
