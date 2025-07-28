"""Registro de eventos para el historial del CMMS.

Este módulo centraliza la inserción de eventos en la colección ``historial``
garantizando trazabilidad según las directrices de ISO 9001 e ISO 55001.
"""

from __future__ import annotations

from datetime import datetime
import logging
from modulos.conexion_mongo import db
import streamlit as st

logger = logging.getLogger(__name__)

def registrar_evento_historial(
    tipo_evento: str,
    id_activo: str | None,
    descripcion: str,
    usuario: str,
    id_origen: str | None = None,
    proveedor_externo: str | None = None,
    observaciones: str | None = None,
) -> str:
    """Inserta un evento consolidado en la colección ``historial``.

    Devuelve el identificador generado para facilitar la trazabilidad
    de acuerdo con ISO 9001.
    """

    if db is None:
        logger.warning("MongoDB no disponible. Evento no registrado.")
        try:
            st.warning("MongoDB no disponible. Evento no registrado.")
        except Exception:
            pass
        return ""

    historial = db["historial"]

    evento = {
        "id_evento": f"HIST_{int(datetime.now().timestamp())}",
        "id_activo_tecnico": id_activo,
        "fecha_evento": datetime.now(),
        "tipo_evento": tipo_evento,
        "id_origen": id_origen or "HUÉRFANO",
        "descripcion": descripcion,
        "usuario_registro": usuario,
        "proveedor_externo": proveedor_externo,
        "observaciones": observaciones or ""
    }

    historial.insert_one(evento)
    logger.info("Evento registrado en historial: %s", evento["id_evento"])
    return evento["id_evento"]

# Ejemplo de uso desde otro script:
if __name__ == "__main__":
    registrar_evento_historial(
        tipo_evento="correctiva",
        id_activo="BOBST_SP126E",
        descripcion="Falla en sistema de succión",
        usuario="pablo",
        id_origen="TAREA_5678",
        proveedor_externo="TecnoComp",
        observaciones="Requiere seguimiento"
    )
