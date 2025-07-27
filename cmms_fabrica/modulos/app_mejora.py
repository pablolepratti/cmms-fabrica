# modulos/app_mejora.py

import streamlit as st
import pandas as pd
import json
from datetime import datetime
from openai import OpenAI
from modulos.estilos import aplicar_estilos
from modulos.conexion_mongo import db
from modulos.conexion_openai import obtener_api_key_openai

# Configuración general
ASISTENTE_ID = "mejora"
COSTO_INPUT = 0.005 / 1000
COSTO_OUTPUT = 0.015 / 1000
CSV_USO = "uso_api.csv"
LIMITE_USD_MENSUAL = 10.0

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

def serializar_documentos(doc_list):
    def convertir(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return obj
    return json.dumps(doc_list, default=convertir)

def app():
    obtener_api_key_openai()
    aplicar_estilos()
    st.title("🧰 Asistente de Mejora Continua")

    client = OpenAI()
    consulta = st.text_area("¿Qué parte del sistema querés mejorar o revisar?")

    colecciones = db.list_collection_names()
    coleccion = st.selectbox("Seleccioná una colección para mostrar contexto (opcional):", [""] + colecciones)

    if consulta:
        total_mes = calcular_total_mes()
        if total_mes >= LIMITE_USD_MENSUAL:
            st.error("🚫 Límite mensual alcanzado ($10 USD).")
        else:
            contexto = ""
            if coleccion:
                docs = list(db[coleccion].find().limit(50))
                contexto = serializar_documentos(docs)[:4000]  # recorte por tokens

            with st.spinner("Analizando propuesta de mejora..."):
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "Sos un ingeniero digital experto en mantenimiento industrial, sistemas CMMS y normas ISO. Ayudás a revisar código, mejorar módulos, sugerir mejoras reales y mantener la coherencia del sistema."},
                        {"role": "user", "content": f"Consulta: {consulta}\n\nContexto (JSON): {contexto}"}
                    ]
                )
                respuesta = response.choices[0].message.content
                tokens_in = response.usage.prompt_tokens
                tokens_out = response.usage.completion_tokens
                costo = registrar_uso(ASISTENTE_ID, tokens_in, tokens_out)
                st.success(respuesta)
                st.caption(f"Consulta registrada – Tokens: {tokens_in + tokens_out} | Costo: ${costo:.4f} USD")
