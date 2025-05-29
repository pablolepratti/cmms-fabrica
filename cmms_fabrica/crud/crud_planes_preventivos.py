import streamlit as st
from datetime import datetime
from modulos.conexion_mongo import db

coleccion = db["planes_preventivos"]

def app():

    st.title("🗓️ Gestión de Planes Preventivos")
    
    menu = ["Registrar Plan", "Ver Planes", "Editar Plan", "Eliminar Plan"]
    choice = st.sidebar.selectbox("Acción", menu)
    
    # Formulario de plan preventivo
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
    
    # Registrar plan
    if choice == "Registrar Plan":
        st.subheader("➕ Nuevo Plan Preventivo")
        data = form_plan()
        if data:
            coleccion.insert_one(data)
            st.success("Plan preventivo registrado correctamente.")
    
    # Ver planes
    elif choice == "Ver Planes":
        st.subheader("📋 Planes Preventivos Registrados")
        planes = list(coleccion.find().sort("proxima_fecha", 1))
        for p in planes:
            st.markdown(f"**{p['id_plan']}** ({p['estado']}) - Próxima: {p['proxima_fecha']}")
            st.write(p['observaciones'])
            st.write("---")
    
    # Editar plan
    elif choice == "Editar Plan":
        st.subheader("✏️ Editar Plan Preventivo")
        planes = list(coleccion.find())
        opciones = {f"{p['id_plan']} - {p['id_activo_tecnico']}": p for p in planes}
        seleccion = st.selectbox("Seleccionar plan", list(opciones.keys()))
        datos = opciones[seleccion]
    
        nuevos_datos = form_plan(defaults=datos)
        if nuevos_datos:
            coleccion.update_one({"_id": datos["_id"]}, {"$set": nuevos_datos})
            st.success("Plan actualizado correctamente.")
    
    # Eliminar plan
    elif choice == "Eliminar Plan":
        st.subheader("🗑️ Eliminar Plan Preventivo")
        planes = list(coleccion.find())
        opciones = {f"{p['id_plan']} - {p['id_activo_tecnico']}": p for p in planes}
        seleccion = st.selectbox("Seleccionar plan", list(opciones.keys()))
        datos = opciones[seleccion]
        if st.button("Eliminar definitivamente"):
            coleccion.delete_one({"_id": datos["_id"]})
            st.success("Plan eliminado.")

if __name__ == "__main__":
    app()
