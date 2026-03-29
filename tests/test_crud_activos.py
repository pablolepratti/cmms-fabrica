import mongomock
from unittest.mock import patch
from cmms_fabrica.crud import crud_activos_tecnicos


def test_crear_activo_registra_historial():
    db_mock = mongomock.MongoClient().db
    with patch("cmms_fabrica.modulos.conexion_mongo.db", db_mock), \
         patch("cmms_fabrica.crud.generador_historial.db", db_mock), \
         patch("cmms_fabrica.crud.generador_historial.mongo_error", None, create=True):
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
        evento = db_mock.historial.find_one({"id_origen": "A1"})
        assert evento is not None
        assert evento["id_activo_tecnico"] == "A1"
        assert evento["descripcion"] == "Se dio de alta el activo 'Compresor'"
        assert evento["usuario_registro"] == "user"
        assert evento["id_origen"] == "A1"
