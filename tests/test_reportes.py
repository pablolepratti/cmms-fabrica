import pandas as pd
from cmms_fabrica.modulos.app_reportes import generar_pdf, generar_excel


def test_generar_reportes_con_observaciones(tmp_path):
    df = pd.DataFrame({
        "fecha_evento": [pd.Timestamp("2024-01-01")],
        "tipo_evento": ["test"],
        "id_activo_tecnico": ["A1"],
        "descripcion": ["ok"],
        "usuario_registro": ["user"],
    })
    if "observaciones" not in df.columns:
        df["observaciones"] = "-"
    columnas = ["fecha_evento", "tipo_evento", "id_activo_tecnico", "descripcion", "observaciones", "usuario_registro"]
    pdf_path = generar_pdf(df[columnas], "tmp")
    assert pdf_path.endswith(".pdf")
    excel_buffer = generar_excel(df[columnas], "tmp")
    assert excel_buffer.getbuffer().nbytes > 0
