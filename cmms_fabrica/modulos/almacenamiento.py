from datetime import datetime
from crud.generador_historial import registrar_evento_historial
from modulos.conexion_mongo import db

LIMITE_MB = 400

# Colecciones a rotar, campo por el que se ordenan (más antiguos primero)
colecciones_rotables = {
    "historial": "fecha",
    "observaciones": "fecha",
    "tareas": "ultima_ejecucion",
    "servicios": "fecha_realizacion"
}

def obtener_tamano_total_mb():
    """Obtiene el tamaño total estimado de la base de datos Mongo en MB."""
    stats = db.command("dbstats")
    total_bytes = stats.get("storageSize", 0)
    return total_bytes / (1024 * 1024)

def limpiar_coleccion(nombre, campo_fecha, porcentaje=0.3, minimo=100):
    """Elimina los documentos más antiguos de una colección si tiene muchos registros"""
    coleccion = db[nombre]
    total = coleccion.count_documents({})

    if total < minimo:
        return 0

    cantidad_a_eliminar = int(total * porcentaje)
    documentos = coleccion.find({}, {"_id": 1, campo_fecha: 1}).sort(campo_fecha, 1).limit(cantidad_a_eliminar)
    ids_a_borrar = [doc["_id"] for doc in documentos if campo_fecha in doc]

    if ids_a_borrar:
        coleccion.delete_many({"_id": {"$in": ids_a_borrar}})
        registrar_evento_historial(
            "limpieza",
            None,
            nombre,
            f"Se eliminaron {len(ids_a_borrar)} documentos.",
            "sistema",
        )
        return len(ids_a_borrar)

    return 0

def ejecutar_limpieza_si_es_necesario():
    uso_actual = obtener_tamano_total_mb()
    if uso_actual < LIMITE_MB:
        return False

    total_eliminados = 0
    for nombre, campo_fecha in sorted(colecciones_rotables.items(), key=lambda x: db[x[0]].estimated_document_count(), reverse=True):
        eliminados = limpiar_coleccion(nombre, campo_fecha)
        total_eliminados += eliminados
        if obtener_tamano_total_mb() < LIMITE_MB:
            break

    return total_eliminados > 0
