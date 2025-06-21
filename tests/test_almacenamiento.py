import builtins
import types
from unittest.mock import MagicMock, patch
import cmms_fabrica.modulos.almacenamiento as almacenamiento


def test_limpiar_coleccion_elimina_y_registra():
    db_mock = MagicMock()
    coleccion_mock = MagicMock()
    db_mock.__getitem__.return_value = coleccion_mock
    coleccion_mock.count_documents.return_value = 200
    docs = [{"_id": i, "fecha": i} for i in range(60)]
    coleccion_mock.find.return_value.sort.return_value.limit.return_value = docs
    with patch.object(almacenamiento, "db", db_mock), \
         patch("cmms_fabrica.modulos.almacenamiento.registrar_evento_historial") as log:
        eliminados = almacenamiento.limpiar_coleccion("historial", "fecha")
        assert eliminados == 60
        coleccion_mock.delete_many.assert_called_once()
        log.assert_called_once()


def test_limpiar_coleccion_no_elimina_si_pocos():
    db_mock = MagicMock()
    coleccion_mock = MagicMock()
    db_mock.__getitem__.return_value = coleccion_mock
    coleccion_mock.count_documents.return_value = 50
    with patch.object(almacenamiento, "db", db_mock), \
         patch("cmms_fabrica.modulos.almacenamiento.registrar_evento_historial") as log:
        eliminados = almacenamiento.limpiar_coleccion("historial", "fecha")
        assert eliminados == 0
        coleccion_mock.delete_many.assert_not_called()
        log.assert_not_called()
