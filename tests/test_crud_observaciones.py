from unittest.mock import patch

from cmms_fabrica.crud import crud_observaciones


class FakeCollection:
    def __init__(self):
        self.docs = []

    def insert_one(self, doc):
        self.docs.append(dict(doc))
        return {"inserted_id": len(self.docs)}

    def count_documents(self, query):
        return sum(1 for d in self.docs if all(d.get(k) == v for k, v in query.items()))

    def find_one(self, query):
        for d in self.docs:
            if all(d.get(k) == v for k, v in query.items()):
                return d
        return None


class FakeDB:
    def __init__(self):
        self._collections = {
            "observaciones": FakeCollection(),
            "historial": FakeCollection(),
            "activos_tecnicos": FakeCollection(),
        }

    def __getitem__(self, item):
        return self._collections[item]

    @property
    def observaciones(self):
        return self._collections["observaciones"]

    @property
    def historial(self):
        return self._collections["historial"]


def test_registrar_observacion_inserta_observacion_y_historial():
    db_mock = FakeDB()
    data = {
        "id_observacion": "OBS-100",
        "id_activo_tecnico": "AT-100",
        "fecha_evento": "2026-03-29",
        "descripcion": "Temperatura elevada en rodamiento lado acople",
        "tipo_observacion": "Advertencia",
        "reportado_por": "inspector_1",
        "estado": "Pendiente",
        "usuario_registro": "tecnico_cmms",
        "observaciones": "Verificar vibración en próxima ronda",
        "criticidad": "Media",
        "fecha_registro": 0,
    }

    with patch("cmms_fabrica.crud.crud_observaciones.db", db_mock), \
         patch("cmms_fabrica.crud.generador_historial.db", db_mock), \
         patch("cmms_fabrica.crud.generador_historial.mongo_error", None, create=True), \
         patch("cmms_fabrica.crud.crud_observaciones.form_observacion", return_value=data), \
         patch("cmms_fabrica.crud.crud_observaciones.st.title"), \
         patch("cmms_fabrica.crud.crud_observaciones.st.subheader"), \
         patch("cmms_fabrica.crud.crud_observaciones.st.success"), \
         patch("cmms_fabrica.crud.crud_observaciones.st.sidebar.radio", return_value="Registrar Observación"):
        crud_observaciones.app()

    assert db_mock.observaciones.count_documents({"id_observacion": "OBS-100"}) == 1

    evento = db_mock.historial.find_one({"id_origen": "OBS-100"})
    assert evento is not None
    assert evento["id_origen"] == "OBS-100"
    assert evento["usuario_registro"] == "tecnico_cmms"
    assert evento["criticidad"] == "Media"
    observacion = db_mock.observaciones.find_one({"id_observacion": "OBS-100"})
    assert observacion["criticidad"] == "Media"


def test_normalizar_criticidad_observacion_guarda_none_para_sin_clasificar():
    assert crud_observaciones._normalizar_criticidad("Sin clasificar") is None
    assert crud_observaciones._normalizar_criticidad(None) is None
    assert crud_observaciones._normalizar_criticidad("Alta") == "Alta"
