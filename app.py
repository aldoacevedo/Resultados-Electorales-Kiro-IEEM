"""Portada — Sistema de Consulta Electoral IEEM"""

import streamlit as st
import base64
import os

st.set_page_config(
    page_title="Sistema Electoral IEEM",
    page_icon="🗳️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Paleta ────────────────────────────────────────────────────────────────────
MAGENTA = "#e91e8c"
GRIS    = "#f5f5f5"
TEXTO   = "#222222"
MUTED   = "#666666"

st.markdown(f"""
<style>
  .stApp {{ background-color: #ffffff; }}
  #MainMenu {{ visibility: hidden; }}
  footer {{ visibility: hidden; }}
  header {{ visibility: hidden; }}
  .block-container {{ padding-top: 2rem; }}
  [data-testid="collapsedControl"] {{ display: none !important; }}
  [data-testid="stSidebar"] {{ display: none !important; }}

  .portada-wrapper {{
      display: flex;
      flex-direction: column;
      align-items: center;
      text-align: center;
      padding: 2rem 1rem 1rem 1rem;
  }}
  .linea-magenta {{
      width: 60px;
      height: 4px;
      background: {MAGENTA};
      margin: 1.2rem auto;
      border-radius: 2px;
  }}
  .titulo {{
      font-size: 2rem;
      font-weight: 800;
      color: {TEXTO};
      line-height: 1.2;
      margin-bottom: 0.3rem;
  }}
  .subtitulo {{
      font-size: 1rem;
      color: {MAGENTA};
      font-weight: 600;
      letter-spacing: 1px;
      margin-bottom: 1.5rem;
  }}
  .descripcion {{
      font-size: 1rem;
      color: {MUTED};
      max-width: 560px;
      line-height: 1.7;
      margin: 0 auto 2rem auto;
  }}
  .ieem-logo {{
      font-size: 3rem;
      font-weight: 900;
      color: {TEXTO};
      letter-spacing: 6px;
      line-height: 1;
  }}
  .ieem-sub {{
      font-size: 0.7rem;
      color: {MUTED};
      letter-spacing: 1px;
      margin-top: 0.2rem;
  }}
  .divider {{
      border: none;
      border-top: 1px solid #e0e0e0;
      margin: 2rem auto;
      width: 80%;
  }}
  .footer-txt {{
      font-size: 0.7rem;
      color: #bbbbbb;
      margin-top: 2rem;
  }}
  /* Botón Entrar */
  div[data-testid="stButton"] > button {{
      background-color: {MAGENTA} !important;
      color: white !important;
      border: none !important;
      border-radius: 8px !important;
      font-size: 1.1rem !important;
      font-weight: 700 !important;
      padding: 0.8rem 3rem !important;
      letter-spacing: 1px !important;
      width: 100%;
      max-width: 320px;
      transition: opacity 0.2s;
  }}
  div[data-testid="stButton"] > button:hover {{
      opacity: 0.85 !important;
  }}
</style>
""", unsafe_allow_html=True)

# ── Logo ──────────────────────────────────────────────────────────────────────
logo_path = "assets/logo_ieem.png"
if os.path.exists(logo_path):
    with open(logo_path, "rb") as f:
        logo_b64 = base64.b64encode(f.read()).decode()
    st.markdown(
        f'<div style="text-align:center;margin-bottom:0.5rem;">'
        f'<img src="data:image/png;base64,{logo_b64}" height="80">'
        f'</div>',
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        f'<div style="text-align:center;margin-bottom:0.5rem;">'
        f'<div class="ieem-logo">IEEM</div>'
        f'<div class="ieem-sub">Instituto Electoral del Estado de México</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

# ── Contenido ─────────────────────────────────────────────────────────────────
st.markdown('<div class="linea-magenta"></div>', unsafe_allow_html=True)

st.markdown('<div class="titulo">Sistema de Consulta Electoral</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitulo">GUBERNATURA · ESTADO DE MÉXICO</div>', unsafe_allow_html=True)

st.markdown("""
<div class="descripcion">
Este sistema es una herramienta de información y análisis electoral desarrollada
con base en los resultados oficiales publicados por el
<strong>Instituto Electoral del Estado de México (IEEM)</strong>
para las elecciones de Gobernador de los años
<strong>2005, 2011, 2017 y 2023</strong>.<br><br>
Permite consultar resultados por partido y coalición, comparar participación
y abstención, explorar el comportamiento electoral por distrito y visualizar
los datos en gráficas, tablas y mapas interactivos.
</div>
""", unsafe_allow_html=True)

# ── Botón ─────────────────────────────────────────────────────────────────────
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("🗳️  Entrar al sistema"):
        st.switch_page("pages/1_Sistema.py")

st.markdown('<hr class="divider">', unsafe_allow_html=True)
st.markdown(
    '<div class="footer-txt">Los datos utilizados son de acceso público y fueron publicados por el IEEM.<br>'
    'Este sistema es de carácter informativo.</div>',
    unsafe_allow_html=True,
)
