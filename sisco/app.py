"""
SISCO — Sistema de Información de Sesiones de Consejo General
Entry point principal
"""
import streamlit as st
from sisco.database.db import init_db
from sisco.utils.styles import inject, header, MAGENTA, MUTED

# Inicializar BD al arrancar
init_db()

st.set_page_config(
    page_title="SISCO",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject(st)
st.markdown(header("Sistema de Información de Sesiones", "Consejo General y Junta General — IEEM"), unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
col1.info("📚 **Catálogo**\nIntegrantes y partidos")
col2.info("📋 **Orden del Día**\nRegistro previo a la sesión")
col3.info("🎙️ **Seguimiento**\nCaptura durante la sesión")
col4.info("📊 **Reportes**\nWord y Excel descargables")
