"""
Carga y prepara los GeoDataFrames de distritos locales por año electoral.
Convierte a WGS84 (EPSG:4326) para uso con Plotly/Mapbox.
"""

import geopandas as gpd
import pandas as pd
import json

SHP = {
    2005: "SHP_DL_SECC_2005_2023/SHP_2005/dttoloc.shp",
    2011: "SHP_DL_SECC_2005_2023/SHP_2011/dttoloc.shp",
    2017: "SHP_DL_SECC_2005_2023/SHP_2017/DISTRITO_LOCAL.shp",
    2023: "SHP_DL_SECC_2005_2023/SHP_2023/DISTRITO_LOCAL1.shp",
}


def cargar_geo(anio: int) -> gpd.GeoDataFrame:
    """Carga el shapefile distrital del año, normaliza a WGS84 y agrega columna 'num_distrito'."""
    gdf = gpd.read_file(SHP[anio])
    gdf = gdf.to_crs(epsg=4326)

    if anio in (2005, 2011):
        gdf["num_distrito"] = gdf["DL"].astype(int)
    else:
        gdf["num_distrito"] = gdf["DISTRITO_L"].astype(int)

    return gdf[["num_distrito", "geometry"]]


def geo_a_geojson(gdf: gpd.GeoDataFrame) -> dict:
    """Convierte GeoDataFrame a dict GeoJSON con id = num_distrito."""
    gdf2 = gdf.copy()
    gdf2["id"] = gdf2["num_distrito"].astype(str)
    return json.loads(gdf2.to_json())


def _romano_a_num(texto: str) -> int | None:
    """Extrae el número de distrito de nombres con numeral romano (2005/2011)."""
    romanos = {
        "I": 1, "II": 2, "III": 3, "IV": 4, "V": 5,
        "VI": 6, "VII": 7, "VIII": 8, "IX": 9, "X": 10,
        "XI": 11, "XII": 12, "XIII": 13, "XIV": 14, "XV": 15,
        "XVI": 16, "XVII": 17, "XVIII": 18, "XIX": 19, "XX": 20,
        "XXI": 21, "XXII": 22, "XXIII": 23, "XXIV": 24, "XXV": 25,
        "XXVI": 26, "XXVII": 27, "XXVIII": 28, "XXIX": 29, "XXX": 30,
        "XXXI": 31, "XXXII": 32, "XXXIII": 33, "XXXIV": 34, "XXXV": 35,
        "XXXVI": 36, "XXXVII": 37, "XXXVIII": 38, "XXXIX": 39, "XL": 40,
        "XLI": 41, "XLII": 42, "XLIII": 43, "XLIV": 44, "XLV": 45,
    }
    if not isinstance(texto, str):
        return None
    # formato "01 - I - TOLUCA" → extraer parte romana
    partes = texto.strip().split(" - ")
    for p in partes:
        p = p.strip().split()[0].upper()
        if p in romanos:
            return romanos[p]
    # formato "I - TOLUCA (PARTE) 1" → primera parte
    primera = texto.strip().split()[0].upper()
    return romanos.get(primera)


def join_electoral_geo(df_electoral: pd.DataFrame, gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Une datos electorales con geometría usando el número de distrito.
    Soporta formato '01 - NOMBRE' (2017/2023) y 'I - NOMBRE' (2005/2011).
    """
    df = df_electoral.copy()

    # intentar extraer número arábigo del prefijo
    num_arabigo = df["distrito"].str.extract(r"^(\d+)")[0]

    if num_arabigo.notna().all():
        df["num_distrito"] = num_arabigo.astype(int)
    else:
        # usar conversión romano→arábigo
        df["num_distrito"] = df["distrito"].apply(_romano_a_num)

    df = df[df["num_distrito"].notna()]
    df["num_distrito"] = df["num_distrito"].astype(int)
    merged = gdf.merge(df, on="num_distrito", how="left")
    return merged
