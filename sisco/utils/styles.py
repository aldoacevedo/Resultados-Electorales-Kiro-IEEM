"""
CSS global compartido por todas las páginas de SISCO.
"""

MAGENTA = "#e91e8c"
MUTED   = "#888888"
BG      = "#ffffff"
SIDEBAR = "#f5f5f5"
TEXT    = "#1a1a1a"

CSS = f"""
<style>
  /* ── Quitar márgenes gigantes de Streamlit ── */
  .block-container {{
      padding-top: 1rem !important;
      padding-bottom: 1rem !important;
      padding-left: 1.5rem !important;
      padding-right: 1.5rem !important;
      max-width: 100% !important;
  }}

  /* ── Fondo y texto base ── */
  .stApp {{ background-color: {BG}; color: {TEXT}; font-size: 15px; }}

  /* ── Sidebar ── */
  [data-testid="stSidebar"] {{
      background-color: {SIDEBAR} !important;
      border-right: 3px solid {MAGENTA};
  }}
  [data-testid="stSidebar"] * {{ color: {TEXT} !important; font-size: 14px; }}
  [data-testid="stSidebarNav"] a {{
      padding: 0.4rem 0.8rem !important;
      border-radius: 6px;
  }}
  [data-testid="stSidebarNav"] a:hover {{
      background-color: #ffe0f0 !important;
  }}

  /* ── Header oculto ── */
  #MainMenu {{ visibility: hidden; }}
  footer {{ visibility: hidden; }}
  .stAppHeader {{ display: none; }}
  header[data-testid="stHeader"] {{ display: none; }}

  /* ── Títulos más compactos ── */
  h1 {{ font-size: 1.5rem !important; margin-bottom: 0.4rem !important; color: {TEXT}; }}
  h2 {{ font-size: 1.2rem !important; margin-bottom: 0.3rem !important; }}
  h3 {{ font-size: 1.05rem !important; margin-bottom: 0.2rem !important; }}

  /* ── Tabs ── */
  .stTabs [data-baseweb="tab-list"] {{
      gap: 2px;
      background-color: {SIDEBAR};
      border-radius: 6px 6px 0 0;
      padding: 0 4px;
  }}
  .stTabs [data-baseweb="tab"] {{
      font-size: 13px !important;
      padding: 6px 14px !important;
      color: {MUTED} !important;
      background: transparent !important;
  }}
  .stTabs [aria-selected="true"] {{
      color: {TEXT} !important;
      background: {BG} !important;
      border-bottom: 2px solid {MAGENTA} !important;
      font-weight: 600 !important;
  }}
  .stTabs [data-baseweb="tab-panel"] {{
      padding: 0.8rem 0.2rem !important;
  }}

  /* ── Botones ── */
  .stButton > button {{
      font-size: 13px !important;
      padding: 0.3rem 1rem !important;
      border-radius: 6px !important;
  }}
  .stButton > button[kind="primary"] {{
      background-color: {MAGENTA} !important;
      color: white !important;
      border: none !important;
  }}
  .stDownloadButton > button {{
      background-color: {MAGENTA} !important;
      color: white !important;
      border: none !important;
      border-radius: 6px !important;
      font-size: 13px !important;
  }}

  /* ── Inputs más compactos ── */
  .stTextInput > div > div > input,
  .stTextArea > div > textarea,
  .stSelectbox > div > div {{
      font-size: 14px !important;
  }}
  .stTextInput label, .stSelectbox label,
  .stTextArea label, .stNumberInput label,
  .stDateInput label, .stRadio label,
  .stCheckbox label {{
      font-size: 13px !important;
      color: {MUTED} !important;
      margin-bottom: 2px !important;
  }}

  /* ── Métricas ── */
  [data-testid="stMetric"] {{
      background-color: #fafafa !important;
      border-radius: 8px;
      padding: 0.5rem 0.8rem !important;
      border-left: 3px solid {MAGENTA};
  }}
  [data-testid="stMetricLabel"] p {{ font-size: 0.72rem !important; color: {MUTED} !important; }}
  [data-testid="stMetricValue"]  {{ font-size: 1.3rem !important; color: {TEXT} !important; }}

  /* ── Expanders ── */
  .streamlit-expanderHeader {{
      font-size: 13px !important;
      padding: 0.4rem 0.6rem !important;
  }}
  .streamlit-expanderContent {{
      padding: 0.5rem 0.6rem !important;
  }}

  /* ── Dataframes ── */
  .stDataFrame {{ font-size: 13px !important; }}

  /* ── Divider ── */
  hr {{ margin: 0.6rem 0 !important; border-color: #e8e8e8; }}

  /* ── Info / warning boxes ── */
  [data-testid="stAlert"] {{
      padding: 0.5rem 0.8rem !important;
      font-size: 13px !important;
      border-left: 3px solid {MAGENTA} !important;
  }}
</style>
"""


def header(titulo: str, subtitulo: str = "") -> str:
    """Genera el header institucional de cada página."""
    sub = f'<div style="font-size:0.72rem;color:{MUTED};margin-top:2px;">{subtitulo}</div>' if subtitulo else ""
    return (
        f'<div style="background:#f5f5f5;border-bottom:3px solid {MAGENTA};'
        f'padding:0.6rem 1rem;margin-bottom:1rem;border-radius:0 0 4px 4px;">'
        f'<span style="font-size:1.4rem;font-weight:900;color:{MAGENTA};'
        f'letter-spacing:2px;margin-right:10px;">SISCO</span>'
        f'<span style="font-size:1rem;font-weight:600;color:{TEXT};">{titulo}</span>'
        f'{sub}</div>'
    )


def inject(st_instance):
    """Inyecta el CSS global en la página actual."""
    st_instance.markdown(CSS, unsafe_allow_html=True)
