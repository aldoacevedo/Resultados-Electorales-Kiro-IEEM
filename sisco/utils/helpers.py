"""
Utilidades generales — SISCO
"""
from sqlalchemy.orm import Session
from sisco.database.models import Sesion, NaturalezaEnum


def siguiente_numero_sesion(db: Session, anio: int, naturaleza: NaturalezaEnum, tipo_sesion: str) -> int:
    """Calcula el siguiente número de sesión para el año + naturaleza + tipo dados."""
    from sqlalchemy import extract, func
    ultimo = (
        db.query(func.max(Sesion.numero_sesion))
        .filter(
            extract("year", Sesion.fecha) == anio,
            Sesion.naturaleza == naturaleza,
            Sesion.tipo_sesion == tipo_sesion,
        )
        .scalar()
    )
    return (ultimo or 0) + 1


def hora_valida(hora: str) -> bool:
    """Valida formato HH:MM."""
    try:
        h, m = hora.split(":")
        return 0 <= int(h) <= 23 and 0 <= int(m) <= 59
    except Exception:
        return False


def integrantes_activos_en_fecha(db: Session, fecha):
    """Devuelve los integrantes con periodo vigente en la fecha dada."""
    from sisco.database.models import Integrante, PeriodoIntegrante
    from sqlalchemy import or_
    return (
        db.query(Integrante)
        .join(PeriodoIntegrante)
        .filter(
            PeriodoIntegrante.fecha_inicio <= fecha,
            or_(PeriodoIntegrante.fecha_fin == None, PeriodoIntegrante.fecha_fin >= fecha),
        )
        .all()
    )
