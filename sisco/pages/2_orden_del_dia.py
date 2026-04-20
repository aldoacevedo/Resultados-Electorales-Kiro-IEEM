"""
Página: Registro del Orden del Día
"""
import streamlit as st
from datetime import date
from sisco.database.db import SessionLocal
from sisco.database.models import NaturalezaEnum, ModalidadEnum, TipoPuntoEnum
from sisco.data.sesiones import (
    listar_sesiones, crear_sesion, agregar_punto, omitir_punto, obtener_sesion
)
from sisco.utils.helpers import siguiente_numero_sesion
from sisco.utils.styles import inject, header

st.set_page_config(page_title="Orden del Día — SISCO", layout="wide")
inject(st)
st.markdown(header("Orden del Día", "Registro previo a la sesión"), unsafe_allow_html=True)

db = SessionLocal()

tab_nueva, tab_ver = st.tabs(["Nueva sesión", "Sesiones registradas"])

# ── Nueva sesión ──────────────────────────────────────────────────────────────
with tab_nueva:
    st.subheader("Registrar nueva sesión")

    col1, col2 = st.columns(2)
    with col1:
        naturaleza  = st.selectbox("Naturaleza", [n.value for n in NaturalezaEnum])
        tipo_sesion = st.text_input("Tipo de sesión", placeholder="Ej. Extraordinaria, Especial…")
        fecha       = st.date_input("Fecha", value=date.today())
    with col2:
        modalidad = st.selectbox("Modalidad", [m.value for m in ModalidadEnum])
        if tipo_sesion and fecha:
            num_preview = siguiente_numero_sesion(
                db, fecha.year, NaturalezaEnum(naturaleza), tipo_sesion
            )
            st.metric("No. de sesión (automático)", num_preview)

    st.markdown("---")
    st.markdown("**Puntos del orden del día**")

    # Puntos opcionales
    col_a, col_b = st.columns(2)
    with col_a:
        incluir_actas = st.checkbox("Aprobación de actas", value=True)
        actas_desc    = st.text_area("Actas a aprobar (una por línea)", height=80, disabled=not incluir_actas)
    with col_b:
        incluir_informes = st.checkbox("Informes / Presentaciones", value=True)
        informes_desc    = st.text_area("Informes (uno por línea)", height=80, disabled=not incluir_informes)

    st.markdown("**Acuerdos / Resoluciones**")
    num_acuerdos = st.number_input("¿Cuántos acuerdos?", min_value=0, max_value=30, step=1, value=1)
    acuerdos = []
    for i in range(int(num_acuerdos)):
        acuerdos.append(st.text_input(f"Descripción acuerdo {i+1}", key=f"acuerdo_{i}"))

    if st.button("✅ Crear sesión", type="primary"):
        if not tipo_sesion:
            st.warning("Ingresa el tipo de sesión.")
        else:
            sesion = crear_sesion(
                db,
                NaturalezaEnum(naturaleza),
                tipo_sesion,
                fecha,
                ModalidadEnum(modalidad),
            )
            orden_actual = 3

            if incluir_actas:
                for linea in actas_desc.strip().splitlines():
                    if linea.strip():
                        agregar_punto(db, sesion.id, TipoPuntoEnum.acta, linea.strip(), orden_actual)
                        orden_actual += 1

            if incluir_informes:
                for linea in informes_desc.strip().splitlines():
                    if linea.strip():
                        agregar_punto(db, sesion.id, TipoPuntoEnum.informe, linea.strip(), orden_actual)
                        orden_actual += 1

            for desc in acuerdos:
                if desc.strip():
                    agregar_punto(db, sesion.id, TipoPuntoEnum.acuerdo, desc.strip(), orden_actual)
                    orden_actual += 1

            st.success(f"Sesión #{sesion.numero_sesion} creada correctamente (ID: {sesion.id}).")
            st.rerun()

# ── Sesiones registradas ──────────────────────────────────────────────────────
with tab_ver:
    st.subheader("Sesiones registradas")

    anio_filtro = st.selectbox("Año", [date.today().year] + list(range(date.today().year - 1, 2019, -1)))
    sesiones = listar_sesiones(db, anio=anio_filtro)

    if sesiones:
        import pandas as pd
        df_s = pd.DataFrame([
            {
                "ID": s.id,
                "No.": s.numero_sesion,
                "Naturaleza": s.naturaleza.value,
                "Tipo": s.tipo_sesion,
                "Fecha": s.fecha,
                "Modalidad": s.modalidad.value,
                "Cerrada": "✅" if s.cerrada else "🔓",
                "Puntos": len([p for p in s.puntos if p.incluido]),
            }
            for s in sesiones
        ])
        st.dataframe(df_s, use_container_width=True, hide_index=True)

        # Ver puntos de una sesión
        sesion_id_ver = st.number_input("ID de sesión para ver puntos", min_value=1, step=1)
        if st.button("Ver puntos"):
            s = obtener_sesion(db, int(sesion_id_ver))
            if s:
                df_p = pd.DataFrame([
                    {"Orden": p.orden, "Tipo": p.tipo.value, "Descripción": p.descripcion or "—", "Incluido": p.incluido}
                    for p in s.puntos
                ])
                st.dataframe(df_p, use_container_width=True, hide_index=True)
            else:
                st.warning("Sesión no encontrada.")
    else:
        st.info("No hay sesiones registradas para este año.")

db.close()
