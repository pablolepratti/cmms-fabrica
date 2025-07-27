# modulos/app_mejora.py

import streamlit as st
import pandas as pd
from datetime import datetime
from modulos.estilos import aplicar_estilos
from modulos.conexion_openai import obtener_api_key_openai
from modulos.conexion_mongo import db
from openai import OpenAI
import json

# Configuración general
ASISTENTE_ID = "mejora"
COSTO_INPUT = 0.005 / 1000
COSTO_OUTPUT = 0.015 / 1000
CSV_USO = "uso_api.csv"
LIMITE_USD_MENSUAL = 10.0

# Funciones auxiliares
def registrar_uso(asistente, tokens_in, tokens_out):
    costo = tokens_in * COSTO_INPUT + tokens_out * COSTO_OUTPUT
    fecha = datetime.now().strftime("%Y-%m-%d")
    nuevo = pd.DataFrame([[fecha, asistente, tokens_in, tokens_out, costo]],
                         columns=["fecha", "asistente", "tokens_input", "tokens_output", "costo_usd"])
    try:
        df = pd.read_csv(CSV_USO)
        df = pd.concat([df, nuevo], ignore_index=True)
    except FileNotFoundError:
        df = nuevo
    df.to_csv(CSV_USO, index=False)
    return costo

def calcular_total_mes():
    try:
        df = pd.read_csv(CSV_USO)
        df["fecha"] = pd.to_datetime(df["fecha"])
        mes_actual = datetime.now().month
        return df[df["fecha"].dt.month == mes_actual]["costo_usd"].sum()
    except:
        return 0.0

def obtener_muestra_codigo():
    archivos = ["app.py"]
    carpetas = ["crud", "modulos"]
    fragmentos = []
    for carpeta in carpetas:
        try:
            import os
            for archivo in os.listdir(carpeta):
                if archivo.endswith(".py"):
                    with open(os.path.join(carpeta, archivo), "r", encoding="utf-8") as f:
                        contenido = f.read()
                        fragmentos.append(f"# {carpeta}/{archivo}\n" + contenido[:1000])
        except Exception:
            continue
    return "\n\n".join([f"# {a}\n" + open(a).read()[:1000] for a in archivos]) + "\n\n" + "\n\n".join(fragmentos[:3])

def app():
    obtener_api_key_openai()
    aplicar_estilos()
    st.title("🧰 Asistente de Mejora Continua del CMMS")

    client = OpenAI()
    consulta = st.text_area("¿Qué parte del sistema querés mejorar o revisar?")

    colecciones = db.list_collection_names()
    col_seleccionada = st.selectbox("Seleccioná una colección para mostrar contexto (opcional):", ["(ninguna)"] + colecciones)

    contexto = ""
    if col_seleccionada != "(ninguna)":
        docs = list(db[col_seleccionada].find().limit(3))
        for d in docs:
            d.pop("_id", None)
        contexto = json.dumps(docs, indent=2)

    codigo = obtener_muestra_codigo()

    if consulta:
        total_mes = calcular_total_mes()
        if total_mes >= LIMITE_USD_MENSUAL:
            st.error("🚫 Se alcanzó el límite mensual ($10 USD). Esperá al próximo mes o ajustá el tope.")
        else:
            with st.spinner("Revisando el sistema..."):
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "Sos un ingeniero digital que mejora sistemas CMMS reales, basados en Python y MongoDB. Leés el código, analizás estructuras y proponés mejoras prácticas y trazables. Respondé claro, con criterio industrial."},
                        {"role": "user", "content": f"CONSULTA: {consulta}\n\nCÓDIGO:```python\n{codigo}```\n\nBASE DE DATOS:```json\n{contexto}```"}
                    ]
                )
                respuesta = response.choices[0].message.content
                tokens_in = response.usage.prompt_tokens
                tokens_out = response.usage.completion_tokens
                costo = registrar_uso(ASISTENTE_ID, tokens_in, tokens_out)
                st.success(respuesta)
                st.caption(f"Consulta registrada – Tokens: {tokens_in + tokens_out} | Costo: ${costo:.4f} USD")
