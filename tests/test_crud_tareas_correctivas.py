import mongomock
from unittest.mock import patch
from cmms_fabrica.crud import crud_tareas_correctivas


def test_crear_tarea_correctiva_registra_historial():
    db_mock = mongomock.MongoClient().db
    with patch("cmms_fabrica.modulos.conexion_mongo.db", db_mock), \
         patch("cmms_fabrica.crud.generador_historial.db", db_mock):
        data = {
            "id_tarea": "TC1",
            "id_activo_tecnico": "A1",
            "fecha_evento": "2024-01-01",
            "descripcion_falla": "falla",
            "modo_falla": "corriente",
            "rca_requerido": False,
            "rca_completado": False,
            "causa_raiz": "",
            "metodo_rca": "",
            "acciones_rca": "",
            "usuario_rca": "",
            "responsable": "tech",
            "proveedor_externo": "",
            "estado": "Abierta",
            "usuario_registro": "tech",
            "observaciones": "",
            "fecha_registro": 0,
            "incompleto": False,
        }
        crud_tareas_correctivas.crear_tarea_correctiva(data, db_mock)
        assert db_mock.tareas_correctivas.count_documents({"id_tarea": "TC1"}) == 1
        assert db_mock.historial.count_documents({"id_origen": "TC1"}) == 1
