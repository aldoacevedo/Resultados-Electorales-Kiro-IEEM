"""
Exportación a Excel con openpyxl
"""
from io import BytesIO
import pandas as pd


def exportar_excel(hojas: dict[str, pd.DataFrame]) -> bytes:
    """
    Recibe un dict {nombre_hoja: DataFrame} y devuelve bytes de un .xlsx.
    """
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        for nombre, df in hojas.items():
            df.to_excel(writer, sheet_name=nombre[:31], index=False)
    buf.seek(0)
    return buf.read()
