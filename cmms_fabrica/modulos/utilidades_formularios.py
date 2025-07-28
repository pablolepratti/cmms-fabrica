"""Funciones auxiliares para cargar opciones en formularios Streamlit."""

from __future__ import annotations
from typing import List
from modulos.conexion_mongo import db


def select_activo_tecnico(database=db) -> List[str]:
    """Devuelve lista ordenada de IDs de activos técnicos."""
    if database is None:
        return []
    activos = database["activos_tecnicos"].find({}, {"_id": 0, "id_activo_tecnico": 1})
    return sorted(a.get("id_activo_tecnico") for a in activos if a.get("id_activo_tecnico"))


def select_usuarios(database=db) -> List[str]:
    """Devuelve lista ordenada de nombres de usuario."""
    if database is None:
        return []
    usuarios = database["usuarios"].find({}, {"_id": 0, "nombre": 1})
    return sorted(u.get("nombre") for u in usuarios if u.get("nombre"))


def select_proveedores_externos(database=db) -> List[str]:
    """Devuelve lista ordenada de proveedores externos."""
    if database is None:
        return []
    proveedores = database["servicios_externos"].find({}, {"_id": 0, "nombre": 1})
    return sorted(p.get("nombre") for p in proveedores if p.get("nombre"))
