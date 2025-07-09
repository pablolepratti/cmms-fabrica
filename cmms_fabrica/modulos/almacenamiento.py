"""📦 Herramientas de Mantenimiento de Almacenamiento – CMMS Fábrica

Este módulo controla el tamaño total de la base de datos MongoDB y permite ejecutar limpieza
automática de colecciones rotables como `historial`, `observaciones`, `tareas` y `servicios`,
respetando antigüedad y umbrales definidos.

✅ Normas aplicables:
- ISO 9001:2015 (Control de registros)
- ISO 55001 (Gestión del ciclo de vida del activo)
"""

from __future__ import annotations
from datetime import datetime
from typing import Dict

from crud.generador_historial import registrar_evento_historial
from modulos.conexion_mongo import db

# 📏 Límite total estimado permitido antes de ejecutar limpieza
LIMITE_MB: int = 400

# 🗂️ Colecciones que se pueden limpiar y su campo de fecha para ordenarlas
colecciones_rotables: Dict[str, str] = {
    "historial": "fecha_evento",
    "observaciones": "fecha_evento",
    "tareas": "ultima_ejecucion",
    "servicios": "fecha_realizacion"
}

def obtener_tamano_total_mb() -> float:
    """Devuelve el tamaño total estimado de la base de datos en megabytes."""
    stats = db.command("dbstats")
    total_bytes = stats.get("storageSize", 0)
    return total_bytes / (1024 * 1024)

def listar_colecciones_ordenadas() -> list[tuple[str, int, str]]:
    """Devuelve lista de colecciones rotables ordenadas por cantidad de documentos."""
    datos = []
    for nombre, campo in colecciones_rotables.items():
        cantidad = db[nombre].estimated_document_count()
        datos.append((nombre, cantidad, campo))
    return sorted(datos, key=lambda x: x[1], reverse=True)

def limpiar_coleccion(
    nombre: str,
    campo_fecha: str,
    porcentaje: float = 0.3,
    minimo: int = 100
) -> int:
    """Borra documentos antiguos de una colección respetando trazabilidad.

    Parameters
    ----------
    nombre : str
        Nombre de la colección objetivo.
    campo_fecha : str
        Campo de fecha por el cual ordenar los documentos.
    porcentaje : float
        Proporción aproximada a eliminar (por defecto 30%).
    minimo : int
        Mínimo de documentos para ejecutar la limpieza.

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
            tipo_evento="limpieza",
            id_activo=None,
            id_origen=nombre,
            descripcion=f"Se eliminaron {len(ids_a_borrar)} documentos antiguos de `{nombre}`.",
            usuario="sistema"
        )
        return len(ids_a_borrar)

    return 0

def ejecutar_limpieza_si_es_necesario() -> bool:
    """Ejecuta limpieza automática si se supera el límite de almacenamiento total."""
    uso_actual = obtener_tamano_total_mb()
    if uso_actual < LIMITE_MB:
        return False

    total_eliminados = 0
    for nombre, campo_fecha in listar_colecciones_ordenadas():
        eliminados = limpiar_coleccion(nombre, campo_fecha)
        total_eliminados += eliminados
        if obtener_tamano_total_mb() < LIMITE_MB:
            break

    return total_eliminados > 0

def limpiar_coleccion_mas_cargada() -> tuple[str, int] | None:
    """Limpia automáticamente la colección rotable con más documentos.

    Returns
    -------
    tuple(nombre_coleccion, cantidad_eliminada) or None
    """
    lista = listar_colecciones_ordenadas()
    if not lista:
        return None

    nombre, _, campo_fecha = lista[0]
    eliminados = limpiar_coleccion(nombre, campo_fecha)
    return (nombre, eliminados) if eliminados > 0 else None
