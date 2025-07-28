"""Detección de Tareas Correctivas Huérfanas

Este script revisa la base de datos buscando tareas correctivas sin trazabilidad
completa en la colección ``historial`` y eventos correctivos mal registrados.
Se alinea con las buenas prácticas de mantenimiento industrial y la normativa
ISO 9001 para control de registros.
"""

from __future__ import annotations

from typing import List, Dict

from modulos.conexion_mongo import db


def obtener_correctivas_sin_historial() -> List[str]:
    """Devuelve los ``id_tarea`` sin evento ``historial`` tipo ``correctiva``."""
    if db is None:
        return []

    tareas = db["tareas_correctivas"].find({}, {"_id": 0, "id_tarea": 1})
    ids_faltantes: List[str] = []
    for tarea in tareas:
        id_tarea = tarea.get("id_tarea")
        if not id_tarea:
            continue
        query = {"id_origen": id_tarea, "tipo_evento": "correctiva"}
        if db["historial"].count_documents(query) == 0:
            ids_faltantes.append(id_tarea)
    return ids_faltantes


def obtener_eventos_correctivos_huerfanos() -> List[Dict[str, str]]:
    """Lista eventos ``historial`` tipo ``correctiva`` sin ``id_origen`` o ``id_activo_tecnico``."""
    if db is None:
        return []

    query = {
        "tipo_evento": "correctiva",
        "$or": [
            {"id_origen": {"$exists": False}},
            {"id_activo_tecnico": {"$exists": False}},
            {"id_origen": ""},
            {"id_activo_tecnico": ""},
        ],
    }
    campos = {"_id": 0, "id_evento": 1, "id_origen": 1, "id_activo_tecnico": 1}
    return list(db["historial"].find(query, campos))


def main() -> None:
    if db is None:
        print("❌ MongoDB no disponible. Revisá la conexión en conexion_mongo.py")
        return

    correctivas_sin_hist = obtener_correctivas_sin_historial()
    eventos_huerfanos = obtener_eventos_correctivos_huerfanos()

    print("correctivas_sin_historial:", correctivas_sin_hist)
    print("eventos_correctivos_huerfanos:", eventos_huerfanos)


if __name__ == "__main__":
    main()
