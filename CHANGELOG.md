# Changelog — TICaP Pipeline

Historial de versiones del pipeline de mapeo sistemático.  
Formato: [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/) · Versionado semántico.

---

## [Unreleased]

### Pendiente
- Módulo de análisis temático y síntesis cuantitativa sobre corpus incluido.
- Generación de diagrama PRISMA 2020 en formato visual (SVG/Mermaid).
- Gráficos de distribución de tecnologías y aplicaciones acuícolas.

---

## [1.0.0] — 2026-09-19

### Resumen
Versión estable y consolidada del pipeline completo sobre el corpus TICaP-509 (509 registros). Todas las fases ejecutadas, validadas y con 0 registros dudosos pendientes.

### Corpus final
- **509 registros** importados, normalizados y clasificados.
- **229 INCLUIR** | **261 EXCLUIR** | **18 DUPLICADO** | **1 TIPO_NO_ADMITIDO** | **0 DUDOSO**
- Abstracts: 383 existentes + 40 recuperados + 69 manuales (investigador) + 14 no encontrados.

### Pruebas
- 22/22 pruebas automatizadas pasan (`tests/test_pipeline.py` + `tests/test_workflow.py`).
- 17/17 validaciones de integridad del consolidador pasan.

### Publicado
- Repositorio disponible en GitHub: `Brokenearth/TICaP-Systematic-Mapping-Classification`.
- Commit baseline: `f5069dc`.

---

## [0.9.0] — 2026-08-15

### Resumen
Clasificación completa del corpus TICaP-509. Revisión manual de los 40 registros dudosos completada. TICAP-0236 reclasificado de INCLUIR a EXCLUIR por decisión humana (CE3).

### Cambios
- **Revisión manual completada:** 40 dudosos → 6 INCLUIR + 34 EXCLUIR.
- **Caso especial TICAP-0236:** Falso positivo del clasificador automático. Reclasificado a EXCLUIR (CE3) por el investigador.
- **Excel de trabajo enriquecido** (`TICaPAll_clasificacion_titulo_abstract.xlsx`) con abstracts manuales del investigador.

---

## [0.8.0] — 2026-08-09

### Resumen
Primera ejecución completa del pipeline sobre el corpus TICaP-509. Clasificación preliminar generada con 40 registros dudosos para revisión humana.

### Cambios
- **Fase 1–2:** Importación y normalización de 509 registros desde BibTeX.
- **Fase 3:** Detección y marcado de 18 duplicados (15 automáticos + 3 manuales).
- **Fases 4–5:** Recuperación de 40 abstracts faltantes vía APIs (Crossref, OpenAlex, Semantic Scholar).
- **Fase 6:** Base de clasificación cerrada con 509 registros.
- **Fases 7–9:** Clasificación heurística offline. 40 dudosos detectados (31 CE4, 9 CE5).

### Bugs corregidos
- **Parser BibTeX — paréntesis en abstracts:** El parser anterior corrompía la profundidad léxica cuando un abstract contenía enumeraciones `(i)`, `(ii)`, `(iii)`. Reescritura de `_split_top_level` en `pipeline_lib.py` para aislar campos por llaves `{...}` independientemente del balance de paréntesis. Registros afectados previamente: `TICAP-0007` y `TICAP-0062`.
- Protección activa: prueba unitaria `test_parses_fields_when_abstract_has_enumeration_parentheses`.

---

## [0.5.0] — 2026-07-27

### Resumen
Validación del pipeline con corpus piloto de 170 registros. Pipeline declarado estable y reproducible.

### Cambios
- **Corpus piloto:** 170 registros procesados de extremo a extremo.
- **Fases 1–11** completas y validadas sobre el corpus piloto.
- **31 casos dudosos** identificados en el piloto.
- Determinismo verificado mediante re-ejecución idéntica.
- Suite de pruebas automatizadas establecida.

### Arquitectura
- `scripts/pipeline_lib.py`: lógica pura de parsing, normalización, clasificación.
- `scripts/pipeline_steps.py`: orquestador de fases e I/O.
- `scripts/run_pipeline.py`: punto de entrada CLI.
- `tests/test_pipeline.py` + `tests/test_workflow.py`: pruebas unitarias e integración.

---

## [0.1.0] — 2026-07-27

### Resumen
Inicialización del proyecto. Definición de la estructura de directorios, criterios CE1–CE10 y primeras reglas metodológicas.

### Cambios
- Estructura de directorios establecida (`data/`, `scripts/`, `tests/`, `criteria/`, `logs/`, `output/`).
- `plan.md` con especificación metodológica de las 12 fases.
- Criterios CE1–CE10 formalizados en `criteria/catalogo_criterios.csv`.
- `.gitignore` configurado para excluir datos sensibles.
- Reglas de gobernanza en `.agents/rules/`.
