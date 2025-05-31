"""
🗓️ CRUD de Planes Preventivos – CMMS Fábrica

Este módulo permite registrar, visualizar, editar y eliminar planes preventivos asociados a activos técnicos.
Cada acción se registra en la colección `historial` para trazabilidad operativa y auditorías.

✅ Normas aplicables:
- ISO 55001 (Gestión del ciclo de vida del activo)
- ISO 9001:2015 (Gestión de planificación, ejecución y control)
- ISO 14224 (Mantenimiento preventivo documentado y rastreable)
"""

import streamlit as st
from datetime import datetime
from modulos.conexion_mongo import db

coleccion = db["planes_preventivos"]
historial = db["historial"]

def registrar_evento_historial(evento):
    historial.insert_one({
        "tipo_evento": evento["tipo_evento"],
        "id_activo_tecnico": evento.get("id_activo_tecnico"),
        "descripcion": evento.get("descripcion", ""),
        "usuario": evento.get("usuario"),
        "fecha_evento": datetime.now(),
        "modulo": "planes_preventivos"
    })

def app():
    st.title("🗓️ Gestión de Planes Preventivos")

    menu = ["Registrar Plan", "Ver Planes", "Editar Plan", "Eliminar Plan"]
    choice = st.sidebar.radio("Acción", menu)

    def form_plan(defaults=None):
        with st.form("form_plan_preventivo"):
            id_plan = st.text_input("ID del Plan", value=defaults.get("id_plan") if defaults else "")
            id_activo = st.text_input("ID del Activo Técnico", value=defaults.get("id_activo_tecnico") if defaults else "")
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
            registrar_evento_historial({
                "tipo_evento": "Alta de plan preventivo",
                "id_activo_tecnico": data["id_activo_tecnico"],
                "usuario": data["usuario_registro"],
                "descripcion": f"Plan '{data['id_plan']}' registrado con frecuencia {data['frecuencia']} {data['unidad_frecuencia']}"
            })
            st.success("Plan preventivo registrado correctamente.")

    elif choice == "Ver Planes":
        st.subheader("📋 Planes Preventivos por Activo Técnico")
        st.markdown("<br>", unsafe_allow_html=True)

        planes = list(coleccion.find().sort("proxima_fecha", 1))
        hoy = datetime.today().date()

        if planes:
            activos = sorted(set(str(p.get("id_activo_tecnico") or "⛔ Sin ID") for p in planes))
            for activo in activos:
                st.markdown(f"### 🏷️ Activo Técnico: `{activo}`")
                planes_activo = [p for p in planes if str(p.get("id_activo_tecnico") or "⛔ Sin ID") == activo]

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

                    if vencido:
                        st.markdown(
                            f"<span style='color:red; font-weight:bold'>🚨 {id_plan} ({estado}) - VENCIDO el {proxima_fecha}</span>",
                            unsafe_allow_html=True
                        )
                    else:
                        st.markdown(f"**{id_plan}** ({estado}) - Próxima: {proxima_fecha}")

                    st.write(observaciones)
                st.markdown("---")
        else:
            st.info("No hay planes preventivos registrados.")

    elif choice == "Editar Plan":
        st.subheader("✏️ Editar Plan Preventivo")
        planes = list(coleccion.find())
        opciones = {f"{p['id_plan']} - {p['id_activo_tecnico']}": p for p in planes}
        seleccion = st.selectbox("Seleccionar plan", list(opciones.keys()))
        datos = opciones[seleccion]
        nuevos_datos = form_plan(defaults=datos)
        if nuevos_datos:
            coleccion.update_one({"_id": datos["_id"]}, {"$set": nuevos_datos})
            registrar_evento_historial({
                "tipo_evento": "Edición de plan preventivo",
                "id_activo_tecnico": nuevos_datos["id_activo_tecnico"],
                "usuario": nuevos_datos["usuario_registro"],
                "descripcion": f"Plan '{nuevos_datos['id_plan']}' fue editado"
            })
            st.success("Plan actualizado correctamente.")

    elif choice == "Eliminar Plan":
        st.subheader("🗑️ Eliminar Plan Preventivo")
        planes = list(coleccion.find())
        opciones = {f"{p['id_plan']} - {p['id_activo_tecnico']}": p for p in planes}
        seleccion = st.selectbox("Seleccionar plan", list(opciones.keys()))
        datos = opciones[seleccion]
        if st.button("Eliminar definitivamente"):
            coleccion.delete_one({"_id": datos["_id"]})
            registrar_evento_historial({
                "tipo_evento": "Baja de plan preventivo",
                "id_activo_tecnico": datos.get("id_activo_tecnico"),
                "usuario": datos.get("usuario_registro", "desconocido"),
                "descripcion": f"Se eliminó el plan '{datos.get('id_plan', '')}'"
            })
            st.success("Plan eliminado.")

if __name__ == "__main__":
    app()
