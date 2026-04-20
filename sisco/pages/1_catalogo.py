"""
Página: Catálogo de integrantes y partidos
"""
import streamlit as st
from datetime import date
from sisco.database.db import SessionLocal
from sisco.database.models import CargoEnum
from sisco.data.catalogo import (
    listar_partidos, crear_partido, actualizar_partido, desactivar_partido,
    listar_integrantes, crear_integrante, actualizar_integrante,
    cerrar_periodo, historial_integrante,
)
from sisco.utils.styles import inject, header

st.set_page_config(page_title="Catálogo — SISCO", layout="wide")
inject(st)
st.markdown(header("Catálogo", "Integrantes y partidos políticos"), unsafe_allow_html=True)

db = SessionLocal()

tab_partidos, tab_integrantes = st.tabs(["Partidos políticos", "Integrantes del CG"])

# ── Partidos ──────────────────────────────────────────────────────────────────
with tab_partidos:
    st.subheader("Partidos políticos")

    partidos = listar_partidos(db, solo_activos=False)
    if partidos:
        import pandas as pd
        df_p = pd.DataFrame([{"ID": p.id, "Siglas": p.siglas, "Nombre": p.nombre, "Activo": p.activo} for p in partidos])
        st.dataframe(df_p, use_container_width=True, hide_index=True)
    else:
        st.info("No hay partidos registrados.")

    with st.expander("➕ Agregar / Editar partido"):
        col1, col2 = st.columns(2)
        with col1:
            p_nombre = st.text_input("Nombre del partido", key="p_nombre")
            p_siglas = st.text_input("Siglas", key="p_siglas")
        with col2:
            p_id_edit = st.number_input("ID a editar (0 = nuevo)", min_value=0, step=1, key="p_id_edit")

        if st.button("Guardar partido"):
            if p_nombre and p_siglas:
                if p_id_edit:
                    actualizar_partido(db, int(p_id_edit), p_nombre, p_siglas)
                    st.success("Partido actualizado.")
                else:
                    crear_partido(db, p_nombre, p_siglas)
                    st.success("Partido creado.")
                st.rerun()
            else:
                st.warning("Completa nombre y siglas.")

    with st.expander("🗑️ Desactivar partido"):
        p_id_des = st.number_input("ID del partido a desactivar", min_value=1, step=1, key="p_id_des")
        if st.button("Desactivar"):
            desactivar_partido(db, int(p_id_des))
            st.success("Partido desactivado.")
            st.rerun()

# ── Integrantes ───────────────────────────────────────────────────────────────
with tab_integrantes:
    st.subheader("Integrantes del Consejo General")

    integrantes = listar_integrantes(db, solo_activos=False)
    partidos_activos = listar_partidos(db)

    if integrantes:
        import pandas as pd
        df_i = pd.DataFrame([
            {"ID": i.id, "Nombre": i.nombre, "Cargo": i.cargo.value, "Activo": i.activo}
            for i in integrantes
        ])
        st.dataframe(df_i, use_container_width=True, hide_index=True)
    else:
        st.info("No hay integrantes registrados.")

    with st.expander("➕ Agregar integrante"):
        col1, col2 = st.columns(2)
        with col1:
            i_nombre = st.text_input("Nombre completo", key="i_nombre")
            i_cargo  = st.selectbox("Cargo", [c.value for c in CargoEnum], key="i_cargo")
        with col2:
            opciones_pp = {f"{p.siglas} — {p.nombre}": p.id for p in partidos_activos}
            i_partido_label = st.selectbox("Partido (solo PP)", ["— Ninguno —"] + list(opciones_pp.keys()), key="i_partido")
            i_inicio = st.date_input("Inicio de periodo", value=date.today(), key="i_inicio")
            i_fin    = st.date_input("Fin de periodo (opcional)", value=None, key="i_fin")

        if st.button("Guardar integrante"):
            if i_nombre:
                partido_id = opciones_pp.get(i_partido_label)
                cargo_enum = CargoEnum(i_cargo)
                crear_integrante(db, i_nombre, cargo_enum, partido_id, i_inicio, i_fin or None)
                st.success("Integrante creado.")
                st.rerun()
            else:
                st.warning("Ingresa el nombre del integrante.")

    with st.expander("✏️ Editar integrante"):
        i_id_edit = st.number_input("ID del integrante", min_value=1, step=1, key="i_id_edit")
        i_nombre_edit = st.text_input("Nuevo nombre", key="i_nombre_edit")
        i_cargo_edit  = st.selectbox("Nuevo cargo", [c.value for c in CargoEnum], key="i_cargo_edit")
        if st.button("Actualizar integrante"):
            actualizar_integrante(db, int(i_id_edit), i_nombre_edit, CargoEnum(i_cargo_edit))
            st.success("Integrante actualizado.")
            st.rerun()

    with st.expander("📋 Historial de un integrante"):
        i_id_hist = st.number_input("ID del integrante", min_value=1, step=1, key="i_id_hist")
        if st.button("Ver historial"):
            periodos = historial_integrante(db, int(i_id_hist))
            if periodos:
                import pandas as pd
                df_h = pd.DataFrame([
                    {
                        "Partido": p.partido.siglas if p.partido else "—",
                        "Inicio": p.fecha_inicio,
                        "Fin": p.fecha_fin or "Vigente",
                    }
                    for p in periodos
                ])
                st.dataframe(df_h, use_container_width=True, hide_index=True)
            else:
                st.info("Sin historial.")

    with st.expander("🔒 Cerrar periodo de integrante"):
        i_id_cierre = st.number_input("ID del integrante", min_value=1, step=1, key="i_id_cierre")
        i_fecha_cierre = st.date_input("Fecha de cierre", value=date.today(), key="i_fecha_cierre")
        if st.button("Cerrar periodo"):
            cerrar_periodo(db, int(i_id_cierre), i_fecha_cierre)
            st.success("Periodo cerrado.")
            st.rerun()

db.close()
