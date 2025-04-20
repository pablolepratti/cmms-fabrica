import streamlit as st

def mobile():
    """
    Aplica un estilo base adaptable. Por ahora, no detecta si es móvil,
    pero puede extenderse usando JavaScript o cookies en el futuro.
    """
    st.markdown(
        """
        <style>
            /* Estilos generales para toda la app */
            html, body, [data-testid="stApp"] {
                background-color: #0e1117;
                color: white;
            }

            /* Personalizar botones */
            .stButton>button {
                background-color: #2c7be5;
                color: white;
                border-radius: 0.5rem;
                padding: 0.4rem 1rem;
                font-weight: bold;
            }

            /* Inputs más suaves */
            .stTextInput>div>div>input {
                border-radius: 0.5rem;
                padding: 0.5rem;
                background-color: #1e222a;
                color: white;
            }

            /* Centrar títulos */
            h1, h2, h3 {
                text-align: center;
            }
        </style>
        """,
        unsafe_allow_html=True
    )
