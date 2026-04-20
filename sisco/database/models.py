"""
Modelos ORM — SISCO
"""
from sqlalchemy import (
    Column, Integer, String, Boolean, Date, DateTime,
    ForeignKey, Text, Enum as SAEnum
)
from sqlalchemy.orm import relationship
from sisco.database.db import Base
import enum


# ── Enums ─────────────────────────────────────────────────────────────────────

class NaturalezaEnum(str, enum.Enum):
    ordinaria = "Ordinaria"
    judicial  = "Judicial"

class ModalidadEnum(str, enum.Enum):
    presencial = "Presencial"
    virtual    = "Virtual"
    hibrida    = "Híbrida"

class CargoEnum(str, enum.Enum):
    cp = "CP"   # Consejero/a Presidente/a
    se = "SE"   # Secretario/a Ejecutivo/a
    ce = "CE"   # Consejero/a Electoral
    pp = "PP"   # Representante de Partido Político

class TipoPuntoEnum(str, enum.Enum):
    asistencia   = "Asistencia"
    orden_dia    = "Orden del día"
    acta         = "Aprobación de acta"
    informe      = "Informe/Presentación"
    acuerdo      = "Acuerdo/Resolución"
    asunto       = "Asunto general"
    clausura     = "Declaratoria de clausura"

class ResultadoVotacionEnum(str, enum.Enum):
    unanimidad = "Unanimidad"
    mayoria    = "Mayoría"
    desechado  = "Desechado"

class TipoParticipacionEnum(str, enum.Enum):
    solicitud          = "Solicitud"
    voto_concurrente   = "Voto concurrente"
    voto_particular    = "Voto particular"
    participacion      = "Participación"


# ── Catálogo ──────────────────────────────────────────────────────────────────

class Partido(Base):
    __tablename__ = "partidos"

    id      = Column(Integer, primary_key=True, index=True)
    nombre  = Column(String(120), nullable=False)
    siglas  = Column(String(30), nullable=False, unique=True)
    activo  = Column(Boolean, default=True)

    periodos = relationship("PeriodoIntegrante", back_populates="partido")


class Integrante(Base):
    __tablename__ = "integrantes"

    id     = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(200), nullable=False)
    cargo  = Column(SAEnum(CargoEnum), nullable=False)
    activo = Column(Boolean, default=True)

    periodos    = relationship("PeriodoIntegrante", back_populates="integrante")
    asistencias = relationship("Asistencia", back_populates="integrante")
    participaciones = relationship("Participacion", back_populates="integrante")


class PeriodoIntegrante(Base):
    """Vincula un integrante a un partido y define su periodo de vigencia."""
    __tablename__ = "periodos_integrante"

    id             = Column(Integer, primary_key=True, index=True)
    integrante_id  = Column(Integer, ForeignKey("integrantes.id"), nullable=False)
    partido_id     = Column(Integer, ForeignKey("partidos.id"), nullable=True)  # null para CP/SE/CE
    fecha_inicio   = Column(Date, nullable=False)
    fecha_fin      = Column(Date, nullable=True)   # null = vigente

    integrante = relationship("Integrante", back_populates="periodos")
    partido    = relationship("Partido", back_populates="periodos")


# ── Sesiones ──────────────────────────────────────────────────────────────────

class Sesion(Base):
    __tablename__ = "sesiones"

    id                 = Column(Integer, primary_key=True, index=True)
    naturaleza         = Column(SAEnum(NaturalezaEnum), nullable=False)
    tipo_sesion        = Column(String(100), nullable=False)
    fecha              = Column(Date, nullable=False)
    numero_sesion      = Column(Integer, nullable=False)   # auto por año+naturaleza+tipo
    modalidad          = Column(SAEnum(ModalidadEnum), nullable=False)
    hora_transmision   = Column(String(5), nullable=True)  # HH:MM
    hora_instalacion   = Column(String(5), nullable=True)
    hora_clausura      = Column(String(5), nullable=True)
    cerrada            = Column(Boolean, default=False)

    puntos      = relationship("PuntoOrdenDia", back_populates="sesion", order_by="PuntoOrdenDia.orden")
    asistencias = relationship("Asistencia", back_populates="sesion")


