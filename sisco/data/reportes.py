"""
Consultas agregadas para reportes
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from sisco.database.models import (
    Sesion, Asistencia, Participacion, Votacion,
    Solicitud, PuntoOrdenDia, NaturalezaEnum, ResultadoVotacionEnum
)


def resumen_sesiones(db: Session, anio: int | None = None, naturaleza: str | None = None):
    q = db.query(Sesion)
    if anio:
        q = q.filter(extract("year", Sesion.fecha) == anio)
    if naturaleza:
        q = q.filter(Sesion.naturaleza == naturaleza)
    sesiones = q.all()

    total = len(sesiones)
    por_tipo = {}
    for s in sesiones:
        key = f"{s.naturaleza.value} — {s.tipo_sesion}"
        por_tipo[key] = por_tipo.get(key, 0) + 1

    return {"total": total, "por_tipo": por_tipo, "sesiones": sesiones}


def resumen_asistencias(db: Session, anio: int | None = None, integrante_id: int | None = None):
    q = db.query(Asistencia).join(Sesion)
    if anio:
        q = q.filter(extract("year", Sesion.fecha) == anio)
    if integrante_id:
        q = q.filter(Asistencia.integrante_id == integrante_id)

    asistencias = q.all()
    total     = len(asistencias)
    presentes = sum(1 for a in asistencias if a.presente)
    faltas    = total - presentes
    pct_asist = presentes / total * 100 if total else 0

    por_modalidad = {}
    for a in asistencias:
        if a.presente and a.modalidad:
            k = a.modalidad.value
            por_modalidad[k] = por_modalidad.get(k, 0) + 1

    return {
        "total": total,
        "presentes": presentes,
        "faltas": faltas,
        "pct_asistencia": pct_asist,
        "por_modalidad": por_modalidad,
        "detalle": asistencias,
    }


def resumen_votaciones(db: Session, anio: int | None = None):
    q = db.query(Votacion).join(PuntoOrdenDia).join(Sesion)
    if anio:
        q = q.filter(extract("year", Sesion.fecha) == anio)

    votaciones = q.all()
    total = len(votaciones)
    por_resultado = {r.value: 0 for r in ResultadoVotacionEnum}
    for v in votaciones:
        por_resultado[v.resultado.value] += 1

    return {"total": total, "por_resultado": por_resultado, "detalle": votaciones}


def resumen_solicitudes(db: Session, anio: int | None = None, integrante_id: int | None = None):
    q = db.query(Solicitud).join(PuntoOrdenDia).join(Sesion)
    if anio:
        q = q.filter(extract("year", Sesion.fecha) == anio)
    if integrante_id:
        q = q.filter(Solicitud.integrante_id == integrante_id)

    return q.all()
