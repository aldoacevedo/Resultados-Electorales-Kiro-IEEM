"""Funciones de visualización con Plotly para el sistema electoral."""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import json
from data.loader import COLORES, FUERZAS_POR_ANIO


def _color(fuerza):
    return COLORES.get(fuerza, "#999999")


# ── 1. Barras: resultados por fuerza (un año) ─────────────────────────────────
def grafico_barras_anio(df: pd.DataFrame, anio: int, porcentual: bool = False):
    fuerzas = [f for f in FUERZAS_POR_ANIO[anio] if f in df.columns]
    totales = {f: df[f].sum() for f in fuerzas}
    total_validos = sum(totales.values())

    if porcentual:
        valores = [totales[f] / total_validos * 100 for f in fuerzas]
        ytitle = "% de votos válidos"
        textfmt = [f"{v:.1f}%" for v in valores]
    else:
        valores = [totales[f] for f in fuerzas]
        ytitle = "Votos"
        textfmt = [f"{v:,.0f}" for v in valores]

    fig = go.Figure(go.Bar(
        x=fuerzas,
        y=valores,
        text=textfmt,
        textposition="outside",
        marker_color=[_color(f) for f in fuerzas],
        width=0.5,
    ))
    y_max = max(valores) * 1.15 if valores else 1
    fig.update_layout(
        title=f"Resultados Gubernatura {anio} — Estado de México",
        xaxis_title="Fuerza política",
        yaxis_title=ytitle,
        plot_bgcolor="white",
        yaxis=dict(gridcolor="#eeeeee", range=[0, y_max]),
        bargap=0.3,
        height=450,
        margin=dict(t=60, b=60, l=60, r=20),
    )
    return fig


# ── 2. Barras comparativas entre años ─────────────────────────────────────────
def grafico_comparativo_fuerzas(totales_df: pd.DataFrame, porcentual: bool = False):
    """Compara participación de cada fuerza a lo largo de los 4 años."""
    # Construir tabla larga
    filas = []
    for anio in totales_df.index:
        fuerzas = FUERZAS_POR_ANIO[anio]
        total_validos = totales_df.loc[anio, "votos_validos"]
        for f in fuerzas:
            if f in totales_df.columns:
                votos = totales_df.loc[anio, f]
                filas.append({
                    "anio": str(anio),
                    "fuerza": f,
                    "votos": votos,
                    "pct": votos / total_validos * 100 if total_validos else 0,
                })
    df_long = pd.DataFrame(filas)
    y_col = "pct" if porcentual else "votos"
    ytitle = "% de votos válidos" if porcentual else "Votos"

    fig = px.bar(
        df_long, x="anio", y=y_col, color="fuerza",
        barmode="group",
        color_discrete_map={f: _color(f) for f in df_long["fuerza"].unique()},
        text=df_long[y_col].apply(lambda v: f"{v:.1f}%" if porcentual else f"{v:,.0f}"),
        labels={"anio": "Año", y_col: ytitle, "fuerza": "Fuerza política"},
        title="Comparativo de fuerzas políticas 2005–2023",
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(
        plot_bgcolor="white",
        yaxis=dict(gridcolor="#eeeeee"),
        height=450,
        bargap=0.2,
        bargroupgap=0.1,
        margin=dict(t=60, b=60, l=60, r=20),
    )
    return fig


# ── 3. Pie: distribución de votos ─────────────────────────────────────────────
def grafico_pie_anio(df: pd.DataFrame, anio: int):
    fuerzas = [f for f in FUERZAS_POR_ANIO[anio] if f in df.columns]
    totales = {f: df[f].sum() for f in fuerzas}
    # agregar nulos
    totales["Votos Nulos"] = df["votos_nulos"].sum()

    fig = go.Figure(go.Pie(
        labels=list(totales.keys()),
        values=list(totales.values()),
        marker_colors=[_color(f) for f in totales.keys()],
        hole=0.35,
        textinfo="label+percent",
    ))
    fig.update_layout(title=f"Distribución de votos {anio}")
    return fig


# ── 4. Participación y abstención por año ─────────────────────────────────────
def grafico_participacion(totales_df: pd.DataFrame):
    anios = [str(a) for a in totales_df.index]
    participacion = totales_df["participacion"] * 100
    abstencion = totales_df["abstencion"] * 100

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Participación", x=anios, y=participacion,
        marker_color="#2196F3",
        text=[f"{v:.1f}%" for v in participacion], textposition="inside",
    ))
    fig.add_trace(go.Bar(
        name="Abstención", x=anios, y=abstencion,
        marker_color="#FF7043",
        text=[f"{v:.1f}%" for v in abstencion], textposition="inside",
    ))
    fig.update_layout(
        barmode="stack",
        title="Participación y abstención electoral 2005–2023",
        xaxis_title="Año", yaxis_title="%",
        plot_bgcolor="white",
        yaxis=dict(gridcolor="#eeeeee", range=[0, 100]),
        height=400,
        bargap=0.4,
        margin=dict(t=60, b=60, l=60, r=20),
    )
    return fig


