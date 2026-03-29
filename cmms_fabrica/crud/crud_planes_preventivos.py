"""
🗓️ CRUD de Planes Preventivos – CMMS Fábrica
Versión extendida (tiempo + uso + ambos)
- tiempo  -> como el original: vence por fecha
- uso     -> vence por horas/km/ciclos según lectura
- ambos   -> vence por el primero que se cumpla

✅ Alineado con:
- ISO 55001 (activo como eje)
- ISO 9001:2015 (control operacional)
- ISO 14224 (datos de mantenimiento)
"""

from datetime import datetime, date

import pandas as pd
import streamlit as st

from cmms_fabrica.crud.generador_historial import registrar_evento_historial
from cmms_fabrica.modulos.conexion_mongo import db
from cmms_fabrica.modulos.utilidades_formularios import select_proveedores_externos


# ---------------------------------------------------------------------
# Helpers básicos
# ---------------------------------------------------------------------
def crear_plan_preventivo(data: dict, database=db):
    """Inserta un plan preventivo y registra el evento en historial."""
    if database is None:
        return None
    coleccion = database["planes_preventivos"]
    coleccion.insert_one(data)
    registrar_evento_historial(
        tipo_evento="Alta de plan preventivo",
        id_activo=data["id_activo_tecnico"],
        descripcion=f"Alta de plan para activo: {data['id_activo_tecnico']}",
        usuario=data["usuario_registro"],
        id_origen=data["id_plan"],
    )
    return data["id_plan"]


def generar_id_plan() -> str:
    """Genera un ID único simple para el plan."""
    return f"PP-{int(datetime.now().timestamp())}"


