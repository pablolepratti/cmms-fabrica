import csv
import os
import pandas as pd

RUTA_CSV = os.path.join("data", "maquinas.csv")

# Cargar máquinas como DataFrame
def cargar_maquinas():
    return pd.read_csv(RUTA_CSV)

# Guardar DataFrame actualizado
def guardar_maquinas(df):
    df.to_csv(RUTA_CSV, index=False)

# Listar todas las máquinas
def listar_maquinas():
    return cargar_maquinas()

# Filtrar por tipo_activo
def filtrar_por_tipo(tipo_activo):
    df = cargar_maquinas()
    return df[df["tipo_activo"] == tipo_activo]

# Filtrar por sector
def filtrar_por_sector(sector):
    df = cargar_maquinas()
    return df[df["sector"] == sector]

# Obtener una máquina por ID
def obtener_maquina(id_maquina):
    df = cargar_maquinas()
    resultado = df[df["id"] == id_maquina]
    return resultado if not resultado.empty else None

# Editar una máquina existente
def editar_maquina(id_maquina, campo, nuevo_valor):
    df = cargar_maquinas()
    if id_maquina in df["id"].values:
        df.loc[df["id"] == id_maquina, campo] = nuevo_valor
        guardar_maquinas(df)
        return True
    return False

# Agregar nueva máquina
def agregar_maquina(nueva_maquina: dict):
    df = cargar_maquinas()
    df = pd.concat([df, pd.DataFrame([nueva_maquina])], ignore_index=True)
    guardar_maquinas(df)

# Eliminar una máquina
def eliminar_maquina(id_maquina):
    df = cargar_maquinas()
    df = df[df["id"] != id_maquina]
    guardar_maquinas(df)
