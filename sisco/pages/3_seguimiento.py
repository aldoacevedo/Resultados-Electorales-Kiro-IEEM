"""
Página: Seguimiento a la Sesión
"""
import streamlit as st
from datetime import date
from sisco.database.db import SessionLocal
from sisco.database.models import ModalidadEnum, TipoParticipacionEnum, ResultadoVotacionEnum, TipoPuntoEnum
from sisco.data.sesiones import listar_sesiones, obtener_sesion, cerrar_sesion
from sisco.data.seguimiento import (
    registrar_asistencia, asistencias_sesion,
    agregar_participacion, participaciones_punto,
    registrar_votacion, registrar_voto_integrante,
    agregar_modificacion, crear_solicitud, agregar_seguimiento,
    actualizar_estatus, solicitudes_sesion,
)
from sisco.utils.helpers import integrantes_activos_en_fecha
from sisco.utils.styles import inject, header

st.set_page_config(page_title="Seguimiento — SISCO", layout="wide")
inject(st)
st.markdown(header("Seguimiento a la Sesión", "Captura en tiempo real"), unsafe_allow_html=True)

db = SessionLocal()

# ── Selección de sesión ───────────────────────────────────────────────────────
sesiones_abiertas = [s for s in listar_sesiones(db) if not s.cerrada]
if not sesiones_abiertas:
    st.warning("No hay sesiones abiertas. Crea una en el módulo **Orden del Día**.")
    db.close()
    st.stop()

opciones_sesion = {
    f"#{s.numero_sesion} — {s.naturaleza.value} {s.tipo_sesion} ({s.fecha})": s.id
    for s in sesiones_abiertas
}
sesion_label = st.selectbox("Sesión activa", list(opciones_sesion.keys()))
sesion_id    = opciones_sesion[sesion_label]
sesion       = obtener_sesion(db, sesion_id)
integrantes  = integrantes_activos_en_fecha(db, sesion.fecha)

st.markdown("---")

# ── Horas de inicio ───────────────────────────────────────────────────────────
col1, col2 = st.columns(2)
with col1:
    hora_tx = st.text_input("Hora inicio transmisión (HH:MM)", value=sesion.hora_transmision or "")
with col2:
    hora_inst = st.text_input("Hora de instalación (HH:MM)", value=sesion.hora_instalacion or "")

if st.button("Guardar horas de inicio"):
    from sisco.database.db import SessionLocal as SL
    _db = SL()
    s = _db.query(sesion.__class__).filter_by(id=sesion_id).first()
    s.hora_transmision = hora_tx or None
    s.hora_instalacion = hora_inst or None
    _db.commit()
    _db.close()
    st.success("Horas guardadas.")

st.markdown("---")

# ── Tabs por sección ──────────────────────────────────────────────────────────
tab_asist, tab_puntos, tab_solicitudes, tab_clausura = st.tabs([
    "👥 Asistencia", "📌 Puntos del orden del día", "📨 Solicitudes", "🔒 Clausura"
])

# ── Asistencia ────────────────────────────────────────────────────────────────
with tab_asist:
    st.subheader("Registro de asistencia")
    asistencias_actuales = {a.integrante_id: a for a in asistencias_sesion(db, sesion_id)}

    for integrante in integrantes:
        a_actual = asistencias_actuales.get(integrante.id)
        with st.expander(f"{integrante.cargo.value} — {integrante.nombre}"):
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                presente = st.radio(
                    "Asistencia", ["Presente", "Falta"],
                    index=0 if (not a_actual or a_actual.presente) else 1,
                    key=f"asist_{integrante.id}",
                    horizontal=True,
                )
            with col_b:
                modalidad = st.selectbox(
                    "Modalidad", [m.value for m in ModalidadEnum],
                    index=0 if not a_actual or not a_actual.modalidad else [m.value for m in ModalidadEnum].index(a_actual.modalidad.value),
                    key=f"modal_{integrante.id}",
                )
            with col_c:
                es_suplente = st.checkbox("Es suplente", value=a_actual.es_suplente if a_actual else False, key=f"supl_{integrante.id}")

            justificacion = ""
            if presente == "Falta":
                justificacion = st.text_input("Justificación", value=a_actual.justificacion or "", key=f"just_{integrante.id}")

            if st.button("Guardar", key=f"btn_asist_{integrante.id}"):
                registrar_asistencia(
                    db, sesion_id, integrante.id,
                    presente=(presente == "Presente"),
                    modalidad=ModalidadEnum(modalidad),
                    justificacion=justificacion or None,
                    es_suplente=es_suplente,
                )
                st.success("Guardado.")

