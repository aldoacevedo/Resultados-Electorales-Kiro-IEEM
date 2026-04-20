# Contexto del Proyecto — Sistema de Consulta Electoral IEEM

## Descripción
App web de consulta y análisis de resultados electorales de la elección de Gobernador
del Estado de México en 2005, 2011, 2017 y 2023.

**Stack:** Python · Streamlit · Plotly · Pandas · GeoPandas

**Para correr la app:**
```bash
python -m streamlit run app.py
```

---

## Estructura del proyecto

```
├── app.py                          # App principal Streamlit
├── requirements.txt
├── Pendientes.md                   # Pendientes técnicos
├── CONTEXTO.md                     # Este archivo
├── data/
│   ├── loader.py                   # Carga y normaliza los 4 Excel electorales
│   └── geo_loader.py               # Carga shapefiles y hace join con datos electorales
├── charts/
│   └── plots.py                    # Todas las visualizaciones Plotly
├── assets/
│   └── README.txt                  # Colocar logo_ieem.png aquí para mostrarlo en header
├── Datos de excel/                 # Archivos fuente Excel
│   ├── computo_dttal_2005dg.xls
│   ├── Computo_FINAL_GOB_2011.xls
│   ├── Res_Definitivos_Gobernador_2017_por_DistritoLocal.xlsx
│   └── RESULTADOS DEFINITIVOS GUBERNATURA 2023 POR DISTRITO LOCAL.xlsx
└── SHP_DL_SECC_2005_2023/          # Shapefiles por año
    ├── SHP_2005/dttoloc.shp        # Distritos locales 2005
    ├── SHP_2011/dttoloc.shp        # Distritos locales 2011
    ├── SHP_2017/DISTRITO_LOCAL.shp # Distritos locales 2017
    └── SHP_2023/DISTRITO_LOCAL1.shp# Distritos locales 2023
```

---

## Fuerzas políticas por año

| Año | Fuerzas |
|-----|---------|
| 2005 | PAN - Convergencia · Alianza por México (PRI+PVEM) · Unidos para Ganar (PRD+PT) |
| 2011 | PAN · Unidos por Ti (PRI+PVEM+NA) · Unidos Podemos Más (PRD+PT+Conv+MC) |
| 2017 | PAN · Alianza PRI (PRI+PVEM+NVA_ALIANZA+ES y combinaciones) · MORENA · PRD · PT · Candidato Independiente |
| 2023 | Fuerza y Corazón por el Edo. de Méx (PAN+PRI+PRD+NAEM y combinaciones) · Sigamos Haciendo Historia (PVEM+PT+MORENA) |

**Regla de agrupación:** Los votos de candidaturas comunes y combinaciones de partidos
se suman a la coalición o bloque correspondiente.

---

## Estructura de datos normalizados (loader.py)

Cada año produce un DataFrame con estas columnas:
- `distrito` — nombre con prefijo numérico: `"01 - NOMBRE"` (2005 con romano: `"01 - I - TOLUCA"`)
- `lista_nominal`
- [columnas por fuerza política según el año]
- `No Registrados`
- `votos_validos`, `votos_nulos`, `total_votos`
- `participacion` (0 a 1), `abstencion` (0 a 1)
- `anio`

---

## Distritación

- **2005 y 2011:** misma distritación, 45 distritos con numerales romanos (I–XLV)
- **2017:** nueva distritación, 45 distritos con nombre de cabecera
- **2023:** nueva distritación, 45 distritos con nombre de cabecera

Los shapefiles están en CRS EPSG:26714 (2005/2011) y EPSG:32614 (2017/2023).
`geo_loader.py` los convierte a WGS84 (EPSG:4326) automáticamente.

**Join shapefile ↔ datos electorales:** por número de distrito (`num_distrito`).
- 2005/2011: campo `DL` en el shapefile
- 2017/2023: campo `DISTRITO_L` en el shapefile

---

## Paleta de colores IEEM

```python
IEEM_MAGENTA = "#e91e8c"   # acento principal
IEEM_SIDEBAR = "#f0f0f0"   # fondo sidebar
IEEM_TEXT    = "#222222"   # texto
IEEM_MUTED   = "#666666"   # texto secundario
```

---

## Secciones de la app

1. **Resultados por año** — barras, pie, por distrito (con filtro estatal/distrito)
2. **Comparativo histórico** — fuerzas por año, participación/abstención, evolución multifuerza
3. **Mapa por distrito** — coroplético interactivo con shapefiles reales del IEEM
4. **Tablas** — resultados por distrito descargables en CSV

---

## Pendientes

Ver archivo `Pendientes.md` para detalle. Resumen:
- Distritos V y VII de 2011 sin datos electorales (aparecen sin color en el mapa)
- Logo oficial del IEEM: colocar PNG en `assets/logo_ieem.png`
