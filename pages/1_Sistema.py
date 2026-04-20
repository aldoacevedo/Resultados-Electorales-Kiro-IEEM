"""
Sistema de Consulta Electoral — Gubernatura Estado de México
2005 · 2011 · 2017 · 2023
"""

import streamlit as st
import pandas as pd
import json
import os
import base64

from data.loader import cargar_todos, totales_estatales, FUERZAS_POR_ANIO, COLORES
from charts.plots import (
    grafico_barras_anio,
    grafico_comparativo_fuerzas,
    grafico_pie_anio,
    grafico_participacion,
    grafico_evolucion_fuerza,
    grafico_distritos,
    grafico_mapa_shp,
    tabla_distritos,
)

# ── Configuración de página ───────────────────────────────────────────────────
st.set_page_config(
    page_title="Análisis Electoral — IEEM",
    page_icon="🗳️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Botón para volver a la portada en el sidebar
with st.sidebar:
    st.markdown(
        '<a href="/" target="_self" style="'
        'color:#e91e8c;text-decoration:none;font-weight:600;font-size:0.85rem;">'
        '← Portada</a>',
        unsafe_allow_html=True,
    )

# ── Paleta IEEM ───────────────────────────────────────────────────────────────
IEEM_DARK    = "#ffffff"
IEEM_DARKER  = "#f5f5f5"
IEEM_MAGENTA = "#e91e8c"
IEEM_SIDEBAR = "#f0f0f0"
IEEM_CARD    = "#f8f8f8"
IEEM_TEXT    = "#222222"
IEEM_MUTED   = "#666666"

# ── CSS global ────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
  /* Fondo general */
  .stApp {{ background-color: #ffffff; color: {IEEM_TEXT}; }}

  /* Sidebar */
  [data-testid="stSidebar"] {{
      background-color: {IEEM_SIDEBAR} !important;
      border-right: 2px solid {IEEM_MAGENTA};
  }}
  [data-testid="stSidebar"] * {{ color: {IEEM_TEXT} !important; }}

  /* Header superior */
  .ieem-header {{
      background-color: {IEEM_DARKER};
      border-bottom: 3px solid {IEEM_MAGENTA};
      padding: 0.6rem 1.5rem;
      display: flex;
      align-items: center;
      gap: 1.2rem;
      margin-bottom: 1rem;
  }}
  .ieem-logo-text {{
      font-size: 1.6rem;
      font-weight: 900;
      color: {IEEM_TEXT};
      letter-spacing: 2px;
      line-height: 1;
  }}
  .ieem-logo-sub {{
      font-size: 0.62rem;
      color: {IEEM_MUTED};
      letter-spacing: 0.5px;
      line-height: 1.3;
  }}
  .ieem-logo-divider {{
      width: 2px;
      height: 40px;
      background: {IEEM_MAGENTA};
      margin: 0 0.5rem;
  }}
  .ieem-title {{
      font-size: 1.3rem;
      font-weight: 600;
      color: {IEEM_TEXT};
  }}
  .ieem-subtitle {{
      font-size: 0.75rem;
      color: {IEEM_MUTED};
  }}

  /* Métricas */
  [data-testid="stMetric"] {{
      background-color: {IEEM_CARD} !important;
      border-radius: 8px;
      padding: 0.7rem 1rem !important;
      border-left: 3px solid {IEEM_MAGENTA};
      box-shadow: 0 1px 4px rgba(0,0,0,0.08);
  }}
  [data-testid="stMetricLabel"] p {{ color: {IEEM_MUTED} !important; font-size: 0.75rem !important; }}
  [data-testid="stMetricValue"]  {{ color: {IEEM_TEXT}  !important; font-size: 1.4rem !important; }}
  [data-testid="stMetricDelta"]  {{ color: {IEEM_MAGENTA} !important; }}

  /* Tabs */
  .stTabs [data-baseweb="tab-list"] {{
      background-color: {IEEM_SIDEBAR};
      border-radius: 8px 8px 0 0;
      gap: 4px;
  }}
  .stTabs [data-baseweb="tab"] {{
      color: {IEEM_MUTED} !important;
      background-color: transparent !important;
      border-radius: 6px 6px 0 0;
  }}
  .stTabs [aria-selected="true"] {{
      color: {IEEM_TEXT} !important;
      background-color: #ffffff !important;
      border-bottom: 2px solid {IEEM_MAGENTA} !important;
  }}
  .stTabs [data-baseweb="tab-panel"] {{
      background-color: #ffffff;
      border-radius: 0 0 8px 8px;
      padding: 1rem;
      border: 1px solid #e0e0e0;
  }}

  /* Botón descarga */
  .stDownloadButton button {{
      background-color: {IEEM_MAGENTA} !important;
      color: white !important;
      border: none !important;
      border-radius: 6px !important;
  }}

  /* Divider */
  hr {{ border-color: #e0e0e0; }}

  /* Info box */
  [data-testid="stAlert"] {{
      border-left: 3px solid {IEEM_MAGENTA} !important;
  }}

  /* Botón para abrir/cerrar sidebar — siempre visible */
  [data-testid="collapsedControl"] {{
      display: flex !important;
      visibility: visible !important;
      color: {IEEM_MAGENTA} !important;
      background-color: {IEEM_SIDEBAR} !important;
      border-radius: 0 6px 6px 0 !important;
      border: 1px solid {IEEM_MAGENTA} !important;
  }}

  /* Ocultar menú hamburguesa y footer, pero mantener botón del sidebar */
  #MainMenu {{ visibility: hidden; }}
  footer {{ visibility: hidden; }}
  header[data-testid="stHeader"] {{ background: transparent; height: 0; min-height: 0; }}
  .block-container {{ padding-top: 0 !important; padding-bottom: 1rem; }}
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
logo_path = "assets/logo_ieem.png"
if os.path.exists(logo_path):
    with open(logo_path, "rb") as f:
        logo_b64 = base64.b64encode(f.read()).decode()
    logo_img = f'<img src="data:image/png;base64,{logo_b64}" height="44">'
else:
    logo_img = (
        '<div style="display:inline-block;">'
        f'<div style="font-size:2.2rem;font-weight:900;color:{IEEM_MAGENTA};letter-spacing:3px;line-height:1;">IEEM</div>'
        f'<div style="font-size:0.58rem;color:{IEEM_MUTED};line-height:1.3;">Instituto Electoral del<br>Estado de México</div>'
        '</div>'
    )

header_html = (
    f'<div style="background:{IEEM_DARKER};border-bottom:3px solid {IEEM_MAGENTA};'
    f'padding:1rem 1.5rem;display:flex;align-items:center;gap:1.2rem;margin-bottom:1rem;">'
    f'{logo_img}'
    f'<div style="width:2px;height:56px;background:{IEEM_MAGENTA};margin:0 0.3rem;"></div>'
    f'<div>'
    f'<div style="font-size:1.2rem;font-weight:600;color:{IEEM_TEXT};">Análisis Electoral</div>'
    f'<div style="font-size:0.72rem;color:{IEEM_MUTED};">Gubernatura · 2005 · 2011 · 2017 · 2023</div>'
    f'</div>'
    f'</div>'
)
st.markdown(header_html, unsafe_allow_html=True)

# ── Carga de datos ────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def cargar_datos():
    return cargar_todos()

@st.cache_data(show_spinner=False)
def cargar_totales(_datos):
    return totales_estatales(_datos)

datos    = cargar_datos()
totales  = cargar_totales(datos)

# ── GeoJSON ───────────────────────────────────────────────────────────────────
geojson = None
if os.path.exists("data/distritos_edomex.geojson"):
    with open("data/distritos_edomex.geojson", encoding="utf-8") as f:
        geojson = json.load(f)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        f'<div style="text-align:center;padding:0.5rem 0 1rem 0;border-bottom:1px solid {IEEM_MAGENTA};margin-bottom:1rem;">'
        f'<div style="font-size:2.2rem;font-weight:900;color:{IEEM_TEXT};letter-spacing:4px;line-height:1;">IEEM</div>'
        f'<div style="font-size:0.6rem;color:{IEEM_MUTED};">Instituto Electoral del Estado de México</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    st.markdown(f"<div style='color:{IEEM_MAGENTA};font-size:0.7rem;font-weight:600;letter-spacing:1px;margin-bottom:0.5rem;'>NAVEGACIÓN</div>", unsafe_allow_html=True)

    seccion = st.radio(
        "Sección",
        ["📊 Resultados por año", "📈 Comparativo histórico", "🗺️ Mapa por distrito", "📋 Tablas"],
        label_visibility="collapsed",
    )

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(f"<div style='color:{IEEM_MAGENTA};font-size:0.7rem;font-weight:600;letter-spacing:1px;margin-bottom:0.5rem;'>FILTROS</div>", unsafe_allow_html=True)

    anio_global = st.selectbox("Año electoral", [2005, 2011, 2017, 2023])
    porcentual  = st.toggle("Ver en porcentaje", value=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:0.6rem;color:{IEEM_MUTED};text-align:center;'>Elección de Gubernatura<br>Estado de México</div>", unsafe_allow_html=True)

# ── Helpers de gráficas con tema claro ───────────────────────────────────────
PLOT_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="#ffffff",
    font=dict(color=IEEM_TEXT, size=12),
    title_font=dict(color=IEEM_TEXT, size=14),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=IEEM_TEXT)),
    xaxis=dict(gridcolor="#e0e0e0", color=IEEM_TEXT, zerolinecolor="#e0e0e0"),
    yaxis=dict(gridcolor="#e0e0e0", color=IEEM_TEXT, zerolinecolor="#e0e0e0"),
    margin=dict(t=50, b=50, l=60, r=20),
)

def aplicar_tema(fig):
    fig.update_layout(**PLOT_LAYOUT)
    return fig

def fmt_num(v, decimales=0):
    """Formatea número con coma como separador de miles y punto para decimales."""
    if pd.isna(v) or not isinstance(v, (int, float)):
        return "—"
    import math
    if math.isinf(v) or math.isnan(v):
        return "—"
    if decimales == 0:
        return f"{v:,.0f}"
    return f"{v:,.{decimales}f}"

def fmt_pct(v, decimales=1):
    """Formatea porcentaje con punto decimal."""
    if pd.isna(v) or not isinstance(v, (int, float)):
        return "—"
    import math
    if math.isinf(v) or math.isnan(v):
        return "—"
    return f"{v:.{decimales}f}%"

# ═══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 1 — Resultados por año
# ═══════════════════════════════════════════════════════════════════════════════
if seccion == "📊 Resultados por año":
    st.markdown(f"<h3 style='color:{IEEM_TEXT}; margin-bottom:0.5rem;'>Resultados por año</h3>", unsafe_allow_html=True)

    c1, c2 = st.columns([1, 2])
    with c1:
        nivel = st.radio("Nivel geográfico", ["Estatal", "Por distrito"], horizontal=True)
    df_anio = datos[anio_global]

    if nivel == "Por distrito":
        with c2:
            distritos = sorted(df_anio["distrito"].dropna().unique())
            distrito_sel = st.selectbox("Distrito", distritos)
        df_anio = df_anio[df_anio["distrito"] == distrito_sel]

    # Métricas
    total_votos = df_anio["total_votos"].sum()
    lista_nom   = df_anio["lista_nominal"].sum()
    part_pct    = total_votos / lista_nom * 100 if lista_nom else 0
    abst_pct    = 100 - part_pct
    nulos       = df_anio["votos_nulos"].sum()
    nulos_pct   = nulos / total_votos * 100 if total_votos else 0

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Lista nominal",  f"{lista_nom:,.0f}")
    m2.metric("Total votos",    f"{total_votos:,.0f}")
    m3.metric("Votos nulos",    f"{nulos:,.0f} ({nulos_pct:.1f}%)")
    m4.metric("Participación",  f"{part_pct:.1f}%")
    m5.metric("Abstención",     f"{abst_pct:.1f}%")

    st.markdown("<hr>", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📊 Barras", "🥧 Pie", "📍 Por distrito"])

    with tab1:
        fig = grafico_barras_anio(df_anio, anio_global, porcentual)
        st.plotly_chart(aplicar_tema(fig), use_container_width=True)

    with tab2:
        col_pie, col_info = st.columns([2, 1])
        with col_pie:
            fig = grafico_pie_anio(df_anio, anio_global)
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font=dict(color=IEEM_TEXT), legend=dict(font=dict(color=IEEM_TEXT)))
            st.plotly_chart(fig, use_container_width=True)
        with col_info:
            st.markdown(f"<div style='color:{IEEM_MAGENTA}; font-weight:600; margin-bottom:0.5rem;'>Votos por fuerza</div>", unsafe_allow_html=True)
            fuerzas = [f for f in FUERZAS_POR_ANIO[anio_global] if f in df_anio.columns]
            total_val = df_anio["votos_validos"].sum()
            for f in fuerzas:
                v   = df_anio[f].sum()
                pct = v / total_val * 100 if total_val else 0
                st.metric(f, f"{v:,.0f} ({pct:.1f}%)")

    with tab3:
        fuerzas_disp = [f for f in FUERZAS_POR_ANIO[anio_global] if f in datos[anio_global].columns]
        fuerza_sel   = st.selectbox("Fuerza política", fuerzas_disp, key="fuerza_dist")
        fig = grafico_distritos(datos[anio_global], anio_global, fuerza_sel, porcentual)
        st.plotly_chart(aplicar_tema(fig), use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 2 — Comparativo histórico
# ═══════════════════════════════════════════════════════════════════════════════
elif seccion == "📈 Comparativo histórico":
    st.markdown(f"<h3 style='color:{IEEM_TEXT}; margin-bottom:0.5rem;'>Comparativo histórico 2005–2023</h3>", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📊 Fuerzas por año", "📉 Participación / Abstención", "📈 Evolución de fuerza"])

    with tab1:
        fig = grafico_comparativo_fuerzas(totales, porcentual)
        st.plotly_chart(aplicar_tema(fig), use_container_width=True)

    with tab2:
        fig = grafico_participacion(totales)
        st.plotly_chart(aplicar_tema(fig), use_container_width=True)

    with tab3:
        # Fuerzas agrupadas por año, de más reciente a más antiguo
        opciones_agrupadas = []
        etiquetas = {}
        for a in [2023, 2017, 2011, 2005]:
            for f in FUERZAS_POR_ANIO[a]:
                clave = f"{a} — {f}"
                opciones_agrupadas.append(clave)
                etiquetas[clave] = (a, f)

        fuerzas_sel_claves = st.multiselect(
            "Fuerzas políticas (selecciona una o más)",
            opciones_agrupadas,
            default=[opciones_agrupadas[0]],
        )

        if fuerzas_sel_claves:
            import plotly.graph_objects as go
            from data.loader import COLORES
            ANIOS_FIJOS = [2005, 2011, 2017, 2023]
            fig_ev = go.Figure()
            for clave in fuerzas_sel_claves:
                _, fuerza_ev = etiquetas[clave]
                valores_ev = []
                for a in ANIOS_FIJOS:
                    if fuerza_ev in totales.columns and not pd.isna(totales.loc[a, fuerza_ev]):
                        v = totales.loc[a, fuerza_ev]
                        if porcentual:
                            v = v / totales.loc[a, "votos_validos"] * 100
                        valores_ev.append(v)
                    else:
                        valores_ev.append(None)

                color = COLORES.get(fuerza_ev, "#999999")
                textos = [
                    (f"{v:.1f}%" if porcentual else f"{v:,.0f}") if v is not None else ""
                    for v in valores_ev
                ]
                fig_ev.add_trace(go.Scatter(
                    x=ANIOS_FIJOS,
                    y=valores_ev,
                    mode="lines+markers+text",
                    name=clave,
                    text=textos,
                    textposition="top center",
                    line=dict(color="#555555", width=1.5, dash="dot"),
                    marker=dict(size=10, color=color),
                    connectgaps=True,
                ))
            fig_ev.update_layout(
                title="Evolución de fuerzas políticas 2005–2023",
                xaxis_title="Año",
                yaxis_title="% votos válidos" if porcentual else "Votos",
                height=450,
                xaxis=dict(
                    tickmode="array",
                    tickvals=[2005, 2011, 2017, 2023],
                    ticktext=["2005", "2011", "2017", "2023"],
                ),
            )
            st.plotly_chart(aplicar_tema(fig_ev), use_container_width=True)
        else:
            st.info("Selecciona al menos una fuerza política.")

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(f"<div style='color:{IEEM_MAGENTA}; font-weight:600; margin-bottom:0.5rem;'>Resumen estatal por año</div>", unsafe_allow_html=True)
    df_show = totales.copy()
    num_cols = [c for c in df_show.columns if c not in ["participacion", "abstencion"]]
    fmt = {c: "{:,.0f}" for c in num_cols}
    fmt.update({"participacion": "{:.1%}", "abstencion": "{:.1%}"})
    st.dataframe(df_show.style.format(fmt, na_rep="—"), use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 3 — Mapa por distrito
# ═══════════════════════════════════════════════════════════════════════════════
elif seccion == "🗺️ Mapa por distrito":
    st.markdown(f"<h3 style='color:{IEEM_TEXT}; margin-bottom:0.5rem;'>Mapa por distrito</h3>", unsafe_allow_html=True)

    from data.geo_loader import cargar_geo, join_electoral_geo

    fuerzas_m = [f for f in FUERZAS_POR_ANIO[anio_global] if f in datos[anio_global].columns]
    c1, c2 = st.columns([1, 2])
    with c1:
        fuerza_m = st.selectbox("Fuerza política", fuerzas_m)

    @st.cache_data
    def cargar_geo_cached(anio):
        return cargar_geo(anio)

    with st.spinner("Cargando mapa..."):
        gdf = cargar_geo_cached(anio_global)
        gdf_merged = join_electoral_geo(datos[anio_global], gdf)

    fig_mapa = grafico_mapa_shp(gdf_merged, anio_global, fuerza_m, porcentual)
    st.plotly_chart(aplicar_tema(fig_mapa), use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 4 — Tablas
# ═══════════════════════════════════════════════════════════════════════════════
elif seccion == "📋 Tablas":
    st.markdown(f"<h3 style='color:{IEEM_TEXT}; margin-bottom:0.5rem;'>Tablas de resultados por distrito</h3>", unsafe_allow_html=True)

    tabla = tabla_distritos(datos[anio_global], anio_global, porcentual)
    tabla = tabla.replace([float("inf"), float("-inf")], pd.NA)
    tabla.index = range(1, len(tabla) + 1)

    fuerzas_t  = [f for f in FUERZAS_POR_ANIO[anio_global] if f in tabla.columns]
    num_cols_t = fuerzas_t + ["lista_nominal", "votos_validos", "votos_nulos", "total_votos"]
    pct_cols_t = ["participacion"] if "participacion" in tabla.columns else []

    def safe_fmt(v, pct=False):
        try:
            if pd.isna(v): return "—"
            return f"{float(v):.1f}%" if pct else f"{float(v):,.0f}"
        except Exception:
            return "—"

    fmt_dict = {c: (lambda v: safe_fmt(v, pct=False)) for c in num_cols_t}
    fmt_dict.update({c: (lambda v: safe_fmt(v, pct=True)) for c in pct_cols_t})

    st.dataframe(tabla.style.format(fmt_dict, na_rep="—"), use_container_width=True, height=600)

    csv = tabla.to_csv(index=True, index_label="#").encode("utf-8")
    st.download_button(
        label="⬇️ Descargar CSV",
        data=csv,
        file_name=f"resultados_gubernatura_{anio_global}.csv",
        mime="text/csv",
    )
