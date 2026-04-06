import mongomock
from unittest.mock import patch
from cmms_fabrica.crud import crud_tareas_correctivas


def test_crear_tarea_correctiva_registra_historial():
    db_mock = mongomock.MongoClient().db
    with patch("cmms_fabrica.modulos.conexion_mongo.db", db_mock), \
         patch("cmms_fabrica.crud.generador_historial.db", db_mock), \
         patch("cmms_fabrica.crud.generador_historial.mongo_error", None, create=True):
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
            "criticidad": "Alta",
            "fecha_registro": 0,
            "incompleto": False,
        }

        # Flujo vigente en crud_tareas_correctivas.py:
        # CMMSRepository.insert_with_log(...)
        repository = crud_tareas_correctivas.CMMSRepository(
            "tareas_correctivas",
            database=db_mock,
        )
        repository.insert_with_log(
            data,
            event=crud_tareas_correctivas.HistorialEvent(
                tipo_evento="Alta de tarea correctiva",
                descripcion=f"Tarea registrada por falla: {data['descripcion_falla'][:120]}",
                usuario=data["usuario_registro"],
                id_origen=data["id_tarea"],
                proveedor_externo=data.get("proveedor_externo") or None,
                observaciones=data.get("observaciones") or None,
                criticidad=data.get("criticidad") or None,
            ),
        )

        assert db_mock.tareas_correctivas.count_documents({"id_tarea": "TC1"}) == 1
        evento = db_mock.historial.find_one({"id_origen": "TC1"})
        assert evento is not None
        assert evento["tipo_evento"] == "Alta de tarea correctiva"
        assert evento["id_activo_tecnico"] == "A1"
        assert evento["usuario_registro"] == "tech"
        assert evento["id_origen"] == "TC1"
        assert evento["criticidad"] == "Alta"
        tarea = db_mock.tareas_correctivas.find_one({"id_tarea": "TC1"})
        assert tarea["criticidad"] == "Alta"


def test_normalizar_criticidad_tarea_guarda_none_para_sin_clasificar():
    assert crud_tareas_correctivas._normalizar_criticidad("Sin clasificar") is None
    assert crud_tareas_correctivas._normalizar_criticidad("") is None
    assert crud_tareas_correctivas._normalizar_criticidad("Media") == "Media"