class PuntoOrdenDia(Base):
    __tablename__ = "puntos_orden_dia"

    id          = Column(Integer, primary_key=True, index=True)
    sesion_id   = Column(Integer, ForeignKey("sesiones.id"), nullable=False)
    tipo        = Column(SAEnum(TipoPuntoEnum), nullable=False)
    descripcion = Column(Text, nullable=True)
    orden       = Column(Integer, nullable=False)
    incluido    = Column(Boolean, default=True)  # False = punto omitido (ej. sin actas)

    sesion          = relationship("Sesion", back_populates="puntos")
    votacion        = relationship("Votacion", back_populates="punto", uselist=False)
    participaciones = relationship("Participacion", back_populates="punto")
    modificaciones  = relationship("Modificacion", back_populates="punto")


# ── Seguimiento ───────────────────────────────────────────────────────────────

class Asistencia(Base):
    __tablename__ = "asistencias"

    id            = Column(Integer, primary_key=True, index=True)
    sesion_id     = Column(Integer, ForeignKey("sesiones.id"), nullable=False)
    integrante_id = Column(Integer, ForeignKey("integrantes.id"), nullable=False)
    presente      = Column(Boolean, nullable=False, default=True)
    justificacion = Column(Text, nullable=True)
    modalidad     = Column(SAEnum(ModalidadEnum), nullable=True)
    es_suplente   = Column(Boolean, default=False)

    sesion     = relationship("Sesion", back_populates="asistencias")
    integrante = relationship("Integrante", back_populates="asistencias")


class Participacion(Base):
    __tablename__ = "participaciones"

    id            = Column(Integer, primary_key=True, index=True)
    punto_id      = Column(Integer, ForeignKey("puntos_orden_dia.id"), nullable=False)
    integrante_id = Column(Integer, ForeignKey("integrantes.id"), nullable=False)
    tipo          = Column(SAEnum(TipoParticipacionEnum), nullable=False)
    ronda         = Column(Integer, nullable=True)
    texto         = Column(Text, nullable=True)
    orden         = Column(Integer, nullable=True)

    punto      = relationship("PuntoOrdenDia", back_populates="participaciones")
    integrante = relationship("Integrante", back_populates="participaciones")


class Modificacion(Base):
    """Modificaciones a un punto del orden del día."""
    __tablename__ = "modificaciones"

    id       = Column(Integer, primary_key=True, index=True)
    punto_id = Column(Integer, ForeignKey("puntos_orden_dia.id"), nullable=False)
    texto    = Column(Text, nullable=False)

    punto = relationship("PuntoOrdenDia", back_populates="modificaciones")


class Votacion(Base):
    __tablename__ = "votaciones"

    id              = Column(Integer, primary_key=True, index=True)
    punto_id        = Column(Integer, ForeignKey("puntos_orden_dia.id"), nullable=False, unique=True)
    resultado       = Column(SAEnum(ResultadoVotacionEnum), nullable=False)
    hora_aprobacion = Column(String(5), nullable=True)
    observaciones   = Column(Text, nullable=True)

    punto          = relationship("PuntoOrdenDia", back_populates="votacion")
    votos_detalle  = relationship("VotoIntegrante", back_populates="votacion")


class VotoIntegrante(Base):
    """Voto individual por integrante en una votación."""
    __tablename__ = "votos_integrante"

    id            = Column(Integer, primary_key=True, index=True)
    votacion_id   = Column(Integer, ForeignKey("votaciones.id"), nullable=False)
    integrante_id = Column(Integer, ForeignKey("integrantes.id"), nullable=False)
    sentido       = Column(String(20), nullable=False)  # "A favor" / "En contra"

    votacion   = relationship("Votacion", back_populates="votos_detalle")
    integrante = relationship("Integrante")


# ── Solicitudes con historial de seguimiento ──────────────────────────────────

class Solicitud(Base):
    __tablename__ = "solicitudes"

    id            = Column(Integer, primary_key=True, index=True)
    punto_id      = Column(Integer, ForeignKey("puntos_orden_dia.id"), nullable=False)
    integrante_id = Column(Integer, ForeignKey("integrantes.id"), nullable=False)
    descripcion   = Column(Text, nullable=False)
    estatus       = Column(String(60), nullable=True)

    seguimientos = relationship("SeguimientoSolicitud", back_populates="solicitud")
    integrante   = relationship("Integrante")
    punto        = relationship("PuntoOrdenDia")


class SeguimientoSolicitud(Base):
    """Historial de seguimientos de una solicitud (múltiples entradas)."""
    __tablename__ = "seguimientos_solicitud"

    id           = Column(Integer, primary_key=True, index=True)
    solicitud_id = Column(Integer, ForeignKey("solicitudes.id"), nullable=False)
    texto        = Column(Text, nullable=False)
    fecha        = Column(DateTime, nullable=False)

    solicitud = relationship("Solicitud", back_populates="seguimientos")
