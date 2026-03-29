import pandas as pd
from cmms_fabrica.modulos.app_reportes import (
    categorizar_tipo_evento,
    generar_pdf,
    generar_excel,
    filtrar_ultimo_por_activo,
)


def test_generar_reportes_con_observaciones(tmp_path):
    df_eventos = pd.DataFrame({
        "fecha_evento": [pd.Timestamp("2024-01-01")],
        "tipo_evento": ["test"],
        "id_activo_tecnico": ["A1"],
        "id_origen": ["EV-1"],
        "descripcion": ["ok"],
        "observaciones": ["-"],
        "usuario_registro": ["user"],
    })

    df_inventario = pd.DataFrame({
        "fecha_evento": [pd.Timestamp("2024-01-02")],
        "id_item": ["IT-1"],
        "descripcion": ["Filtro de aire"],
    })

    columnas_eventos = [
        "fecha_evento",
        "tipo_evento",
        "id_activo_tecnico",
        "id_origen",
        "descripcion",
        "observaciones",
        "usuario_registro",
    ]
    pdf_path = generar_pdf(df_eventos[columnas_eventos], df_inventario, "tmp")
    assert pdf_path.endswith(".pdf")
    excel_buffer = generar_excel(df_eventos[columnas_eventos], df_inventario)
    assert excel_buffer.getbuffer().nbytes > 0


def test_filtrar_ultimo_por_evento():
    df = pd.DataFrame(
        {
            "fecha_evento": [pd.Timestamp("2024-01-01"), pd.Timestamp("2024-01-05")],
            "tipo_evento": ["test", "test"],
            "id_activo_tecnico": ["A1", "A1"],
            "id_origen": ["EV1", "EV1"],
            "descripcion": ["primero", "segundo"],
            "usuario_registro": ["u", "u"],
        }
    )
    filtrado = filtrar_ultimo_por_activo(df)
    assert len(filtrado) == 1
    assert filtrado.iloc[0]["descripcion"] == "segundo"


def test_filtrar_por_tarea_y_activo():
    df = pd.DataFrame(
        {
            "fecha_evento": [
                pd.Timestamp("2024-01-01"),
                pd.Timestamp("2024-01-03"),
                pd.Timestamp("2024-01-05"),
            ],
            "tipo_evento": ["test", "test", "test"],
            "id_activo_tecnico": ["A1", "A2", "A1"],
            "id_origen": ["EV1", "EV1", "EV1"],
            "descripcion": ["a1-1", "a2-1", "a1-2"],
            "usuario_registro": ["u", "u", "u"],
        }
    )
    filtrado = filtrar_ultimo_por_activo(df)
    assert len(filtrado) == 2
    assert set(filtrado["id_activo_tecnico"]) == {"A1", "A2"}
    assert filtrado.loc[filtrado["id_activo_tecnico"] == "A1", "descripcion"].iloc[0] == "a1-2"


def test_categorizar_tipo_evento_variantes_texto_largo():
    assert categorizar_tipo_evento("Registro de observación técnica") == "observacion"
    assert categorizar_tipo_evento("Tarea correctiva registrada") == "correctiva"


def test_filtrado_por_categoria_evento_en_dataframe():
    df = pd.DataFrame(
        {
            "tipo_evento": [
                "Registro de observación técnica",
                "Tarea correctiva registrada",
                "Mantenimiento preventivo ejecutado",
            ]
        }
    )
    categorias_ui = ["observacion", "correctiva"]
    df["categoria_evento"] = df["tipo_evento"].apply(categorizar_tipo_evento)
    filtrado = df[df["categoria_evento"].isin(categorias_ui)]

    assert len(filtrado) == 2
    assert set(filtrado["categoria_evento"]) == {"observacion", "correctiva"}
