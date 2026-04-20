"""
Carga y normaliza los datos electorales de gubernatura del Estado de México
2005, 2011, 2017 y 2023.

Estructura de salida por año:
  - distrito: nombre del distrito
  - lista_nominal: lista nominal
  - fuerza_1..N: votos por fuerza/coalición
  - votos_validos, votos_nulos, total_votos, participacion, abstencion
"""

import pandas as pd
import numpy as np

# ── Mapeo de colores por fuerza política ──────────────────────────────────────
COLORES = {
    "PAN - Convergencia":                  "#003f8a",
    "Alianza por México":                  "#006847",
    "Unidos para Ganar":                   "#FFCC00",
    "PAN":                                 "#003f8a",
    "Unidos por Ti":                       "#006847",
    "Unidos Podemos Más":                  "#FFCC00",
    "Alianza PRI":                         "#006847",
    "MORENA":                              "#8B0000",
    "PRD":                                 "#FFCC00",
    "PT":                                  "#CC0000",
    "Candidato Independiente":             "#888888",
    "Fuerza y Corazón por el Edo. de Méx": "#003f8a",
    "Sigamos Haciendo Historia":           "#8B0000",
    "No Registrados":                      "#aaaaaa",
    "Votos Nulos":                         "#cccccc",
}

FUERZAS_POR_ANIO = {
    2005: ["PAN - Convergencia", "Alianza por México", "Unidos para Ganar"],
    2011: ["PAN", "Unidos por Ti", "Unidos Podemos Más"],
    2017: ["PAN", "Alianza PRI", "MORENA", "PRD", "PT", "Candidato Independiente"],
    2023: ["Fuerza y Corazón por el Edo. de Méx", "Sigamos Haciendo Historia"],
}


def _limpiar_distrito(nombre):
    if pd.isna(nombre):
        return None
    nombre = str(nombre).strip()
    # quitar número romano al inicio si viene como "I - TOLUCA"
    return nombre


def cargar_2005():
    df = pd.read_excel(
        "Datos de excel/computo_dttal_2005dg.xls",
        sheet_name=0,
        header=None,
    )
    datos = df.iloc[10:].copy()
    datos = datos[datos.iloc[:, 1].notna() & (datos.iloc[:, 1] != "")]
    # filtrar filas no numéricas en columna 0 (número de distrito) y notas al pie
    datos = datos[pd.to_numeric(datos.iloc[:, 0], errors="coerce").notna()]

    resultado = pd.DataFrame()
    nums = pd.to_numeric(datos.iloc[:, 0], errors="coerce").astype(int)
    nombres = datos.iloc[:, 1].apply(_limpiar_distrito)
    resultado["distrito"]              = nums.astype(str).str.zfill(2) + " - " + nombres.values
    resultado["lista_nominal"]         = pd.to_numeric(datos.iloc[:, 2], errors="coerce").values
    resultado["PAN - Convergencia"]    = pd.to_numeric(datos.iloc[:, 3], errors="coerce").values
    resultado["Alianza por México"]    = pd.to_numeric(datos.iloc[:, 5], errors="coerce").values
    resultado["Unidos para Ganar"]     = pd.to_numeric(datos.iloc[:, 7], errors="coerce").values
    resultado["No Registrados"]        = pd.to_numeric(datos.iloc[:, 9], errors="coerce").values
    resultado["votos_validos"]         = pd.to_numeric(datos.iloc[:, 11], errors="coerce").values
    resultado["votos_nulos"]           = pd.to_numeric(datos.iloc[:, 13], errors="coerce").values
    resultado["total_votos"]           = pd.to_numeric(datos.iloc[:, 15], errors="coerce").values
    resultado["participacion"]         = pd.to_numeric(datos.iloc[:, 16], errors="coerce").values
    resultado["anio"]                  = 2005
    resultado = resultado.dropna(subset=["distrito"]).reset_index(drop=True)
    # excluir notas al pie
    resultado = resultado[~resultado["distrito"].astype(str).str.upper().str.startswith("NOTA")]
    resultado["es_extranjero"] = False
    resultado["abstencion"] = 1 - resultado["participacion"]
    return resultado