# ---------------------------------------------------------------------
# App principal
# ---------------------------------------------------------------------
def app():
    if db is None:
        st.error("MongoDB no disponible")
        return

    coleccion = db["planes_preventivos"]

    st.title("🗓️ Gestión de Planes Preventivos")
    menu = [
        "Registrar Plan",
        "Ver Planes",
        "Planes vencidos",
        "Editar Plan",
        "Eliminar Plan",
    ]
    choice = st.sidebar.radio("Acción", menu)

    # -----------------------------------------------------------------
    # Formulario reutilizable
    # -----------------------------------------------------------------
    def form_plan(defaults=None):
        # normalizamos para no hacer `if defaults` por todos lados
        if defaults is None:
            defaults = {}

        with st.form("form_plan_preventivo"):
            # ---------------------------------------------------------
            # ID del plan
            # ---------------------------------------------------------
            id_plan = st.text_input(
                "ID del Plan",
                value=defaults.get("id_plan", generar_id_plan()),
            )

            # ---------------------------------------------------------
            # Activo técnico asociado (obligatorio)
            # ---------------------------------------------------------
            activos_lista = list(
                db["activos_tecnicos"].find(
                    {}, {"_id": 0, "id_activo_tecnico": 1, "nombre": 1}
                )
            )
            if activos_lista:
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

                default_id = defaults.get("id_activo_tecnico")
                default_label = (
                    next((k for k, v in map_id.items() if v == default_id), None)
                    or opciones[0]
                )

                index_default = (
                    opciones.index(default_label) if default_label in opciones else 0
                )

                id_activo_sel = st.selectbox(
                    "Activo Técnico asociado", opciones, index=index_default
                )
                id_activo_tecnico = map_id.get(id_activo_sel, "")
            else:
                st.warning("⚠️ No hay activos técnicos cargados. Primero cargá uno.")
                st.form_submit_button("Guardar", disabled=True)
                return None  # no seguimos

            # ---------------------------------------------------------
            # Tipo de programación (novedad)
            # ---------------------------------------------------------
            tipo_programacion = st.selectbox(
                "Tipo de programación",
                ["tiempo", "uso", "ambos"],
                index=["tiempo", "uso", "ambos"].index(
                    defaults.get("tipo_programacion", "tiempo")
                ),
                help="‘tiempo’: por fecha. ‘uso’: por horas/km. ‘ambos’: vence por el primero.",
            )

            # ---------------------------------------------------------
            # BLOQUE POR TIEMPO
            # ---------------------------------------------------------
            frecuencia = st.number_input(
                "Frecuencia (para tiempo)",
                min_value=1,
                value=int(defaults.get("frecuencia", 1)),
            )
            unidad_frecuencia = st.selectbox(
                "Unidad",
                ["días", "semanas", "meses"],
                index=["días", "semanas", "meses"].index(
                    defaults.get("unidad_frecuencia", "días")
                ),
            )

            # fechas seguras
            proxima_raw = defaults.get("proxima_fecha")
            if proxima_raw:
                try:
                    proxima_default = datetime.strptime(proxima_raw, "%Y-%m-%d").date()
                except ValueError:
                    proxima_default = date.today()
            else:
                proxima_default = date.today()

            ultima_raw = defaults.get("ultima_fecha")
            if ultima_raw:
                try:
                    ultima_default = datetime.strptime(ultima_raw, "%Y-%m-%d").date()
                except ValueError:
                    ultima_default = date.today()
            else:
                ultima_default = date.today()

            proxima_fecha = st.date_input(
                "Próxima Ejecución (por tiempo)", value=proxima_default
            )
            ultima_fecha = st.date_input(
                "Última Ejecución (por tiempo)", value=ultima_default
            )

            # ---------------------------------------------------------
            # BLOQUE POR USO (horas/km/ciclos)
            # ---------------------------------------------------------
            col1, col2 = st.columns(2)
            with col1:
                umbral_uso = st.number_input(
                    "Umbral de uso (ej. 250 h / 500 km)",
                    min_value=0.0,
                    value=float(defaults.get("umbral_uso", 0.0)),
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
                    value=float(defaults.get("ultima_lectura_uso", 0.0)),
                    help="Lectura de horómetro/odómetro cuando se hizo el último mantenimiento.",
                )
            with col4:
                lectura_actual_uso = st.number_input(
                    "Lectura actual de uso",
                    min_value=0.0,
                    value=float(defaults.get("lectura_actual_uso", 0.0)),
                    help="Lectura real de hoy. Si no la tenés, dejá el valor anterior.",
                )

            # ---------------------------------------------------------
            # Datos generales
            # ---------------------------------------------------------
            responsable = st.text_input(
                "Responsable", value=defaults.get("responsable", "")
            )

            tipo_ejecucion = st.radio(
                "¿Quién ejecuta la tarea preventiva?",
                ["Interno", "Externo"],
                index=0 if defaults.get("proveedor_externo", "") in ["", None] else 1,
            )

            nombres_proveedores = select_proveedores_externos(db)
            proveedor_externo = ""
            if tipo_ejecucion == "Externo":
                if nombres_proveedores:
                    prov_def = defaults.get("proveedor_externo", "")
                    idx = (
                        nombres_proveedores.index(prov_def)
                        if prov_def in nombres_proveedores
                        else 0
                    )
                    proveedor_externo = st.selectbox(
                        "Proveedor Externo", nombres_proveedores, index=idx
                    )
                else:
                    st.info("No hay proveedores externos cargados.")
                    proveedor_externo = ""
            else:
                proveedor_externo = ""

            estado = st.selectbox(
                "Estado",
                ["Activo", "Suspendido", "Finalizado"],
                index=["Activo", "Suspendido", "Finalizado"].index(
                    defaults.get("estado", "Activo")
                ),
            )

            adjunto_plan = st.text_input(
                "Documento o Link del Plan", value=defaults.get("adjunto_plan", "")
            )
            usuario = st.text_input(
                "Usuario que registra", value=defaults.get("usuario_registro", "")
            )
            observaciones = st.text_area(
                "Observaciones", value=defaults.get("observaciones", "")
            )

            submit = st.form_submit_button("Guardar")

        # -------------------------------------------------------------
        # Validación final
        # -------------------------------------------------------------
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

    # -----------------------------------------------------------------
    # 1) Registrar Plan
    # -----------------------------------------------------------------
    if choice == "Registrar Plan":
        st.subheader("➕ Alta de Plan Preventivo")
        data = form_plan()
        if data:
            crear_plan_preventivo(data, db)
            st.success("✅ Plan preventivo registrado correctamente.")

    # -----------------------------------------------------------------
    # 2) Ver Planes
    # -----------------------------------------------------------------
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
            # agrupamos por activo
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
                        f"- **Tipo:** {tipo_prog} | **Próxima (tiempo):** {p.get('proxima_fecha', '-')} | "
                        f"**Uso umbral:** {p.get('umbral_uso', '-') } {p.get('unidad_uso', '')} | "
                        f"**Frecuencia:** {freq} | **Estado:** {p.get('estado', '-')}"
                    )

    # -----------------------------------------------------------------
    # 3) Planes vencidos (tiempo, uso o ambos)
    # -----------------------------------------------------------------
    elif choice == "Planes vencidos":
        st.subheader("⏰ Planes preventivos vencidos")
        hoy = date.today()
        planes = list(coleccion.find())
        vencidos = []

        for p in planes:
            # solo activos
            if p.get("estado") != "Activo":
                continue

            tipo_prog = p.get("tipo_programacion", "tiempo")
            vencio_por_tiempo = False
            vencio_por_uso = False

            # --- por tiempo
            if tipo_prog in ("tiempo", "ambos"):
                pf = p.get("proxima_fecha")
                if pf:
                    try:
                        fecha_plan = datetime.strptime(pf, "%Y-%m-%d").date()
                        if fecha_plan < hoy:
                            vencio_por_tiempo = True
                    except ValueError:
                        # fecha mal cargada: la ignoramos
                        pass

            # --- por uso
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
            st.success("👌 No hay planes vencidos (ni por tiempo ni por uso).")
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

    # -----------------------------------------------------------------
    # 4) Editar plan
    # -----------------------------------------------------------------
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
                        tipo_evento="Edición de plan preventivo",
                        id_activo=nuevos_datos["id_activo_tecnico"],
                        descripcion=f"Edición de plan para activo: {nuevos_datos['id_activo_tecnico']}",
                        usuario=nuevos_datos["usuario_registro"],
                        id_origen=nuevos_datos["id_plan"],
                    )
                    st.success("✅ Plan actualizado correctamente.")
        else:
            st.info("No hay planes para editar.")

    # -----------------------------------------------------------------
    # 5) Eliminar plan
    # -----------------------------------------------------------------
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
                    tipo_evento="Baja de plan preventivo",
                    id_activo=datos["id_activo_tecnico"],
                    descripcion=f"Eliminación del plan asociado al activo: {datos['id_activo_tecnico']}",
                    usuario=datos["usuario_registro"],
                    id_origen=datos["id_plan"],
                )
                st.success("🗑️ Plan eliminado correctamente.")
        else:
            st.info("No hay planes para eliminar.")


# ---------------------------------------------------------------------
# Ejecutable directo
# ---------------------------------------------------------------------
if __name__ == "__main__":
    app()
