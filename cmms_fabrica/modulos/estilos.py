import streamlit as st

def mobile():
    """Detecta si el usuario accede desde un dispositivo móvil y ajusta el ancho de página."""
    is_mobile = False

    if st.browser.user_agent and "Mobile" in st.browser.user_agent:
        is_mobile = True

    st.session_state["is_mobile"] = is_mobile

    if is_mobile:
        st.set_page_config(layout="centered")
    else:
        st.set_page_config(layout="wide")
