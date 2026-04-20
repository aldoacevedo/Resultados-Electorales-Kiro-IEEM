"""
CRUD — Asistencia, Participaciones, Votaciones, Solicitudes
"""
from sqlalchemy.orm import Session
from sisco.database.models import (
    Asistencia, Participacion, Votacion, VotoIntegrante,
    Modificacion, Solicitud, SeguimientoSolicitud,
    ModalidadEnum, TipoParticipacionEnum, ResultadoVotacionEnum
)
from datetime import datetime


# ── Asistencia ────────────────────────────────────────────────────────────────

def registrar_asistencia(
    db: Session,
    sesion_id: int,
    integrante_id: int,
    presente: bool,
    modalidad: ModalidadEnum | None = None,
    justificacion: str | None = None,
    es_suplente: bool = False,
) -> Asistencia:
    # Upsert: si ya existe, actualizar
    a = (
        db.query(Asistencia)
        .filter(Asistencia.sesion_id == sesion_id, Asistencia.integrante_id == integrante_id)
        .first()
    )
    if a:
        a.presente      = presente
        a.modalidad     = modalidad
        a.justificacion = justificacion
        a.es_suplente   = es_suplente
    else:
        a = Asistencia(
            sesion_id=sesion_id,
            integrante_id=integrante_id,
            presente=presente,
            modalidad=modalidad,
            justificacion=justificacion,
            es_suplente=es_suplente,
        )
        db.add(a)
    db.commit()
    db.refresh(a)
    return a


def asistencias_sesion(db: Session, sesion_id: int):
    return db.query(Asistencia).filter(Asistencia.sesion_id == sesion_id).all()


# ── Participaciones ───────────────────────────────────────────────────────────

def agregar_participacion(
    db: Session,
    punto_id: int,
    integrante_id: int,
    tipo: TipoParticipacionEnum,
    ronda: int | None = None,
    texto: str | None = None,
) -> Participacion:
    # Calcular orden dentro del punto
    ultimo_orden = (
        db.query(Participacion)
        .filter(Participacion.punto_id == punto_id)
        .count()
    )
    p = Participacion(
        punto_id=punto_id,
        integrante_id=integrante_id,
        tipo=tipo,
        ronda=ronda,
        texto=texto,
        orden=ultimo_orden + 1,
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


def participaciones_punto(db: Session, punto_id: int):
    return (
        db.query(Participacion)
        .filter(Participacion.punto_id == punto_id)
        .order_by(Participacion.orden)
        .all()
    )


def eliminar_participacion(db: Session, participacion_id: int):
    p = db.query(Participacion).filter(Participacion.id == participacion_id).first()
    if p:
        db.delete(p)
        db.commit()


# ── Modificaciones ────────────────────────────────────────────────────────────

def agregar_modificacion(db: Session, punto_id: int, texto: str) -> Modificacion:
    m = Modificacion(punto_id=punto_id, texto=texto)
    db.add(m)
    db.commit()
    db.refresh(m)
    return m


# ── Votaciones ────────────────────────────────────────────────────────────────

def registrar_votacion(
    db: Session,
    punto_id: int,
    resultado: ResultadoVotacionEnum,
    hora_aprobacion: str | None = None,
    observaciones: str | None = None,
) -> Votacion:
    v = db.query(Votacion).filter(Votacion.punto_id == punto_id).first()
    if v:
        v.resultado       = resultado
        v.hora_aprobacion = hora_aprobacion
        v.observaciones   = observaciones
    else:
        v = Votacion(
            punto_id=punto_id,
            resultado=resultado,
            hora_aprobacion=hora_aprobacion,
            observaciones=observaciones,
        )
        db.add(v)
    db.commit()
    db.refresh(v)
    return v


def registrar_voto_integrante(
    db: Session, votacion_id: int, integrante_id: int, sentido: str
) -> VotoIntegrante:
    vi = (
        db.query(VotoIntegrante)
        .filter(VotoIntegrante.votacion_id == votacion_id, VotoIntegrante.integrante_id == integrante_id)
        .first()
    )
    if vi:
        vi.sentido = sentido
    else:
        vi = VotoIntegrante(votacion_id=votacion_id, integrante_id=integrante_id, sentido=sentido)
        db.add(vi)
    db.commit()
    db.refresh(vi)
    return vi


# ── Solicitudes ───────────────────────────────────────────────────────────────

def crear_solicitud(
    db: Session, punto_id: int, integrante_id: int, descripcion: str, estatus: str | None = None
) -> Solicitud:
    s = Solicitud(punto_id=punto_id, integrante_id=integrante_id, descripcion=descripcion, estatus=estatus)
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


def agregar_seguimiento(db: Session, solicitud_id: int, texto: str) -> SeguimientoSolicitud:
    seg = SeguimientoSolicitud(solicitud_id=solicitud_id, texto=texto, fecha=datetime.now())
    db.add(seg)
    db.commit()
    db.refresh(seg)
    return seg


def actualizar_estatus(db: Session, solicitud_id: int, estatus: str):
    s = db.query(Solicitud).filter(Solicitud.id == solicitud_id).first()
    if s:
        s.estatus = estatus
        db.commit()


def solicitudes_sesion(db: Session, sesion_id: int):
    from sisco.database.models import PuntoOrdenDia
    return (
        db.query(Solicitud)
        .join(PuntoOrdenDia)
        .filter(PuntoOrdenDia.sesion_id == sesion_id)
        .all()
    )
