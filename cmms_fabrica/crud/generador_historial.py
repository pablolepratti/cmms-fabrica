from pymongo import MongoClient
from datetime import datetime

def registrar_evento_historial(tipo_evento, id_activo, id_origen, descripcion, usuario, proveedor_externo=None, observaciones=None):
    """
    Inserta un evento consolidado en la colección historial.
    """
    client = MongoClient()  # reemplazar con URI de producción si es necesario
    db = client["cmms"]
    historial = db["historial"]

    evento = {
        "id_evento": f"HIST_{int(datetime.now().timestamp())}",
        "id_activo_tecnico": id_activo,
        "fecha_evento": datetime.now(),
        "tipo_evento": tipo_evento,
        "id_origen": id_origen,
        "descripcion": descripcion,
        "usuario_registro": usuario,
        "proveedor_externo": proveedor_externo,
        "observaciones": observaciones or ""
    }

    historial.insert_one(evento)
    print(f"[Historial] Evento registrado: {evento['id_evento']}")

# Ejemplo de uso desde otro script:
if __name__ == "__main__":
    registrar_evento_historial(
        tipo_evento="correctiva",
        id_activo="BOBST_SP126E",
        id_origen="TAREA_5678",
        descripcion="Falla en sistema de succión",
        usuario="pablo",
        proveedor_externo="TecnoComp",
        observaciones="Requiere seguimiento"
    )
