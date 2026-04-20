import pandas as pd
from data.loader import cargar_2005, cargar_2011, cargar_2017, cargar_2023

def chk(label, raw, loader):
    diff = raw - loader
    estado = "OK" if abs(diff) < 1 else "*** DIFERENCIA ***"
    print(f"  {label:<30} raw: {raw:>12,.0f}  loader: {loader:>12,.0f}  diff: {diff:>10,.0f}  {estado}")

# ── 2023 ──────────────────────────────────────────────────────────────────────
print("=== 2023 ===")
df23_raw = pd.read_excel("Datos de excel/RESULTADOS DEFINITIVOS GUBERNATURA 2023 POR DISTRITO LOCAL.xlsx", header=5)
df23_raw = df23_raw[df23_raw["ID_DISTRITO_LOCAL"] > 0]
df23 = cargar_2023()

cols_fc = ["PAN","PRI","PRD","NAEM","PAN_PRI_PRD_NAEM","PAN_PRI_PRD","PAN_PRI_NAEM",
           "PAN_PRD_NAEM","PRI_PRD_NAEM","PAN_PRI","PAN_PRD","PAN_NAEM","PRI_PRD","PRI_NAEM","PRD_NAEM"]
chk("Fuerza y Corazon", df23_raw[cols_fc].apply(pd.to_numeric, errors="coerce").sum().sum(), df23["Fuerza y Corazón por el Edo. de Méx"].sum())
chk("Sigamos Haciendo Historia", pd.to_numeric(df23_raw["PVEM_PT_MORENA"], errors="coerce").sum(), df23["Sigamos Haciendo Historia"].sum())
chk("Votos validos", pd.to_numeric(df23_raw["NUM_VOTOS_VALIDOS"], errors="coerce").sum(), df23["votos_validos"].sum())
chk("Votos nulos", pd.to_numeric(df23_raw["NUM_VOTOS_NULOS"], errors="coerce").sum(), df23["votos_nulos"].sum())
chk("Total votos", pd.to_numeric(df23_raw["TOTAL_VOTOS"], errors="coerce").sum(), df23["total_votos"].sum())

# ── 2017 ──────────────────────────────────────────────────────────────────────
print("\n=== 2017 ===")
df17_raw = pd.read_excel("Datos de excel/Res_Definitivos_Gobernador_2017_por_DistritoLocal.xlsx")
df17 = cargar_2017()

cols_alianza = ["PRI","PVEM","NVA_ALIANZA","ES","PRI_PVEM_NVA_ALIANZA_ES","PRI_PVEM_NVA_ALIANZA",
                "PRI_PVEM_ES","PRI_NVA_ALIANZA_ES","PRI_PVEM","PRI_NVA_ALIANZA","PRI_ES",
                "PVEM_NVA_ALIANZA_ES","PVEM_NVA_ALIANZA","PVEM_ES","NVA_ALIANZA_ES"]
chk("PAN", pd.to_numeric(df17_raw["PAN"], errors="coerce").sum(), df17["PAN"].sum())
chk("Alianza PRI", df17_raw[cols_alianza].apply(pd.to_numeric, errors="coerce").sum().sum(), df17["Alianza PRI"].sum())
chk("MORENA", pd.to_numeric(df17_raw["MORENA"], errors="coerce").sum(), df17["MORENA"].sum())
chk("PRD", pd.to_numeric(df17_raw["PRD"], errors="coerce").sum(), df17["PRD"].sum())
chk("PT", pd.to_numeric(df17_raw["PT"], errors="coerce").sum(), df17["PT"].sum())
chk("Candidato Independiente", pd.to_numeric(df17_raw["CAND_IND1"], errors="coerce").sum(), df17["Candidato Independiente"].sum())
chk("Votos validos", pd.to_numeric(df17_raw["NUM_VOTOS_VALIDOS"], errors="coerce").sum(), df17["votos_validos"].sum())
chk("Votos nulos", pd.to_numeric(df17_raw["NUM_VOTOS_NULOS"], errors="coerce").sum(), df17["votos_nulos"].sum())
chk("Total votos", pd.to_numeric(df17_raw["TOTAL_VOTOS"], errors="coerce").sum(), df17["total_votos"].sum())

# ── 2011 ──────────────────────────────────────────────────────────────────────
print("\n=== 2011 ===")
df11_raw = pd.read_excel("Datos de excel/Computo_FINAL_GOB_2011.xls", header=None)
fila = df11_raw.iloc[6]  # fila TOTAL ESTATAL
df11 = cargar_2011()

chk("PAN", pd.to_numeric(fila[6], errors="coerce"), df11["PAN"].sum())
chk("Unidos por Ti", pd.to_numeric(fila[8], errors="coerce"), df11["Unidos por Ti"].sum())
chk("Unidos Podemos Mas", pd.to_numeric(fila[10], errors="coerce"), df11["Unidos Podemos Más"].sum())
chk("Total votos", pd.to_numeric(fila[18], errors="coerce"), df11["total_votos"].sum())

# ── 2005 ──────────────────────────────────────────────────────────────────────
print("\n=== 2005 ===")
df05_raw = pd.read_excel("Datos de excel/computo_dttal_2005dg.xls", header=None)
fila05 = df05_raw.iloc[8]  # fila ESTATAL
df05 = cargar_2005()

chk("PAN - Convergencia", pd.to_numeric(fila05[3], errors="coerce"), df05["PAN - Convergencia"].sum())
chk("Alianza por Mexico", pd.to_numeric(fila05[5], errors="coerce"), df05["Alianza por México"].sum())
chk("Unidos para Ganar", pd.to_numeric(fila05[7], errors="coerce"), df05["Unidos para Ganar"].sum())
chk("Votos validos", pd.to_numeric(fila05[11], errors="coerce"), df05["votos_validos"].sum())
chk("Total votos", pd.to_numeric(fila05[15], errors="coerce"), df05["total_votos"].sum())