def cargar_2011():
    df = pd.read_excel(
        "Datos de excel/Computo_FINAL_GOB_2011.xls",
        sheet_name=0,
        header=None,
    )
    # Los 45 distritos están exactamente en filas 7-51 (índice)
    # fila 6 = TOTAL ESTATAL, desde fila 52 = notas al pie y segundo bloque
    datos = df.iloc[7:52].copy()
    datos = datos[datos.iloc[:, 0].notna()]
    datos = datos[pd.to_numeric(datos.iloc[:, 1], errors="coerce").notna()]

    resultado = pd.DataFrame()
    nombres = datos.iloc[:, 0].apply(_limpiar_distrito)
    # agregar prefijo arábigo para ordenamiento correcto
    romanos = {
        "I":1,"II":2,"III":3,"IV":4,"V":5,"VI":6,"VII":7,"VIII":8,"IX":9,"X":10,
        "XI":11,"XII":12,"XIII":13,"XIV":14,"XV":15,"XVI":16,"XVII":17,"XVIII":18,
        "XIX":19,"XX":20,"XXI":21,"XXII":22,"XXIII":23,"XXIV":24,"XXV":25,
        "XXVI":26,"XXVII":27,"XXVIII":28,"XXIX":29,"XXX":30,"XXXI":31,"XXXII":32,
        "XXXIII":33,"XXXIV":34,"XXXV":35,"XXXVI":36,"XXXVII":37,"XXXVIII":38,
        "XXXIX":39,"XL":40,"XLI":41,"XLII":42,"XLIII":43,"XLIV":44,"XLV":45,
    }
    def prefijo_romano(nombre):
        if not isinstance(nombre, str):
            return nombre
        primera = nombre.strip().split()[0].upper()
        num = romanos.get(primera)
        if num:
            return f"{num:02d} - {nombre}"
        return nombre
    resultado["distrito"]          = [prefijo_romano(n) for n in nombres.values]
    resultado["lista_nominal"]     = pd.to_numeric(datos.iloc[:, 1], errors="coerce").values
    resultado["PAN"]               = pd.to_numeric(datos.iloc[:, 6], errors="coerce").values
    resultado["Unidos por Ti"]     = pd.to_numeric(datos.iloc[:, 8], errors="coerce").values
    resultado["Unidos Podemos Más"]= pd.to_numeric(datos.iloc[:, 10], errors="coerce").values
    resultado["No Registrados"]    = pd.to_numeric(datos.iloc[:, 12], errors="coerce").values
    resultado["votos_nulos"]       = pd.to_numeric(datos.iloc[:, 14], errors="coerce").values
    resultado["total_votos"]       = pd.to_numeric(datos.iloc[:, 18], errors="coerce").values
    resultado["participacion"]     = pd.to_numeric(datos.iloc[:, 19], errors="coerce").values
    resultado["anio"]              = 2011
    resultado["es_extranjero"]     = False
    resultado = resultado.dropna(subset=["distrito"]).reset_index(drop=True)
    resultado["votos_validos"]     = resultado["total_votos"] - resultado["votos_nulos"]
    resultado["abstencion"]        = 1 - resultado["participacion"]
    return resultado


def cargar_2017():
    df = pd.read_excel(
        "Datos de excel/Res_Definitivos_Gobernador_2017_por_DistritoLocal.xlsx",
        sheet_name=0,
    )
    # Coalición PRI = PRI + PVEM + NVA_ALIANZA + ES + todas sus combinaciones
    cols_alianza_pri = [
        "PRI", "PVEM", "NVA_ALIANZA", "ES",
        "PRI_PVEM_NVA_ALIANZA_ES", "PRI_PVEM_NVA_ALIANZA", "PRI_PVEM_ES",
        "PRI_NVA_ALIANZA_ES", "PRI_PVEM", "PRI_NVA_ALIANZA", "PRI_ES",
        "PVEM_NVA_ALIANZA_ES", "PVEM_NVA_ALIANZA", "PVEM_ES", "NVA_ALIANZA_ES",
    ]

    resultado = pd.DataFrame()
    resultado["distrito"]               = df["ID_DISTRITO"].astype(str).str.zfill(2) + " - " + df["CABECERA_DISTRITAL"].apply(_limpiar_distrito)
    resultado["lista_nominal"]          = pd.to_numeric(df["LISTA_NOMINAL"], errors="coerce")
    resultado["PAN"]                    = pd.to_numeric(df["PAN"], errors="coerce")
    resultado["Alianza PRI"]            = df[cols_alianza_pri].apply(pd.to_numeric, errors="coerce").sum(axis=1)
    resultado["MORENA"]                 = pd.to_numeric(df["MORENA"], errors="coerce")
    resultado["PRD"]                    = pd.to_numeric(df["PRD"], errors="coerce")
    resultado["PT"]                     = pd.to_numeric(df["PT"], errors="coerce")
    resultado["Candidato Independiente"]= pd.to_numeric(df["CAND_IND1"], errors="coerce")
    resultado["No Registrados"]         = pd.to_numeric(df["NUM_VOTOS_CAN_NREG"], errors="coerce")
    resultado["votos_validos"]          = pd.to_numeric(df["NUM_VOTOS_VALIDOS"], errors="coerce")
    resultado["votos_nulos"]            = pd.to_numeric(df["NUM_VOTOS_NULOS"], errors="coerce")
    resultado["total_votos"]            = pd.to_numeric(df["TOTAL_VOTOS"], errors="coerce")
    resultado["participacion"]          = pd.to_numeric(df["PARTICIPACION"], errors="coerce") / 100
    resultado["anio"]                   = 2017
    resultado = resultado.dropna(subset=["distrito"]).reset_index(drop=True)
    # excluir voto en el extranjero de las vistas por distrito pero mantener en totales
    # marcamos la fila para poder filtrarla en gráficas
    resultado["es_extranjero"] = resultado["distrito"].str.upper().str.contains("EXTRANJERO|VMRE")
    resultado["abstencion"]             = 1 - resultado["participacion"]
    return resultado


