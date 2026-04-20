"""
Seed de datos — Integrantes y partidos del CG del IEEM (2026)
Fuente: https://www.ieem.org.mx/consejo_general/integracion/integracion.html
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from datetime import date
from sisco.database.db import init_db, SessionLocal
from sisco.database.models import Partido, Integrante, PeriodoIntegrante, CargoEnum

FECHA_INICIO = date(2023, 10, 1)  # inicio de periodo estimado post-elección 2023

PARTIDOS = [
    {"nombre": "Partido Acción Nacional",                        "siglas": "PAN"},
    {"nombre": "Partido Revolucionario Institucional",           "siglas": "PRI"},
    {"nombre": "Partido del Trabajo",                            "siglas": "PT"},
    {"nombre": "Partido Verde Ecologista de México",             "siglas": "PVEM"},
    {"nombre": "Movimiento Ciudadano",                           "siglas": "MC"},
    {"nombre": "Movimiento Regeneración Nacional",               "siglas": "MORENA"},
    {"nombre": "Partido de la Revolución Democrática Estado de México", "siglas": "PRD-EM"},
]

# (cargo, nombre, siglas_partido_o_None, es_suplente)
INTEGRANTES = [
    # Consejera Presidenta
    (CargoEnum.cp, "Dra. Amalia Pulido Gómez", None, False),

    # Secretario Ejecutivo
    (CargoEnum.se, "Mtro. Francisco Javier López Corral", None, False),

    # Consejeras Electorales
    (CargoEnum.ce, "Dra. Paula Melgarejo Salgado",              None, False),
    (CargoEnum.ce, "Mtra. Patricia Lozano Sanabria",            None, False),
    (CargoEnum.ce, "Mtra. Karina Ivonne Vaquera Montoya",       None, False),
    (CargoEnum.ce, "Dra. July Erika Armenta Paulino",           None, False),
    (CargoEnum.ce, "Dra. en Educación Sayonara Flores Palacios",None, False),
    (CargoEnum.ce, "Dra. Flor Angeli Vieyra Vázquez",           None, False),

    # Representantes de Partidos — Propietarios
    (CargoEnum.pp, "Lic. Alfonso Guillermo Bravo Álvarez Malo", "PAN",    False),
    (CargoEnum.pp, "Dr. Víctor Capilla Mora",                   "PRI",    False),
    (CargoEnum.pp, "C. Reginaldo Sandoval Flores",              "PT",     False),
    (CargoEnum.pp, "Lic. Fabián Enríquez Gamiz",                "PVEM",   False),
    (CargoEnum.pp, "C. Anselmo García Cruz",                    "MC",     False),
    (CargoEnum.pp, "Dr. José Francisco Vázquez Rodríguez",      "MORENA", False),
    (CargoEnum.pp, "C. Araceli Casasola Salazar",               "PRD-EM", False),

    # Representantes de Partidos — Suplentes
    (CargoEnum.pp, "Mtro. en D. Juan Mauro Granja Jiménez",     "PAN",    True),
    (CargoEnum.pp, "Mtra. Flora Martha Angón Paz",              "PRI",    True),
    (CargoEnum.pp, "Mtro. Guenady Hiaroslaf Montoya Orozco",    "PT",     True),
    (CargoEnum.pp, "Mtra. Paulina González Cuadros",            "PVEM",   True),
    (CargoEnum.pp, "C. José Antonio López Lozano",              "MC",     True),
    (CargoEnum.pp, "Lic. Israel Flores Hernández",              "MORENA", True),
    (CargoEnum.pp, "C. Luz del Carmen Bertha Huerta Mendoza",   "PRD-EM", True),
]


def run():
    init_db()
    db = SessionLocal()

    # Verificar si ya hay datos
    if db.query(Partido).count() > 0:
        print("⚠️  La base de datos ya tiene datos. Seed omitido.")
        db.close()
        return

    print("Insertando partidos...")
    partidos_map = {}
    for p in PARTIDOS:
        partido = Partido(nombre=p["nombre"], siglas=p["siglas"], activo=True)
        db.add(partido)
        db.flush()
        partidos_map[p["siglas"]] = partido.id
        print(f"  ✓ {p['siglas']} — {p['nombre']}")

    print("\nInsertando integrantes...")
    for cargo, nombre, siglas, es_suplente in INTEGRANTES:
        integrante = Integrante(nombre=nombre, cargo=cargo, activo=True)
        db.add(integrante)
        db.flush()

        partido_id = partidos_map.get(siglas) if siglas else None
        periodo = PeriodoIntegrante(
            integrante_id=integrante.id,
            partido_id=partido_id,
            fecha_inicio=FECHA_INICIO,
            fecha_fin=None,
        )
        db.add(periodo)
        sufijo = " (Suplente)" if es_suplente else ""
        print(f"  ✓ [{cargo.value}] {nombre}{sufijo}")

    db.commit()
    db.close()
    print("\n✅ Seed completado.")


if __name__ == "__main__":
    run()