# ── Puntos del orden del día ──────────────────────────────────────────────────
with tab_puntos:
    puntos = [p for p in sesion.puntos if p.incluido and p.tipo not in (TipoPuntoEnum.asistencia, TipoPuntoEnum.orden_dia, TipoPuntoEnum.clausura)]

    for punto in puntos:
        titulo = f"Punto {punto.orden}: {punto.tipo.value}"
        if punto.descripcion:
            titulo += f" — {punto.descripcion[:60]}"

        with st.expander(titulo):
            # Participaciones
            st.markdown("**Participaciones**")
            partics = participaciones_punto(db, punto.id)
            if partics:
                import pandas as pd
                df_par = pd.DataFrame([
                    {
                        "Ronda": p.ronda or "—",
                        "Integrante": p.integrante.nombre,
                        "Tipo": p.tipo.value,
                        "Texto": (p.texto or "")[:80],
                    }
                    for p in partics
                ])
                st.dataframe(df_par, use_container_width=True, hide_index=True)

            col_p1, col_p2, col_p3 = st.columns(3)
            with col_p1:
                int_opts = {i.nombre: i.id for i in integrantes}
                int_sel  = st.selectbox("Integrante", list(int_opts.keys()), key=f"int_p_{punto.id}")
            with col_p2:
                tipo_part = st.selectbox("Tipo", [t.value for t in TipoParticipacionEnum], key=f"tipo_p_{punto.id}")
            with col_p3:
                ronda_p = st.number_input("Ronda", min_value=1, step=1, key=f"ronda_p_{punto.id}")

            texto_p = st.text_area("Texto (voto concurrente/particular)", key=f"texto_p_{punto.id}", height=60)

            if st.button("➕ Agregar participación", key=f"btn_part_{punto.id}"):
                agregar_participacion(
                    db, punto.id, int_opts[int_sel],
                    TipoParticipacionEnum(tipo_part), int(ronda_p), texto_p or None
                )
                st.success("Participación registrada.")
                st.rerun()

            st.markdown("---")

            # Modificaciones
            mod_texto = st.text_input("Modificación al punto (si aplica)", key=f"mod_{punto.id}")
            if st.button("Guardar modificación", key=f"btn_mod_{punto.id}") and mod_texto:
                agregar_modificacion(db, punto.id, mod_texto)
                st.success("Modificación guardada.")

            st.markdown("---")

            # Votación (solo acuerdos/actas/informes)
            if punto.tipo in (TipoPuntoEnum.acuerdo, TipoPuntoEnum.acta, TipoPuntoEnum.informe):
                st.markdown("**Votación**")
                col_v1, col_v2 = st.columns(2)
                with col_v1:
                    resultado = st.selectbox(
                        "Resultado", [r.value for r in ResultadoVotacionEnum], key=f"res_{punto.id}"
                    )
                with col_v2:
                    hora_apro = st.text_input("Hora de aprobación (HH:MM)", key=f"hora_v_{punto.id}")

                obs_v = st.text_area("Observaciones", key=f"obs_v_{punto.id}", height=60)

                if st.button("💾 Registrar votación", key=f"btn_vot_{punto.id}"):
                    registrar_votacion(
                        db, punto.id, ResultadoVotacionEnum(resultado),
                        hora_apro or None, obs_v or None
                    )
                    st.success("Votación registrada.")

# ── Solicitudes ───────────────────────────────────────────────────────────────
with tab_solicitudes:
    st.subheader("Solicitudes")
    solicitudes = solicitudes_sesion(db, sesion_id)

    if solicitudes:
        for sol in solicitudes:
            with st.expander(f"[{sol.estatus or 'Sin estatus'}] {sol.integrante.nombre} — {sol.descripcion[:60]}"):
                st.markdown(f"**Descripción:** {sol.descripcion}")
                nuevo_estatus = st.text_input("Estatus", value=sol.estatus or "", key=f"est_{sol.id}")
                if st.button("Actualizar estatus", key=f"btn_est_{sol.id}"):
                    actualizar_estatus(db, sol.id, nuevo_estatus)
                    st.success("Estatus actualizado.")
                    st.rerun()

                st.markdown("**Seguimientos:**")
                for seg in sol.seguimientos:
                    st.markdown(f"- `{seg.fecha.strftime('%d/%m/%Y %H:%M')}` — {seg.texto}")

                nuevo_seg = st.text_area("Agregar seguimiento", key=f"seg_{sol.id}", height=60)
                if st.button("➕ Agregar", key=f"btn_seg_{sol.id}") and nuevo_seg:
                    agregar_seguimiento(db, sol.id, nuevo_seg)
                    st.success("Seguimiento agregado.")
                    st.rerun()
    else:
        st.info("No hay solicitudes registradas para esta sesión.")

    st.markdown("---")
    st.markdown("**Nueva solicitud**")
    puntos_disp = {f"Punto {p.orden} — {p.descripcion or p.tipo.value}": p.id for p in sesion.puntos if p.incluido}
    int_opts_s  = {i.nombre: i.id for i in integrantes}
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        punto_sol = st.selectbox("Punto", list(puntos_disp.keys()), key="punto_sol")
        int_sol   = st.selectbox("Integrante", list(int_opts_s.keys()), key="int_sol")
    with col_s2:
        desc_sol  = st.text_area("Descripción", key="desc_sol", height=80)
        est_sol   = st.text_input("Estatus inicial", key="est_sol")

    if st.button("Crear solicitud"):
        if desc_sol:
            crear_solicitud(db, puntos_disp[punto_sol], int_opts_s[int_sol], desc_sol, est_sol or None)
            st.success("Solicitud creada.")
            st.rerun()

# ── Clausura ──────────────────────────────────────────────────────────────────
with tab_clausura:
    st.subheader("Declaratoria de clausura")
    hora_cl = st.text_input("Hora de clausura (HH:MM)")
    if st.button("🔒 Cerrar sesión", type="primary"):
        if hora_cl:
            cerrar_sesion(db, sesion_id, hora_cl)
            st.success(f"Sesión cerrada a las {hora_cl}.")
            st.rerun()
        else:
            st.warning("Ingresa la hora de clausura.")

db.close()
