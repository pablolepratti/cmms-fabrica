# modulos/app_asistente_tecnico.py

import streamlit as st
import pandas as pd
from datetime import datetime
from modulos.estilos import aplicar_estilos
from modulos.conexion_openai import obtener_api_key_openai
from modulos.conexion_mongo import db
from openai import OpenAI

# Config general
ASISTENTE_ID = "tecnico"
COSTO_INPUT = 0.005 / 1000
COSTO_OUTPUT = 0.015 / 1000
CSV_USO = "uso_api.csv"
LIMITE_USD_MENSUAL = 10.0

# Registrar uso

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

# Calcular total mensual

def calcular_total_mes():
    try:
        df = pd.read_csv(CSV_USO)
        df["fecha"] = pd.to_datetime(df["fecha"])
        mes_actual = datetime.now().month
        return df[df["fecha"].dt.month == mes_actual]["costo_usd"].sum()
    except:
        return 0.0

# App principal

def app():
    obtener_api_key_openai()
    aplicar_estilos()
    st.title("🤖 Asistente Técnico Industrial")

    client = OpenAI()

    colecciones = db.list_collection_names()
    coleccion = st.selectbox("Seleccioná una colección de MongoDB para analizar:", colecciones)

    if coleccion:
        limite = st.slider("¿Cuántos documentos querés mostrar como contexto?", 1, 50, 10)
        documentos = list(db[coleccion].find().limit(limite))
        df = pd.DataFrame(documentos)

        if not df.empty:
            st.dataframe(df)

            consulta = st.text_area("¿Qué querés preguntarle al asistente con base en estos datos?")

            if consulta:
                total_mes = calcular_total_mes()
                if total_mes >= LIMITE_USD_MENSUAL:
                    st.error("🚫 Se alcanzó el límite mensual de uso del asistente ($10 USD). Esperá al próximo mes o ajustá el tope.")
                else:
                    with st.spinner("Consultando al asistente con datos reales..."):
                        contexto = df.to_json(orient="records")[:5000]  # recorte para no pasar tokens de más

                        response = client.chat.completions.create(
                            model="gpt-4o",
                            messages=[
                                {"role": "system", "content": "Sos un técnico industrial uruguayo con calle y experiencia real en planta. Respondé claro, directo, sin vueltas. Usás normas ISO cuando aplican. Tenés acceso parcial a datos reales de mantenimiento (formato JSON)."},
                                {"role": "user", "content": f"Consulta: {consulta}\n\nDatos disponibles:\n{contexto}"}
                            ]
                        )
                        respuesta = response.choices[0].message.content
                        tokens_in = response.usage.prompt_tokens
                        tokens_out = response.usage.completion_tokens
                        costo = registrar_uso(ASISTENTE_ID, tokens_in, tokens_out)
                        st.success(respuesta)
                        st.caption(f"Consulta registrada – Tokens: {tokens_in + tokens_out} | Costo: ${costo:.4f} USD")

        else:
            st.warning("La colección está vacía o no pudo cargarse.")
