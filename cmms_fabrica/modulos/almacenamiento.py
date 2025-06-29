"""Herramientas de mantenimiento del almacenamiento en MongoDB."""

from __future__ import annotations

from datetime import datetime
from typing import Dict, Literal

from crud.generador_historial import registrar_evento_historial
from modulos.conexion_mongo import db

LIMITE_MB: int = 400

# Colecciones a rotar, campo por el que se ordenan (más antiguos primero)
colecciones_rotables: Dict[str, str] = {
    "historial": "fecha",
    "observaciones": "fecha",
    "tareas": "ultima_ejecucion",
    "servicios": "fecha_realizacion"
}

def obtener_tamano_total_mb() -> float:
    """Devuelve el tamaño total estimado de la base de datos en megabytes."""
    stats = db.command("dbstats")
    total_bytes = stats.get("storageSize", 0)
    return total_bytes / (1024 * 1024)

def limpiar_coleccion(
    nombre: str,
    campo_fecha: str,
    porcentaje: float = 0.3,
    minimo: int = 100,
) -> int:
    """Borra documentos antiguos manteniendo la trazabilidad.

    Parameters
    ----------
    nombre: str
        Nombre de la colección objetivo.
    campo_fecha: str
        Campo por el cual ordenar los documentos más antiguos primero.
    porcentaje: float, default 0.3
        Porcentaje aproximado a eliminar si se supera ``minimo``.
    minimo: int, default 100
        Límite de registros a partir del cual se ejecuta la limpieza.

    Returns
    -------
    int
        Cantidad de documentos eliminados.
    """
    coleccion = db[nombre]
    total = coleccion.count_documents({})

    if total < minimo:
        return 0

    cantidad_a_eliminar = int(total * porcentaje)
    documentos = coleccion.find({}, {"_id": 1, campo_fecha: 1}).sort(campo_fecha, 1).limit(cantidad_a_eliminar)
    ids_a_borrar = [doc["_id"] for doc in documentos if campo_fecha in doc]

    if ids_a_borrar:
        coleccion.delete_many({"_id": {"$in": ids_a_borrar}})
        registrar_evento_historial(
            "limpieza",
            None,
            nombre,
            f"Se eliminaron {len(ids_a_borrar)} documentos.",
            "sistema",
        )
        return len(ids_a_borrar)

    return 0

def ejecutar_limpieza_si_es_necesario() -> bool:
    """Ejecuta la rotación de colecciones si se supera ``LIMITE_MB``."""

    uso_actual = obtener_tamano_total_mb()
    if uso_actual < LIMITE_MB:
        return False

    total_eliminados = 0
    for nombre, campo_fecha in sorted(colecciones_rotables.items(), key=lambda x: db[x[0]].estimated_document_count(), reverse=True):
        eliminados = limpiar_coleccion(nombre, campo_fecha)
        total_eliminados += eliminados
        if obtener_tamano_total_mb() < LIMITE_MB:
            break

    return total_eliminados > 0
