"""
CRUD — Sesiones y Orden del Día
"""
from sqlalchemy.orm import Session
from sisco.database.models import (
    Sesion, PuntoOrdenDia, NaturalezaEnum, ModalidadEnum, TipoPuntoEnum
)
from sisco.utils.helpers import siguiente_numero_sesion
from datetime import date


PUNTOS_FIJOS = [
    TipoPuntoEnum.asistencia,
    TipoPuntoEnum.orden_dia,
    TipoPuntoEnum.asunto,
    TipoPuntoEnum.clausura,
]


def listar_sesiones(db: Session, anio: int | None = None):
    q = db.query(Sesion).order_by(Sesion.fecha.desc())
    if anio:
        from sqlalchemy import extract
        q = q.filter(extract("year", Sesion.fecha) == anio)
    return q.all()


def obtener_sesion(db: Session, sesion_id: int) -> Sesion | None:
    return db.query(Sesion).filter(Sesion.id == sesion_id).first()


def crear_sesion(
    db: Session,
    naturaleza: NaturalezaEnum,
    tipo_sesion: str,
    fecha: date,
    modalidad: ModalidadEnum,
) -> Sesion:
    numero = siguiente_numero_sesion(db, fecha.year, naturaleza, tipo_sesion)
    sesion = Sesion(
        naturaleza=naturaleza,
        tipo_sesion=tipo_sesion,
        fecha=fecha,
        numero_sesion=numero,
        modalidad=modalidad,
    )
    db.add(sesion)
    db.flush()
    _crear_puntos_fijos(db, sesion.id)
    db.commit()
    db.refresh(sesion)
    return sesion


def _crear_puntos_fijos(db: Session, sesion_id: int):
    orden_map = {
        TipoPuntoEnum.asistencia: 1,
        TipoPuntoEnum.orden_dia:  2,
        TipoPuntoEnum.asunto:     98,
        TipoPuntoEnum.clausura:   99,
    }
    for tipo, orden in orden_map.items():
        db.add(PuntoOrdenDia(sesion_id=sesion_id, tipo=tipo, orden=orden, incluido=True))


def agregar_punto(
    db: Session,
    sesion_id: int,
    tipo: TipoPuntoEnum,
    descripcion: str | None = None,
    orden: int | None = None,
) -> PuntoOrdenDia:
    if orden is None:
        # Insertar antes de asuntos generales (orden 98)
        ultimo = (
            db.query(PuntoOrdenDia)
            .filter(
                PuntoOrdenDia.sesion_id == sesion_id,
                PuntoOrdenDia.orden < 98,
            )
            .order_by(PuntoOrdenDia.orden.desc())
            .first()
        )
        orden = (ultimo.orden + 1) if ultimo else 3

    punto = PuntoOrdenDia(
        sesion_id=sesion_id,
        tipo=tipo,
        descripcion=descripcion,
        orden=orden,
        incluido=True,
    )
    db.add(punto)
    db.commit()
    db.refresh(punto)
    return punto


def omitir_punto(db: Session, punto_id: int):
    p = db.query(PuntoOrdenDia).filter(PuntoOrdenDia.id == punto_id).first()
    if p:
        p.incluido = False
        db.commit()


def cerrar_sesion(db: Session, sesion_id: int, hora_clausura: str):
    s = db.query(Sesion).filter(Sesion.id == sesion_id).first()
    if s:
        s.hora_clausura = hora_clausura
        s.cerrada = True
        db.commit()
