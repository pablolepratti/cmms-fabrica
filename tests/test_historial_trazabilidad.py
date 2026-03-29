import mongomock
from unittest.mock import patch

from cmms_fabrica.crud.generador_historial import registrar_evento_historial


def test_registrar_evento_historial_persiste_campos_trazables():
    db_mock = mongomock.MongoClient().db
    with patch("cmms_fabrica.crud.generador_historial.db", db_mock):
        registrar_evento_historial(
            tipo_evento="Alta de plan preventivo",
            id_activo="AT-001",
            descripcion="Alta de plan para activo: AT-001",
            usuario="tecnico_a",
            id_origen="PP-001",
            proveedor_externo="Proveedor X",
            observaciones="Programar seguimiento mensual",
        )

    evento = db_mock.historial.find_one({"id_origen": "PP-001"})
    assert evento is not None
    assert evento["tipo_evento"] == "Alta de plan preventivo"
    assert evento["id_activo_tecnico"] == "AT-001"
    assert evento["descripcion"] == "Alta de plan para activo: AT-001"
    assert evento["usuario_registro"] == "tecnico_a"
    assert evento["id_origen"] == "PP-001"
    assert evento["proveedor_externo"] == "Proveedor X"
    assert evento["observaciones"] == "Programar seguimiento mensual"
