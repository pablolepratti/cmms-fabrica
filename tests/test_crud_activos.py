import mongomock
from unittest.mock import patch
from cmms_fabrica.crud import crud_activos_tecnicos


def test_crear_activo_registra_historial():
    db_mock = mongomock.MongoClient().db
    with patch("cmms_fabrica.modulos.conexion_mongo.db", db_mock), \
         patch("cmms_fabrica.crud.generador_historial.db", db_mock):
        data = {
            "id_activo_tecnico": "A1",
            "nombre": "Compresor",
            "ubicacion": "Planta",
            "tipo": "Equipo",
            "estado": "Activo",
            "responsable": "user",
            "usuario_registro": "user",
            "fecha_registro": 0,
        }
        crud_activos_tecnicos.crear_activo(data, db_mock)
        assert db_mock.activos_tecnicos.count_documents({"id_activo_tecnico": "A1"}) == 1
        assert db_mock.historial.count_documents({"id_origen": "A1"}) == 1
