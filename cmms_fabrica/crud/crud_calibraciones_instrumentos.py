import streamlit as st
from datetime import datetime
from modulos.conexion_mongo import db

coleccion = db["calibraciones"]

def app():
        
    st.title("🧪 Gestión de Calibraciones de Instrumentos")
    
    menu = ["Registrar Calibración", "Ver Calibraciones", "Editar Calibración", "Eliminar Calibración"]
    choice = st.sidebar.selectbox("Acción", menu)
    
    # Formulario de calibración
    def form_calibracion(defaults=None):
        with st.form("form_calibracion"):
            id_activo = st.text_input("ID del Instrumento", value=defaults.get("id_activo_tecnico") if defaults else "")
            fecha_calibracion = st.date_input("Fecha de Calibración", value=defaults.get("fecha_calibracion") if defaults else datetime.today())
            responsable = st.text_input("Responsable de Calibración", value=defaults.get("responsable") if defaults else "")
            proveedor_externo = st.text_input("Proveedor Externo (si aplica)", value=defaults.get("proveedor_externo") if defaults else "")
            resultado = st.selectbox("Resultado", ["Correcta", "Desviación leve", "Desviación crítica"],
                                     index=["Correcta", "Desviación leve", "Desviación crítica"].index(defaults.get("resultado")) if defaults else 0)
            acciones = st.text_area("Acciones Derivadas", value=defaults.get("acciones") if defaults else "")
            observaciones = st.text_area("Observaciones", value=defaults.get("observaciones") if defaults else "")
            usuario = st.text_input("Usuario que registra", value=defaults.get("usuario_registro") if defaults else "")
            submit = st.form_submit_button("Guardar Calibración")
    
        if submit:
            data = {
                "id_activo_tecnico": id_activo,
                "fecha_calibracion": str(fecha_calibracion),
                "responsable": responsable,
                "proveedor_externo": proveedor_externo,
                "resultado": resultado,
                "acciones": acciones,
                "observaciones": observaciones,
                "usuario_registro": usuario,
                "fecha_registro": datetime.now()
            }
            return data
        return None
    
    # Registrar calibración
    if choice == "Registrar Calibración":
        st.subheader("➕ Nueva Calibración")
        data = form_calibracion()
        if data:
            coleccion.insert_one(data)
            st.success("Calibración registrada correctamente.")
    
    # Ver calibraciones
    elif choice == "Ver Calibraciones":
        st.subheader("📋 Calibraciones Registradas")
        calibraciones = list(coleccion.find().sort("fecha_calibracion", -1))
        for c in calibraciones:
            st.markdown(f"**{c['id_activo_tecnico']}** ({c['resultado']}) - {c['fecha_calibracion']}")
            st.write(c['observaciones'])
            st.write("---")
    
    # Editar calibración
    elif choice == "Editar Calibración":
        st.subheader("✏️ Editar Calibración")
        calibraciones = list(coleccion.find())
        opciones = {f"{c['id_activo_tecnico']} - {c['fecha_calibracion']}": c for c in calibraciones}
        seleccion = st.selectbox("Seleccionar calibración", list(opciones.keys()))
        datos = opciones[seleccion]
    
        nuevos_datos = form_calibracion(defaults=datos)
        if nuevos_datos:
            coleccion.update_one({"_id": datos["_id"]}, {"$set": nuevos_datos})
            st.success("Calibración actualizada correctamente.")
    
    # Eliminar calibración
    elif choice == "Eliminar Calibración":
        st.subheader("🗑️ Eliminar Calibración")
        calibraciones = list(coleccion.find())
        opciones = {f"{c['id_activo_tecnico']} - {c['fecha_calibracion']}": c for c in calibraciones}
        seleccion = st.selectbox("Seleccionar calibración", list(opciones.keys()))
        datos = opciones[seleccion]
        if st.button("Eliminar definitivamente"):
            coleccion.delete_one({"_id": datos["_id"]})
            st.success("Calibración eliminada.")
        
if __name__ == "__main__":
    app()
