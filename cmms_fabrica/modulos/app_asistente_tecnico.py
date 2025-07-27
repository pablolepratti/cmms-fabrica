# modulos/app_asistente_tecnico.py

import streamlit as st
import pandas as pd
from datetime import datetime
from modulos.estilos import aplicar_estilos
from modulos.conexion_openai import obtener_api_key_openai
from openai import OpenAI

# Configuración general
ASISTENTE_ID = "tecnico"
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

def app():
    obtener_api_key_openai()
    aplicar_estilos()
    st.title("🤖 Asistente Técnico Industrial")

    client = OpenAI()  # Cliente OpenAI ya toma la API Key desde la variable de entorno

    consulta = st.text_area("Ingresá tu consulta técnica de mantenimiento:")

    if consulta:
        total_mes = calcular_total_mes()
        if total_mes >= LIMITE_USD_MENSUAL:
            st.error("🚫 Se alcanzó el límite mensual de uso del asistente ($10 USD). Esperá al próximo mes o ajustá el tope.")
        else:
            with st.spinner("Consultando al asistente..."):
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "Sos Pablo, un técnico industrial uruguayo con calle y experiencia real en planta. Respondé directo, con criterio, sin vueltas. Usás normas ISO cuando aplican. No des discursos, resolvé. Si algo no te convence, decilo."},
                        {"role": "user", "content": consulta}
                    ]
                )
                respuesta = response.choices[0].message.content
                tokens_in = response.usage.prompt_tokens
                tokens_out = response.usage.completion_tokens
                costo = registrar_uso(ASISTENTE_ID, tokens_in, tokens_out)
                st.success(respuesta)
                st.caption(f"Consulta registrada – Tokens: {tokens_in + tokens_out} | Costo: ${costo:.4f} USD")