def cargar_2023():
    df = pd.read_excel(
        "Datos de excel/RESULTADOS DEFINITIVOS GUBERNATURA 2023 POR DISTRITO LOCAL.xlsx",
        sheet_name=0,
        header=5,
    )
    # Excluir filas especiales (voto anticipado, extranjero, prisión preventiva)
    df = df[df["ID_DISTRITO_LOCAL"] > 0].copy()

    cols_fuerza_corazon = [
        "PAN", "PRI", "PRD", "NAEM",
        "PAN_PRI_PRD_NAEM", "PAN_PRI_PRD", "PAN_PRI_NAEM", "PAN_PRD_NAEM",
        "PRI_PRD_NAEM", "PAN_PRI", "PAN_PRD", "PAN_NAEM",
        "PRI_PRD", "PRI_NAEM", "PRD_NAEM",
    ]

    resultado = pd.DataFrame()
    resultado["distrito"]                          = df["ID_DISTRITO_LOCAL"].astype(str).str.zfill(2) + " - " + df["CABECERA_DISTRITAL_LOCAL"].apply(_limpiar_distrito)
    resultado["lista_nominal"]                     = pd.to_numeric(df["LISTA_NOMINAL"], errors="coerce")
    resultado["Fuerza y Corazón por el Edo. de Méx"] = df[cols_fuerza_corazon].apply(pd.to_numeric, errors="coerce").sum(axis=1)
    resultado["Sigamos Haciendo Historia"]         = pd.to_numeric(df["PVEM_PT_MORENA"], errors="coerce")
    resultado["No Registrados"]                    = pd.to_numeric(df["NUM_VOTOS_CAN_NREG"], errors="coerce")
    resultado["votos_validos"]                     = pd.to_numeric(df["NUM_VOTOS_VALIDOS"], errors="coerce")
    resultado["votos_nulos"]                       = pd.to_numeric(df["NUM_VOTOS_NULOS"], errors="coerce")
    resultado["total_votos"]                       = pd.to_numeric(df["TOTAL_VOTOS"], errors="coerce")
    resultado["participacion"]                     = resultado["total_votos"] / resultado["lista_nominal"]
    resultado["anio"]                              = 2023
    resultado["es_extranjero"]                     = False
    resultado = resultado.dropna(subset=["distrito"]).reset_index(drop=True)
    resultado["abstencion"]                        = 1 - resultado["participacion"]
    return resultado


def cargar_todos():
    """Retorna dict {anio: DataFrame} con todos los años normalizados."""
    return {
        2005: cargar_2005(),
        2011: cargar_2011(),
        2017: cargar_2017(),
        2023: cargar_2023(),
    }


def totales_estatales(datos: dict) -> pd.DataFrame:
    """Genera un DataFrame con totales estatales por año para comparativos."""
    filas = []
    for anio, df in datos.items():
        fuerzas = FUERZAS_POR_ANIO[anio]
        fila = {"anio": anio}
        for f in fuerzas:
            if f in df.columns:
                fila[f] = df[f].sum()
        fila["votos_validos"]  = df["votos_validos"].sum()
        fila["votos_nulos"]    = df["votos_nulos"].sum()
        fila["total_votos"]    = df["total_votos"].sum()
        fila["lista_nominal"]  = df["lista_nominal"].sum()
        fila["participacion"]  = fila["total_votos"] / fila["lista_nominal"]
        fila["abstencion"]     = 1 - fila["participacion"]
        filas.append(fila)
    return pd.DataFrame(filas).set_index("anio")
