"""📦 Herramientas de Mantenimiento de Almacenamiento – CMMS Fábrica

Controla el tamaño total de MongoDB y permite limpieza de colecciones rotables,
respetando antigüedad, umbrales y el rol central de `historial`.

Normas:
- ISO 9001:2015 (Control de registros)
- ISO 55001 (Gestión del ciclo de vida del activo)
"""

from __future__ import annotations
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional

from cmms_fabrica.crud.generador_historial import registrar_evento_historial
from cmms_fabrica.modulos.conexion_mongo import db

# 📏 Límite total estimado permitido antes de ejecutar limpieza (ajustable)
LIMITE_MB: int = 400

# 🗂️ Colecciones rotables y su campo de fecha
# ⚠️ Actualizado al modelo 2025 centrado en activo técnico
COLECCIONES_ROTABLES: Dict[str, str] = {
    # crítica: la limpiamos solo por antigüedad
    "historial": "fecha_evento",
    # rotables “livianas”
    "observaciones": "fecha_evento",
    "tareas_correctivas": "fecha_evento",
    "tareas_tecnicas": "fecha_evento",
    "servicios_externos": "fecha_realizacion",
}

# 👮 Colecciones críticas: no se les aplica limpieza por porcentaje
COLECCIONES_CRITICAS = {"historial"}

# ⏱️ Antigüedad máxima para colecciones críticas (p. ej. 365 días)
MAX_DIAS_HISTORIAL = 365


def obtener_tamano_total_mb() -> float:
    """Devuelve el tamaño total estimado de la base de datos en MB."""
    stats = db.command("dbstats")
    total_bytes = stats.get("storageSize", 0)
    return total_bytes / (1024 * 1024)


def listar_colecciones_ordenadas() -> List[Tuple[str, int, str, bool]]:
    """
    Devuelve lista de colecciones rotables ordenadas por cantidad de documentos.

    Retorna tuplas: (nombre, cantidad, campo_fecha, es_critica)
    """
    datos: List[Tuple[str, int, str, bool]] = []
    for nombre, campo in COLECCIONES_ROTABLES.items():
        cantidad = db[nombre].estimated_document_count()
        es_critica = nombre in COLECCIONES_CRITICAS
        datos.append((nombre, cantidad, campo, es_critica))
    # más cargadas primero
    return sorted(datos, key=lambda x: x[1], reverse=True)


def _limpiar_por_antiguedad(
    nombre: str,
    campo_fecha: str,
    dias: int,
    minimo: int = 200,
) -> int:
    """
    Limpia documentos más viejos que N días.
    Útil para `historial`.
    """
    coleccion = db[nombre]
    total = coleccion.count_documents({})
    if total < minimo:
        return 0

    fecha_limite = datetime.utcnow() - timedelta(days=dias)

    # Solo borro los que tienen fecha y son viejos
    to_delete = {"$and": [{campo_fecha: {"$lt": fecha_limite}}]}
    res = coleccion.delete_many(to_delete)
    eliminados = res.deleted_count or 0

    if eliminados:
        registrar_evento_historial(
            tipo_evento="limpieza",
            id_activo=None,
            id_origen=nombre,
            descripcion=(
                f"Se eliminaron {eliminados} documentos de `{nombre}` "
                f"anteriores a {dias} días."
            ),
            usuario="sistema",
        )
    return eliminados


def _limpiar_por_porcentaje(
    nombre: str,
    campo_fecha: str,
    porcentaje: float = 0.3,
    minimo: int = 100,
) -> int:
    """
    Limpia una porción de la colección, empezando por los más viejos.
    """
    coleccion = db[nombre]
    total = coleccion.count_documents({})
    if total < minimo:
        return 0

    cantidad_a_eliminar = int(total * porcentaje)
    if cantidad_a_eliminar <= 0:
        return 0

    # Traigo los más viejos primero
    documentos = (
        coleccion.find({}, {"_id": 1, campo_fecha: 1})
        .sort(campo_fecha, 1)
        .limit(cantidad_a_eliminar)
    )
    ids_a_borrar = [doc["_id"] for doc in documentos if campo_fecha in doc]

    if not ids_a_borrar:
        return 0

    coleccion.delete_many({"_id": {"$in": ids_a_borrar}})

    registrar_evento_historial(
        tipo_evento="limpieza",
        id_activo=None,
        id_origen=nombre,
        descripcion=(
            f"Se eliminaron {len(ids_a_borrar)} documentos antiguos de `{nombre}`."
        ),
        usuario="sistema",
    )
    return len(ids_a_borrar)


def limpiar_coleccion(
    nombre: str,
    campo_fecha: str,
    porcentaje: float = 0.3,
    minimo: int = 100,
) -> int:
    """
    Decide la estrategia de limpieza según si la colección es crítica o no.
    """
    if nombre in COLECCIONES_CRITICAS:
        # limpieza segura por antigüedad
        return _limpiar_por_antiguedad(
            nombre,
            campo_fecha,
            dias=MAX_DIAS_HISTORIAL,
            minimo=minimo,
        )
    # resto de las colecciones, por porcentaje
    return _limpiar_por_porcentaje(
        nombre,
        campo_fecha,
        porcentaje=porcentaje,
        minimo=minimo,
    )


def ejecutar_limpieza_si_es_necesario() -> bool:
    """
    Ejecuta limpieza automática si se supera el límite de almacenamiento total.
    Recorre las colecciones en orden de carga.
    """
    uso_actual = obtener_tamano_total_mb()
    if uso_actual < LIMITE_MB:
        return False

    total_eliminados = 0
    for nombre, _, campo_fecha, _ in listar_colecciones_ordenadas():
        eliminados = limpiar_coleccion(nombre, campo_fecha)
        total_eliminados += eliminados
        # reevalúo después de cada limpieza
        if obtener_tamano_total_mb() < LIMITE_MB:
            break

    return total_eliminados > 0


def limpiar_coleccion_mas_cargada() -> Optional[Tuple[str, int]]:
    """
    Limpia automáticamente la colección rotable con más documentos.
    Devuelve (nombre, cantidad_eliminada) o None.
    """
    lista = listar_colecciones_ordenadas()
    if not lista:
        return None

    nombre, _, campo_fecha, _ = lista[0]
    eliminados = limpiar_coleccion(nombre, campo_fecha)
    return (nombre, eliminados) if eliminados > 0 else None
