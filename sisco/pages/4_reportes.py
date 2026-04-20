"""
Página: Reportes
"""
import streamlit as st
import pandas as pd
from datetime import date
from io import BytesIO
from sisco.database.db import SessionLocal
from sisco.data.reportes import (
    resumen_sesiones, resumen_asistencias, resumen_votaciones, resumen_solicitudes
)
from sisco.data.catalogo import listar_integrantes
from sisco.exports.excel_export import exportar_excel
from sisco.exports.word_export import exportar_sesion_word
from sisco.data.sesiones import obtener_sesion
from sisco.utils.styles import inject, header

st.set_page_config(page_title="Reportes — SISCO", layout="wide")
inject(st)
st.markdown(header("Reportes", "Word y Excel descargables"), unsafe_allow_html=True)

db = SessionLocal()

anio_opts = list(range(date.today().year, 2019, -1))
integrantes = listar_integrantes(db, solo_activos=False)
int_opts = {"— Todos —": None} | {i.nombre: i.id for i in integrantes}

tab_sesion, tab_asist, tab_vot, tab_sol = st.tabs([
    "📄 Reporte por sesión", "👥 Asistencias", "🗳️ Votaciones", "📨 Solicitudes"
])

# ── Reporte por sesión (Word) ─────────────────────────────────────────────────
with tab_sesion:
    st.subheader("Reporte completo de sesión")
    anio_s   = st.selectbox("Año", anio_opts, key="anio_s")
    sesiones = resumen_sesiones(db, anio=anio_s)["sesiones"]

    if sesiones:
        opts_s = {f"#{s.numero_sesion} — {s.naturaleza.value} {s.tipo_sesion} ({s.fecha})": s.id for s in sesiones}
        sel_s  = st.selectbox("Sesión", list(opts_s.keys()))
        if st.button("⬇️ Descargar Word"):
            sesion = obtener_sesion(db, opts_s[sel_s])
            buf = exportar_sesion_word(sesion)
            st.download_button(
                "Descargar .docx",
                data=buf,
                file_name=f"sesion_{sesion.numero_sesion}_{sesion.fecha}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
    else:
        st.info("No hay sesiones para este año.")

# ── Asistencias ───────────────────────────────────────────────────────────────
with tab_asist:
    st.subheader("Reporte de asistencias")
    col1, col2 = st.columns(2)
    with col1:
        anio_a = st.selectbox("Año", anio_opts, key="anio_a")
    with col2:
        int_a  = st.selectbox("Integrante", list(int_opts.keys()), key="int_a")

    res = resumen_asistencias(db, anio=anio_a, integrante_id=int_opts[int_a])

    m1, m2, m3 = st.columns(3)
    m1.metric("Total registros", res["total"])
    m2.metric("Presentes", f"{res['presentes']} ({res['pct_asistencia']:.1f}%)")
    m3.metric("Faltas", res["faltas"])

    if res["por_modalidad"]:
        st.bar_chart(res["por_modalidad"])

    if res["detalle"]:
        df_a = pd.DataFrame([
            {
                "Sesión": a.sesion.numero_sesion,
                "Fecha": a.sesion.fecha,
                "Integrante": a.integrante.nombre,
                "Cargo": a.integrante.cargo.value,
                "Presente": "✅" if a.presente else "❌",
                "Modalidad": a.modalidad.value if a.modalidad else "—",
                "Justificación": a.justificacion or "—",
            }
            for a in res["detalle"]
        ])
        st.dataframe(df_a, use_container_width=True, hide_index=True)

        buf = exportar_excel({"Asistencias": df_a})
        st.download_button("⬇️ Descargar Excel", data=buf, file_name=f"asistencias_{anio_a}.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# ── Votaciones ────────────────────────────────────────────────────────────────
with tab_vot:
    st.subheader("Reporte de votaciones")
    anio_v = st.selectbox("Año", anio_opts, key="anio_v")
    res_v  = resumen_votaciones(db, anio=anio_v)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total votaciones", res_v["total"])
    m2.metric("Unanimidad", res_v["por_resultado"].get("Unanimidad", 0))
    m3.metric("Mayoría", res_v["por_resultado"].get("Mayoría", 0))
    m4.metric("Desechados", res_v["por_resultado"].get("Desechado", 0))

    if res_v["detalle"]:
        df_v = pd.DataFrame([
            {
                "Sesión": v.punto.sesion.numero_sesion,
                "Fecha": v.punto.sesion.fecha,
                "Punto": v.punto.descripcion or v.punto.tipo.value,
                "Resultado": v.resultado.value,
                "Hora aprobación": v.hora_aprobacion or "—",
                "Observaciones": v.observaciones or "—",
            }
            for v in res_v["detalle"]
        ])
        st.dataframe(df_v, use_container_width=True, hide_index=True)

        buf = exportar_excel({"Votaciones": df_v})
        st.download_button("⬇️ Descargar Excel", data=buf, file_name=f"votaciones_{anio_v}.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# ── Solicitudes ───────────────────────────────────────────────────────────────
with tab_sol:
    st.subheader("Reporte de solicitudes")
    col1, col2 = st.columns(2)
    with col1:
        anio_sol = st.selectbox("Año", anio_opts, key="anio_sol")
    with col2:
        int_sol  = st.selectbox("Integrante", list(int_opts.keys()), key="int_sol")

    solicitudes = resumen_solicitudes(db, anio=anio_sol, integrante_id=int_opts[int_sol])

    if solicitudes:
        df_sol = pd.DataFrame([
            {
                "Sesión": s.punto.sesion.numero_sesion,
                "Fecha": s.punto.sesion.fecha,
                "Integrante": s.integrante.nombre,
                "Descripción": s.descripcion,
                "Estatus": s.estatus or "—",
                "Seguimientos": len(s.seguimientos),
            }
            for s in solicitudes
        ])
        st.dataframe(df_sol, use_container_width=True, hide_index=True)

        buf = exportar_excel({"Solicitudes": df_sol})
        st.download_button("⬇️ Descargar Excel", data=buf, file_name=f"solicitudes_{anio_sol}.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:
        st.info("No hay solicitudes para los filtros seleccionados.")

db.close()
