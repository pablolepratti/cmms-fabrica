import mongomock
from unittest.mock import patch
from cmms_fabrica.crud import crud_planes_preventivos


def test_crear_plan_preventivo_registra_historial():
    db_mock = mongomock.MongoClient().db
    with patch("cmms_fabrica.modulos.conexion_mongo.db", db_mock), \
         patch("cmms_fabrica.crud.generador_historial.db", db_mock):
        data = {
            "id_plan": "PP1",
            "id_activo_tecnico": "A1",
            "frecuencia": 1,
            "unidad_frecuencia": "días",
            "proxima_fecha": "2024-01-01",
            "ultima_fecha": "2023-12-01",
            "responsable": "tech",
            "proveedor_externo": "",
            "estado": "Activo",
            "adjunto_plan": "",
            "usuario_registro": "tech",
            "observaciones": "",
            "fecha_registro": 0,
        }
        crud_planes_preventivos.crear_plan_preventivo(data, db_mock)
        assert db_mock.planes_preventivos.count_documents({"id_plan": "PP1"}) == 1
        assert db_mock.historial.count_documents({"id_origen": "PP1"}) == 1
