"""Utilidades de acceso a datos con trazabilidad para el CMMS Fábrica.

Este módulo expone ``CMMSRepository``, una envoltura mínima para las
colecciones de MongoDB que:

* valida la presencia de ``id_activo_tecnico`` en cada operación de escritura,
  cumpliendo la regla corporativa de trazabilidad ISO;
* centraliza el registro en la colección ``historial`` mediante
  :func:`crud.generador_historial.registrar_evento_historial`;
* ofrece helpers consistentes para insertar, actualizar y eliminar
  documentos de manera segura.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, MutableMapping, Optional

from pymongo.collection import Collection
from pymongo.database import Database

from crud.generador_historial import registrar_evento_historial
from modulos.conexion_mongo import get_db


def _coerce_mapping(data: Mapping[str, Any]) -> MutableMapping[str, Any]:
    """Crea una copia mutable asegurando que ``data`` no se modifique in-situ."""
    return dict(data)


@dataclass
class HistorialEvent:
    """Representa los metadatos necesarios para registrar un evento."""

    tipo_evento: str
    descripcion: str
    usuario: str
    id_origen: Optional[str] = None
    proveedor_externo: Optional[str] = None
    observaciones: Optional[str] = None


class CMMSRepository:
    """Repositorio genérico con logging automático en ``historial``."""

    def __init__(self, collection_name: str, database: Optional[Database] = None):
        # 🔴 IMPORTANTE: no usar "database or get_db()" porque Database no admite bool()
        if database is not None:
            self._db = database
        else:
            self._db = get_db()

        if self._db is None:
            # Si falló la conexión, cortamos ahí
            raise ConnectionError("MongoDB no disponible")

        self._collection: Collection = self._db[collection_name]

    @property
    def collection(self) -> Collection:
        return self._collection

    def insert_with_log(
        self,
        document: Mapping[str, Any],
        *,
        event: HistorialEvent,
    ) -> str:
        payload = _coerce_mapping(document)
        id_activo = payload.get("id_activo_tecnico")
        if not id_activo:
            raise ValueError("id_activo_tecnico es obligatorio para mantener trazabilidad")

        result = self._collection.insert_one(payload)

        id_origen = (
            event.id_origen
            or payload.get("id_tarea")
            or payload.get("id_plan")
            or payload.get("id_documento")
            or str(result.inserted_id)
        )

        registrar_evento_historial(
            event.tipo_evento,
            id_activo,
            event.descripcion,
            event.usuario,
            id_origen=id_origen,
            proveedor_externo=event.proveedor_externo or payload.get("proveedor_externo"),
            observaciones=event.observaciones or payload.get("observaciones"),
        )
        return str(result.inserted_id)

    def update_with_log(
        self,
        filtro: Mapping[str, Any],
        update_fields: Mapping[str, Any],
        *,
        event: HistorialEvent,
    ) -> int:
        payload = _coerce_mapping(update_fields)
        id_activo = payload.get("id_activo_tecnico")
        if not id_activo:
            raise ValueError("id_activo_tecnico es obligatorio para mantener trazabilidad")

        result = self._collection.update_one(filtro, {"$set": payload})
        if result.matched_count == 0:
            raise LookupError("Documento no encontrado para actualizar")

        id_origen = (
            event.id_origen
            or payload.get("id_tarea")
            or payload.get("id_plan")
            or payload.get("id_documento")
        )

        registrar_evento_historial(
            event.tipo_evento,
            id_activo,
            event.descripcion,
            event.usuario,
            id_origen=id_origen,
            proveedor_externo=event.proveedor_externo or payload.get("proveedor_externo"),
            observaciones=event.observaciones or payload.get("observaciones"),
        )
        return result.modified_count

    def delete_with_log(
        self,
        filtro: Mapping[str, Any],
        *,
        event: HistorialEvent,
        document: Optional[Mapping[str, Any]] = None,
    ) -> int:
        # Si nos pasaron el documento desde afuera lo usamos, si no lo buscamos
        registro = dict(document) if document is not None else self._collection.find_one(filtro)
        if registro is None:
            return 0

        id_activo = registro.get("id_activo_tecnico")
        if not id_activo:
            raise ValueError("id_activo_tecnico es obligatorio para mantener trazabilidad")

        result = self._collection.delete_one({"_id": registro["_id"]})

        if result.deleted_count:
            id_origen = (
                event.id_origen
                or registro.get("id_tarea")
                or registro.get("id_plan")
                or registro.get("id_documento")
            )
            registrar_evento_historial(
                event.tipo_evento,
                id_activo,
                event.descripcion,
                event.usuario,
                id_origen=id_origen,
                proveedor_externo=event.proveedor_externo or registro.get("proveedor_externo"),
                observaciones=event.observaciones or registro.get("observaciones"),
            )

        return result.deleted_count
