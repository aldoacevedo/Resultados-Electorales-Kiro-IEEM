"""Portada — Sistema de Consulta Electoral IEEM"""

import streamlit as st
import base64
import os

# ── Navegación multipage con nueva API ───────────────────────────────────────
portada  = st.Page("pages/portada.py",  title="Inicio",   icon="🏠", default=True)
sistema  = st.Page("pages/1_Sistema.py", title="Sistema", icon="🗳️")

pg = st.navigation([portada, sistema], position="hidden")
pg.run()
