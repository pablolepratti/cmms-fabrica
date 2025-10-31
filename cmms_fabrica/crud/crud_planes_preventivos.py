"""
🗓️ CRUD de Planes Preventivos – CMMS Fábrica
Extendido para planes por USO (horas/km/ciclos)

- tiempo  -> como lo tenías
- uso     -> compara lecturas de uso contra un umbral
- ambos   -> vence si vence por fecha O por uso
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date
from modulos.conexion_mongo import db
from crud.generador_historial import registrar_evento_historial
from modulos.utilidades_formularios import select_proveedores_externos


def crear_plan_preventivo(data: dict, database=db):
    if database is None:
        return None
    coleccion = database["planes_preventivos"]
    coleccion.insert_one(data)
    registrar_evento_historial(
        "Alta de plan preventivo",
        data["id_activo_tecnico"],
        data["id_plan"],
        f"Alta de plan para activo: {data['id_activo_tecnico']}",
        data["usuario_registro"],
    )
    return data["id_plan"]


def generar_id_plan():
    return f"PP-{int(datetime.now().timestamp())}"


def app():
    if db is None:
        st.error("MongoDB no disponible")
        return
    coleccion = db["planes_preventivos"]

    st.title("🗓️ Gestión de Planes Preventivos")
    menu = ["Registrar Plan", "Ver Planes", "Planes vencidos", "Editar Plan", "Eliminar Plan"]
    choice = st.sidebar.radio("Acción", menu)

    def form_plan(defaults=None):
        with st.form("form_plan_preventivo"):
            id_plan = st.text_input(
                "ID del Plan",
                value=defaults.get("id_plan") if defaults else generar_id_plan(),
            )

            # activos
            activos_lista = list(
                db["activos_tecnicos"].find(
                    {}, {"_id": 0, "id_activo_tecnico": 1, "nombre": 1}
                )
            )
            opciones = [
                f"{a['id_activo_tecnico']} – {a.get('nombre', 'Sin nombre')}"
                for a in activos_lista
            ]
            map_id = {
                f"{a['id_activo_tecnico']} – {a.get('nombre', 'Sin nombre')}": a[
                    "id_activo_tecnico"
                ]
                for a in activos_lista
            }
            default_id = defaults.get("id_activo_tecnico") if defaults else None
            default_label = next(
                (k for k, v in map_id.items() if v == default_id),
                opciones[0] if opciones else "",
            )
            index_default = (
                opciones.index(default_label) if default_label in opciones else 0
            )

            id_activo_sel = st.selectbox(
                "Activo Técnico asociado", opciones, index=index_default
            )
            id_activo_tecnico = map_id.get(id_activo_sel)

            # 🔁 NUEVO: tipo de programación
            tipo_programacion = st.selectbox(
                "Tipo de programación",
                ["tiempo", "uso", "ambos"],
                index=["tiempo", "uso", "ambos"].index(
                    defaults.get("tipo_programacion", "tiempo")
                )
                if defaults
                else 0,
                help="‘tiempo’: por fecha. ‘uso’: por horas/km. ‘ambos’: el que venza primero.",
            )

            # --- bloque por TIEMPO (igual que antes)
            frecuencia = st.number_input(
                "Frecuencia (para tiempo)",
                min_value=1,
                value=defaults.get("frecuencia", 1) if defaults else 1,
            )
            unidad_frecuencia = st.selectbox(
                "Unidad",
                ["días", "semanas", "meses"],
                index=["días", "semanas", "meses"].index(
                    defaults.get("unidad_frecuencia", "días")
                )
                if defaults
                else 0,
            )
            proxima_fecha = st.date_input(
                "Próxima Ejecución (por tiempo)",
                value=(
                    datetime.strptime(defaults.get("proxima_fecha"), "%Y-%m-%d").date()
                    if defaults and defaults.get("proxima_fecha")
                    else date.today()
                ),
            )
            ultima_fecha = st.date_input(
                "Última Ejecución (por tiempo)",
                value=(
                    datetime.strptime(defaults.get("ultima_fecha"), "%Y-%m-%d").date()
                    if defaults and defaults.get("ultima_fecha")
                    else date.today()
                ),
            )

            # --- 🔁 bloque por USO (nuevo)
            col1, col2 = st.columns(2)
            with col1:
                umbral_uso = st.number_input(
                    "Umbral de uso (ej. 250 h / 500 km)",
                    min_value=0.0,
                    value=float(defaults.get("umbral_uso", 0.0)) if defaults else 0.0,
                )
            with col2:
                unidad_uso = st.text_input(
                    "Unidad de uso", value=defaults.get("unidad_uso", "horas")
                )

            col3, col4 = st.columns(2)
            with col3:
                ultima_lectura_uso = st.number_input(
                    "Lectura al último mantenimiento",
                    min_value=0.0,
                    value=float(defaults.get("ultima_lectura_uso", 0.0))
                    if defaults
                    else 0.0,
                    help="Valor del horómetro/odómetro cuando se hizo la última vez.",
                )
            with col4:
                lectura_actual_uso = st.number_input(
                    "Lectura actual de uso",
                    min_value=0.0,
                    value=float(defaults.get("lectura_actual_uso", 0.0))
                    if defaults
                    else 0.0,
                    help="Cargá la lectura real de hoy. Si no la tenés, dejá el valor anterior.",
                )

            responsable = st.text_input(
                "Responsable", value=defaults.get("responsable", "") if defaults else ""
            )

            tipo_ejecucion = st.radio(
                "¿Quién ejecuta la tarea preventiva?",
                ["Interno", "Externo"],
                index=0
                if defaults is None or defaults.get("proveedor_externo") in [None, ""]
                else 1,
            )

            nombres_proveedores = select_proveedores_externos(db)
            proveedor_default = defaults.get("proveedor_externo") if defaults else None
            index_proveedor = (
                nombres_proveedores.index(proveedor_default)
                if proveedor_default in nombres_proveedores
                else 0
                if nombres_proveedores
                else -1
            )

            if tipo_ejecucion == "Externo":
                proveedor_externo = (
                    st.selectbox(
                        "Proveedor Externo",
                        nombres_proveedores,
                        index=index_proveedor,
                    )
                    if nombres_proveedores
                    else ""
                )
            else:
                proveedor_externo = ""

            estado = st.selectbox(
                "Estado",
                ["Activo", "Suspendido", "Finalizado"],
                index=["Activo", "Suspendido", "Finalizado"].index(
                    defaults.get("estado", "Activo")
                )
                if defaults
                else 0,
            )

            adjunto_plan = st.text_input(
                "Documento o Link del Plan",
                value=defaults.get("adjunto_plan", "") if defaults else "",
            )
            usuario = st.text_input(
                "Usuario que registra",
                value=defaults.get("usuario_registro", "") if defaults else "",
            )
            observaciones = st.text_area(
                "Observaciones", value=defaults.get("observaciones", "") if defaults else ""
            )
            submit = st.form_submit_button("Guardar")

        if submit:
            if not responsable or not usuario:
                st.error("Debe completar los campos obligatorios: Responsable y Usuario.")
                return None

            return {
                "id_plan": id_plan,
                "id_activo_tecnico": id_activo_tecnico,
                "tipo_programacion": tipo_programacion,
                # tiempo
                "frecuencia": frecuencia,
                "unidad_frecuencia": unidad_frecuencia,
                "proxima_fecha": str(proxima_fecha),
                "ultima_fecha": str(ultima_fecha),
                # uso
                "umbral_uso": umbral_uso,
                "unidad_uso": unidad_uso,
                "ultima_lectura_uso": ultima_lectura_uso,
                "lectura_actual_uso": lectura_actual_uso,
                # comunes
                "responsable": responsable,
                "proveedor_externo": proveedor_externo,
                "estado": estado,
                "adjunto_plan": adjunto_plan,
                "usuario_registro": usuario,
                "observaciones": observaciones,
                "fecha_registro": datetime.now(),
            }
        return None

    # --- ACCIONES ---
    if choice == "Registrar Plan":
        st.subheader("➕ Alta de Plan Preventivo")
        data = form_plan()
        if data:
            crear_plan_preventivo(data, db)
            st.success("✅ Plan preventivo registrado correctamente.")

    elif choice == "Ver Planes":
        st.subheader("📋 Planes Preventivos Registrados")
        planes = list(coleccion.find().sort("proxima_fecha", 1))
        if not planes:
            st.info("No hay planes cargados.")
            return

        estados = sorted({p.get("estado", "⛔ Sin Estado") for p in planes})
        estado_filtro = st.selectbox("Filtrar por estado", ["Todos"] + estados)
        query = st.text_input("🔍 Buscar por ID o activo")

        filtrados = []
        for p in planes:
            coincide_estado = estado_filtro == "Todos" or p.get("estado") == estado_filtro
            coincide_texto = (
                query.lower() in p.get("id_plan", "").lower()
                or query.lower() in p.get("id_activo_tecnico", "").lower()
            )
            if coincide_estado and coincide_texto:
                filtrados.append(p)

        if not filtrados:
            st.warning("No se encontraron registros con esos filtros.")
        else:
            agrupados = {}
            for p in filtrados:
                act = p.get("id_activo_tecnico", "⛔ Sin Activo")
                agrupados.setdefault(act, []).append(p)

            for act, lista in sorted(agrupados.items()):
                st.markdown(
                    f"<h4 style='text-align: left; margin-bottom: 0.5em;'>🔹 {act}</h4>",
                    unsafe_allow_html=True,
                )
                for p in lista:
                    freq = f"{p.get('frecuencia', '-') } {p.get('unidad_frecuencia', '-')}"
                    tipo_prog = p.get("tipo_programacion", "tiempo")
                    st.code(f"ID del Plan: {p.get('id_plan', '')}", language="yaml")
                    st.markdown(
                        f"- **Tipo:** {tipo_prog} | **Próxima (tiempo):** {p.get('proxima_fecha', '-')} | **Uso umbral:** {p.get('umbral_uso', '-') } {p.get('unidad_uso', '')} | **Estado:** {p.get('estado', '-')}"
                    )

    elif choice == "Planes vencidos":
        st.subheader("⏰ Planes preventivos vencidos")
        hoy = date.today()
        planes = list(coleccion.find())
        vencidos = []

        for p in planes:
            if p.get("estado") != "Activo":
                continue

            tipo_prog = p.get("tipo_programacion", "tiempo")

            vencio_por_tiempo = False
            vencio_por_uso = False

            # --- tiempo
            if tipo_prog in ("tiempo", "ambos"):
                pf = p.get("proxima_fecha")
                if pf:
                    try:
                        fecha_plan = datetime.strptime(pf, "%Y-%m-%d").date()
                        if fecha_plan < hoy:
                            vencio_por_tiempo = True
                    except ValueError:
                        pass

            # --- uso
            if tipo_prog in ("uso", "ambos"):
                umbral = float(p.get("umbral_uso", 0) or 0)
                ult = float(p.get("ultima_lectura_uso", 0) or 0)
                act = float(p.get("lectura_actual_uso", 0) or 0)
                consumido = act - ult
                if umbral > 0 and consumido >= umbral:
                    vencio_por_uso = True

            if vencio_por_tiempo or vencio_por_uso:
                p["_vencio_por_tiempo"] = vencio_por_tiempo
                p["_vencio_por_uso"] = vencio_por_uso
                vencidos.append(p)

        if not vencidos:
            st.success("👌 No hay planes vencidos (tiempo/uso).")
        else:
            rows = []
            for p in vencidos:
                rows.append(
                    {
                        "id_plan": p.get("id_plan"),
                        "id_activo_tecnico": p.get("id_activo_tecnico"),
                        "tipo_programacion": p.get("tipo_programacion", "tiempo"),
                        "proxima_fecha": p.get("proxima_fecha", ""),
                        "venció_por_tiempo": p.get("_vencio_por_tiempo", False),
                        "umbral_uso": p.get("umbral_uso", ""),
                        "ultima_lectura_uso": p.get("ultima_lectura_uso", ""),
                        "lectura_actual_uso": p.get("lectura_actual_uso", ""),
                        "consumido": (
                            float(p.get("lectura_actual_uso", 0) or 0)
                            - float(p.get("ultima_lectura_uso", 0) or 0)
                        ),
                        "venció_por_uso": p.get("_vencio_por_uso", False),
                        "responsable": p.get("responsable", ""),
                    }
                )
            df = pd.DataFrame(rows)
            st.dataframe(df, use_container_width=True)
            st.info(f"📦 Total de planes vencidos: **{len(vencidos)}**")

    elif choice == "Editar Plan":
        st.subheader("✏️ Editar Plan Preventivo")
        planes = list(coleccion.find())
        opciones = {f"{p['id_plan']} | {p['id_activo_tecnico']}": p for p in planes}
        if opciones:
            seleccion = st.selectbox("Seleccionar plan", list(opciones.keys()))
            datos = opciones.get(seleccion)
            if datos:
                nuevos_datos = form_plan(defaults=datos)
                if nuevos_datos:
                    coleccion.update_one({"_id": datos["_id"]}, {"$set": nuevos_datos})
                    registrar_evento_historial(
                        "Edición de plan preventivo",
                        nuevos_datos["id_activo_tecnico"],
                        nuevos_datos["id_plan"],
                        f"Edición de plan para activo: {nuevos_datos['id_activo_tecnico']}",
                        nuevos_datos["usuario_registro"],
                    )
                    st.success("✅ Plan actualizado correctamente.")
        else:
            st.info("No hay planes para editar.")

    elif choice == "Eliminar Plan":
        st.subheader("🗑️ Eliminar Plan Preventivo")
        planes = list(coleccion.find())
        opciones = {f"{p['id_plan']} | {p['id_activo_tecnico']}": p for p in planes}
        if opciones:
            seleccion = st.selectbox("Seleccionar plan", list(opciones.keys()))
            datos = opciones.get(seleccion)
            if datos and st.button("Eliminar definitivamente"):
                coleccion.delete_one({"_id": datos["_id"]})
                registrar_evento_historial(
                    "Baja de plan preventivo",
                    datos["id_activo_tecnico"],
                    datos["id_plan"],
                    f"Eliminación del plan asociado al activo: {datos['id_activo_tecnico']}",
                    datos["usuario_registro"],
                )
                st.success("🗑️ Plan eliminado correctamente.")
        else:
            st.info("No hay planes para eliminar.")


if __name__ == "__main__":
    app()
