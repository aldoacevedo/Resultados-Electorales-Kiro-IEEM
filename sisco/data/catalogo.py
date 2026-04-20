"""
CRUD — Catálogo de integrantes y partidos
"""
from sqlalchemy.orm import Session
from sisco.database.models import Integrante, Partido, PeriodoIntegrante, CargoEnum
from datetime import date


# ── Partidos ──────────────────────────────────────────────────────────────────

def listar_partidos(db: Session, solo_activos: bool = True):
    q = db.query(Partido)
    if solo_activos:
        q = q.filter(Partido.activo == True)
    return q.order_by(Partido.siglas).all()


def crear_partido(db: Session, nombre: str, siglas: str) -> Partido:
    p = Partido(nombre=nombre, siglas=siglas.upper())
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


def actualizar_partido(db: Session, partido_id: int, nombre: str, siglas: str) -> Partido:
    p = db.query(Partido).filter(Partido.id == partido_id).first()
    if p:
        p.nombre = nombre
        p.siglas = siglas.upper()
        db.commit()
        db.refresh(p)
    return p


def desactivar_partido(db: Session, partido_id: int):
    p = db.query(Partido).filter(Partido.id == partido_id).first()
    if p:
        p.activo = False
        db.commit()


# ── Integrantes ───────────────────────────────────────────────────────────────

def listar_integrantes(db: Session, solo_activos: bool = True):
    q = db.query(Integrante)
    if solo_activos:
        q = q.filter(Integrante.activo == True)
    return q.order_by(Integrante.cargo, Integrante.nombre).all()


def crear_integrante(
    db: Session,
    nombre: str,
    cargo: CargoEnum,
    partido_id: int | None,
    fecha_inicio: date,
    fecha_fin: date | None = None,
) -> Integrante:
    integrante = Integrante(nombre=nombre, cargo=cargo)
    db.add(integrante)
    db.flush()
    periodo = PeriodoIntegrante(
        integrante_id=integrante.id,
        partido_id=partido_id,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
    )
    db.add(periodo)
    db.commit()
    db.refresh(integrante)
    return integrante


def actualizar_integrante(db: Session, integrante_id: int, nombre: str, cargo: CargoEnum) -> Integrante:
    i = db.query(Integrante).filter(Integrante.id == integrante_id).first()
    if i:
        i.nombre = nombre
        i.cargo  = cargo
        db.commit()
        db.refresh(i)
    return i


def cerrar_periodo(db: Session, integrante_id: int, fecha_fin: date):
    """Cierra el periodo vigente de un integrante."""
    from sqlalchemy import or_
    periodo = (
        db.query(PeriodoIntegrante)
        .filter(
            PeriodoIntegrante.integrante_id == integrante_id,
            or_(PeriodoIntegrante.fecha_fin == None, PeriodoIntegrante.fecha_fin >= date.today()),
        )
        .first()
    )
    if periodo:
        periodo.fecha_fin = fecha_fin
        db.commit()


def historial_integrante(db: Session, integrante_id: int):
    return (
        db.query(PeriodoIntegrante)
        .filter(PeriodoIntegrante.integrante_id == integrante_id)
        .order_by(PeriodoIntegrante.fecha_inicio.desc())
        .all()
    )
