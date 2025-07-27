# modulos/conexion_openai.py
import os
import openai
import streamlit as st

def obtener_api_key_openai():
    """
    Carga la API key de OpenAI desde variables de entorno.
    Prioriza seguridad y compatibilidad con Render.
    """
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        st.error("🔐 No se encontró la clave API de OpenAI. Verificá tu archivo .env o variables de entorno en Render.")
        st.stop()

    openai.api_key = api_key
    return api_key