# ── 5. Línea: evolución de una fuerza por año ─────────────────────────────────
def grafico_evolucion_fuerza(totales_df: pd.DataFrame, fuerza: str, porcentual: bool = True):
    anios, valores = [], []
    for anio in totales_df.index:
        if fuerza in totales_df.columns and not pd.isna(totales_df.loc[anio, fuerza]):
            anios.append(anio)
            v = totales_df.loc[anio, fuerza]
            if porcentual:
                v = v / totales_df.loc[anio, "votos_validos"] * 100
            valores.append(v)

    fig = go.Figure(go.Scatter(
        x=anios, y=valores, mode="lines+markers+text",
        text=[f"{v:.1f}%" if porcentual else f"{v:,.0f}" for v in valores],
        textposition="top center",
        line=dict(color=_color(fuerza), width=3),
        marker=dict(size=10),
        name=fuerza,
    ))
    fig.update_layout(
        title=f"Evolución de {fuerza}",
        xaxis_title="Año",
        yaxis_title="% votos válidos" if porcentual else "Votos",
        plot_bgcolor="white",
        yaxis=dict(gridcolor="#eeeeee"),
        height=400,
        margin=dict(t=60, b=60, l=60, r=20),
    )
    return fig


# ── 6. Barras horizontales por distrito ───────────────────────────────────────
def grafico_distritos(df: pd.DataFrame, anio: int, fuerza: str, porcentual: bool = True):
    if fuerza not in df.columns:
        return go.Figure()
    df2 = df.copy()
    # excluir voto extranjero de vistas por distrito
    if "es_extranjero" in df2.columns:
        df2 = df2[~df2["es_extranjero"]]
    # limpiar distritos que son notas al pie o no tienen datos válidos
    df2 = df2[df2["distrito"].notna()]
    df2 = df2[~df2["distrito"].astype(str).str.upper().str.startswith("NOTA")]
    if porcentual:
        df2["valor"] = df2[fuerza] / df2["votos_validos"] * 100
        xtitle = f"% votos válidos — {fuerza}"
    else:
        df2["valor"] = df2[fuerza]
        xtitle = f"Votos — {fuerza}"

    # eliminar filas con valor NaN o infinito
    df2 = df2[df2["valor"].notna() & np.isfinite(df2["valor"])]
    # ordenar por número de distrito (el prefijo numérico del nombre)
    df2["_num"] = df2["distrito"].str.extract(r"^(\d+)").astype(float)
    df2 = df2.sort_values("_num", ascending=True).drop(columns="_num")
    fig = go.Figure(go.Bar(
        x=df2["valor"], y=df2["distrito"],
        orientation="h",
        marker_color=_color(fuerza),
        text=df2["valor"].apply(lambda v: f"{v:.1f}%" if porcentual else f"{v:,.0f}"),
        textposition="outside",
    ))
    fig.update_layout(
        title=f"{fuerza} por distrito — {anio}",
        xaxis_title=xtitle,
        yaxis_title="Distrito",
        height=max(500, len(df2) * 26),
        plot_bgcolor="white",
        xaxis=dict(gridcolor="#eeeeee"),
        margin=dict(t=60, b=40, l=200, r=80),
    )
    return fig


# ── 7. Mapa coroplético por distrito ──────────────────────────────────────────
def grafico_mapa_shp(gdf_merged, anio: int, fuerza: str, porcentual: bool = True):
    """Mapa coroplético usando GeoDataFrame ya unido con datos electorales."""
    import plotly.express as px

    if fuerza not in gdf_merged.columns:
        return go.Figure()

    gdf2 = gdf_merged.copy()
    if porcentual:
        gdf2["valor"] = gdf2[fuerza] / gdf2["votos_validos"] * 100
        zlabel = f"% votos válidos"
    else:
        gdf2["valor"] = gdf2[fuerza]
        zlabel = "Votos"

    gdf2 = gdf2[gdf2["valor"].notna()]
    geojson = json.loads(gdf2[["num_distrito", "geometry"]].to_json())

    fig = px.choropleth_mapbox(
        gdf2,
        geojson=geojson,
        locations="num_distrito",
        featureidkey="properties.num_distrito",
        color="valor",
        color_continuous_scale="Blues",
        mapbox_style="carto-positron",
        zoom=7,
        center={"lat": 19.35, "lon": -99.65},
        opacity=0.75,
        labels={"valor": zlabel, "distrito": "Distrito"},
        hover_data={"distrito": True, "valor": ":.1f", "num_distrito": False},
        title=f"{fuerza} por distrito — {anio}",
    )
    fig.update_layout(
        margin={"r": 0, "t": 40, "l": 0, "b": 0},
        coloraxis_colorbar=dict(title=zlabel),
    )
    return fig


# ── 8. Tabla resumen por distrito ─────────────────────────────────────────────
def tabla_distritos(df: pd.DataFrame, anio: int, porcentual: bool = False) -> pd.DataFrame:
    fuerzas = [f for f in FUERZAS_POR_ANIO[anio] if f in df.columns]
    # excluir voto extranjero
    df = df[~df.get("es_extranjero", pd.Series(False, index=df.index))].copy() if "es_extranjero" in df.columns else df.copy()
    cols = ["distrito", "lista_nominal"] + fuerzas + ["votos_validos", "votos_nulos", "total_votos", "participacion"]
    cols = [c for c in cols if c in df.columns]
    tabla = df[cols].copy()
    # Reemplazar inf antes de convertir
    tabla = tabla.replace([float("inf"), float("-inf")], float("nan"))
    if porcentual:
        for f in fuerzas:
            tabla[f] = (tabla[f] / tabla["votos_validos"] * 100).round(2)
        tabla["participacion"] = (tabla["participacion"] * 100).round(2)
    else:
        for f in fuerzas:
            tabla[f] = pd.to_numeric(tabla[f], errors="coerce").fillna(0).astype(int)
        tabla["participacion"] = (tabla["participacion"] * 100).round(2)
    return tabla.reset_index(drop=True)
