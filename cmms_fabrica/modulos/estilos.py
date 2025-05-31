import streamlit as st

def aplicar_estilos():
    """
    Estilos generales de la app CMMS Fábrica.
    Adaptado para un diseño limpio, oscuro y responsive.
    """
    st.markdown(
        """
        <style>
            /* Fondo y texto base */
            html, body, [data-testid="stApp"] {
                background-color: #0e1117;
                color: white;
            }

            /* Botones */
            .stButton>button {
                background-color: #2c7be5;
                color: white;
                border-radius: 0.5rem;
                padding: 0.5rem 1rem;
                font-weight: bold;
                transition: 0.2s ease-in-out;
            }
            .stButton>button:hover {
                background-color: #1a5ecf;
                transform: scale(1.02);
            }

            /* Inputs */
            .stTextInput>div>div>input,
            .stTextArea textarea,
            .stDateInput input,
            .stSelectbox>div>div>div {
                background-color: #1e222a;
                color: white;
                border-radius: 0.4rem;
            }

            /* Títulos centrados */
            h1, h2, h3 {
                text-align: center;
            }
        </style>
        """,
        unsafe_allow_html=True
    )
