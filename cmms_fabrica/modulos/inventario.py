import csv
import os
import pandas as pd
from datetime import datetime

RUTA_CSV = os.path.join("data", "inventario.csv")

# Cargar inventario
def cargar_inventario():
    return pd.read_csv(RUTA_CSV)

# Guardar inventario
def guardar_inventario(df):
    df.to_csv(RUTA_CSV, index=False)

# Listar todos los ítems
def listar_items():
    return cargar_inventario()

# Buscar por tipo (repuesto o insumo)
def buscar_por_tipo(tipo):
    df = cargar_inventario()
    return df[df["tipo"] == tipo]

# Buscar ítems compatibles con una máquina
def buscar_por_maquina(id_maquina):
    df = cargar_inventario()
    return df[df["maquina_compatible"] == id_maquina]

# Ver ítems con stock crítico
def ver_items_criticos():
    df = cargar_inventario()
    return df[df["cantidad"] <= df["stock_minimo"]]

# Actualizar stock (sumar o restar)
def actualizar_stock(id_item, cantidad_usada, uso_destino, destino_descripcion, usuario):
    df = cargar_inventario()
    if id_item in df["id_item"].values:
        index = df[df["id_item"] == id_item].index[0]
        df.at[index, "cantidad"] = max(0, df.at[index, "cantidad"] - cantidad_usada)
        df.at[index, "ultima_actualizacion"] = datetime.today().strftime("%Y-%m-%d")
        guardar_inventario(df)
        from modulos.historial import log_evento
        detalle = f"Usado para {uso_destino}: {destino_descripcion} - {cantidad_usada} {df.at[index, 'unidad']}"
        log_evento(usuario, "Uso de inventario", id_item, "inventario", detalle)
        return True
    return False

# Agregar nuevo ítem
def agregar_item(item_dict):
    df = cargar_inventario()
    df = pd.concat([df, pd.DataFrame([item_dict])], ignore_index=True)
    guardar_inventario(df)

# Editar ítem existente
def editar_item(id_item, campo, nuevo_valor):
    df = cargar_inventario()
    if id_item in df["id_item"].values:
        df.loc[df["id_item"] == id_item, campo] = nuevo_valor
        guardar_inventario(df)
        return True
    return False
