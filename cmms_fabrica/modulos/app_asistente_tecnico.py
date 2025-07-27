# modulos/app_asistente_tecnico.py

import streamlit as st
import openai
import pandas as pd
from datetime import datetime
from modulos.estilos import estilo_formulario
import os

openai.api_key = os.getenv("OPENAI_API_KEY")


# Configuración general
ASISTENTE_ID = "tecnico"
COSTO_INPUT = 0.005 / 1000   # USD por token de entrada
COSTO_OUTPUT = 0.015 / 1000  # USD por token de salida
CSV_USO = "uso_api.csv"
LIMITE_USD_MENSUAL = 10.0

# UI
st.title("🤖 Asistente Técnico Industrial")
estilo_formulario()
consulta = st.text_area("Ingresá tu consulta técnica de mantenimiento:")

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

# Procesamiento
if consulta:
    total_mes = calcular_total_mes()
    if total_mes >= LIMITE_USD_MENSUAL:
        st.error("🚫 Se alcanzó el límite mensual de uso del asistente ($10 USD). Esperá al próximo mes o ajustá el tope.")
    else:
        with st.spinner("Consultando al asistente..."):
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Sos un asistente técnico industrial en una fábrica real. Respondé claro, con criterio de mantenimiento. Usás normas ISO 55001, ISO 9001 e ISO 14224."},
                    {"role": "user", "content": consulta}
                ]
            )
            respuesta = response.choices[0].message.content
            tokens_in = response["usage"]["prompt_tokens"]
            tokens_out = response["usage"]["completion_tokens"]
            costo = registrar_uso(ASISTENTE_ID, tokens_in, tokens_out)
            st.success(respuesta)
            st.caption(f"Consulta registrada – Tokens: {tokens_in + tokens_out} | Costo: ${costo:.4f} USD")
