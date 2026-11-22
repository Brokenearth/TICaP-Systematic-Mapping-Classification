# TICaP — Mapeo Sistemático de TIC aplicadas a Piscicultura (2020–2025)

Pipeline reproducible y trazable para el **mapeo sistemático de literatura científica** sobre Tecnologías de la Información y las Comunicaciones (TIC) aplicadas a la piscicultura y acuicultura productiva (ventana temporal: 2020–2025).

[![Tests](https://img.shields.io/badge/tests-22%2F22%20passed-brightgreen)](#pruebas-automatizadas)
[![Corpus](https://img.shields.io/badge/corpus-509%20registros-blue)](#resultados)
[![Incluidos](https://img.shields.io/badge/incluidos-229-green)](#resultados)
[![Excluidos](https://img.shields.io/badge/excluidos-261-red)](#resultados)
[![Estado](https://img.shields.io/badge/estado-consolidado-brightgreen)](#estado-actual)

---

## Descripción

Este repositorio contiene:
- **Pipeline modular** de procesamiento y normalización bibliográfica (Fases 1–12).
- **Metodología y reglas** de clasificación temática por título y abstract (criterios CE1–CE10).
- **Catálogo formal** de criterios de inclusión y exclusión.
- **Prompts versionados** para el cribado temático offline.
- **Suite de pruebas** automatizadas unitarias y de integración (22 tests).
- **Reglas de gobernanza** de datos, integridad y reproducibilidad.
- **Bitácora de trazabilidad** con el historial completo de sesiones y decisiones.
- **Memoria persistente** del proyecto con estado, arquitectura y decisiones metodológicas.

> **Nota sobre los datos:** Los datasets bibliográficos, abstracts, hojas Excel de clasificación, archivos BibTeX, resultados detallados y documentos de revisión humana **no se incluyen** en el repositorio por razones de integridad, privacidad y gestión responsable de datos de investigación.

---

## Resultados

Clasificación final consolidada (verificada al 2026-09-19):

| Decisión | Total |
|---|---|
| ✅ INCLUIR | **229** |
| ❌ EXCLUIR | **261** |
| 🔄 DUPLICADO | **18** |
| ⛔ TIPO_NO_ADMITIDO | **1** |
| ❓ DUDOSO | **0** |
| **TOTAL** | **509** |

**Conteos PRISMA:**
- Registros iniciales: 509 · Duplicados: 18 · Abstracts recuperados: 40 · No encontrados: 14

---

## Requisitos e Instalación

Entorno estándar recomendado: **Python 3.10+** (verificado en Python 3.12). Sin dependencias de red requeridas para el pipeline de clasificación.

```bash
pip install -r requirements.txt
```

---

## Pruebas automatizadas

El proyecto incluye pruebas unitarias y de integración que validan el parser BibTeX, la normalización, la detección de duplicados y la consistencia del flujo de trabajo:

```bash
python -m unittest discover -s tests -v
```

**Estado:** 22/22 pruebas pasan · 0 fallos · ~0.23 s de ejecución.

---

## Pipeline (Fases)

```
Fase 1: Importación BibTeX → IDs estables TICAP-0001 … TICAP-0509
Fase 2: Normalización (títulos, autores, DOI, año, tipo)
Fase 3: Detección de duplicados (DOI → título → similitud léxica)
Fases 4–5: Recuperación y control de calidad de abstracts (Crossref, OpenAlex, Semantic Scholar)
Fase 6: Congelación de base de clasificación
Fases 7–9: Clasificación offline CE1–CE10 + variables temáticas
Fase 9: Revisión manual (investigador)
Fase 10: Consolidación de decisiones finales
Fase 11: Generación del Excel oficial (10 columnas)
Fase 12: Cálculo de métricas PRISMA
```

```bash
python -m scripts.run_pipeline --root "TICaP-509"
```

---

## Estructura general

```
├── scripts/          # Pipeline modular (parser, normalizador, clasificador, exportador Zotero)
├── tests/            # 22 pruebas automatizadas (unitarias + integración)
├── criteria/         # Criterios CE1–CE10 en CSV y PDF oficial
├── prompts/          # Instrucciones versionadas para clasificación offline
├── .agents/rules/    # Reglas de gobernanza para agentes IA
├── BITACORA.md       # Bitácora oficial de trazabilidad por sesión
├── CHANGELOG.md      # Historial de versiones del pipeline
├── plan.md           # Especificación metodológica de las 12 fases
└── PROJECT_STATE.md  # Memoria persistente oficial del proyecto
```

---

## Trazabilidad

Este proyecto mantiene trazabilidad completa mediante:
- **`BITACORA.md`**: Registro cronológico por sesión de trabajo con métricas y hashes.
- **`CHANGELOG.md`**: Historial semántico de versiones del pipeline.
- **`logs/registro_actividades.csv`**: Log máquina de cada ejecución de fase (no publicado — contiene rutas locales).
- **`logs/manifiesto_archivos.csv`**: Hashes SHA-256 de archivos críticos (no publicado).
- **Hashes SHA-256** de archivos inmutables documentados en `PROJECT_STATE.md`.

---

## Estado actual

- ✅ **Pipeline:** Flujo modular estabilizado, reproducible y validado.
- ✅ **Clasificación:** Cribado completado — 0 dudosos pendientes.
- ✅ **Tests:** 22/22 pruebas automatizadas pasan.
- ✅ **Integridad:** 17/17 validaciones de consolidación pasan.
- 🔄 **Siguiente fase:** Análisis temático y síntesis cuantitativa sobre los 229 estudios incluidos.
