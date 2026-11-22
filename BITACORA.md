# Bitácora de Trazabilidad — TICaP Mapeo Sistemático

**Proyecto:** TICaP — Mapeo Sistemático de TIC aplicadas a Piscicultura (2020–2025)  
**Repositorio:** [Brokenearth/TICaP-Systematic-Mapping-Classification](https://github.com/Brokenearth/TICaP-Systematic-Mapping-Classification)  
**Corpus activo:** TICaP-509 (509 registros)  

---

> [!IMPORTANT]
> Este documento es la **bitácora oficial de trazabilidad** del proyecto. Registra de forma cronológica y auditada cada decisión, ejecución y evento significativo. No contiene datos bibliográficos del corpus ni información personal del investigador.

---

## Convenciones de registro

| Campo | Descripción |
|---|---|
| `Fecha` | ISO 8601 con zona horaria |
| `Sesión` | Identificador de sesión de trabajo (S-XXX) |
| `Fase` | Fase del pipeline metodológico |
| `Agente` | Quién ejecutó la acción: `PIPELINE`, `INVESTIGADOR`, `AGENTE_IA` |
| `Acción` | Descripción de la actividad realizada |
| `Artefactos` | Archivos creados, modificados o validados |
| `Resultado` | Conteos, hashes o métricas de verificación |
| `Observaciones` | Notas metodológicas, decisiones o excepciones |

---

## Registro de sesiones

### S-001 — Construcción del corpus piloto (170 registros)
**Periodo:** 2026-07-27  
**Fase:** Piloto — Corpus 170  
**Agente:** `PIPELINE` + `INVESTIGADOR`

| Timestamp (UTC) | Fase | Acción | Registros | Errores |
|---|---|---|---|---|
| 2026-07-27T22:35:22 | Fase 1 | Importación y asignación de IDs | 170 | 0 |
| 2026-07-27T22:35:22 | Fase 2 | Normalización | 170 → 168 modificados | 0 |
| 2026-07-27T22:36:01 | Fase 3 | Detección de duplicados | 170, 6 marcados | 0 |
| 2026-07-27T22:37:54 | Fases 4–5 | Recuperación y QA de abstracts | 170, 17 recuperados | 0 |
| 2026-07-27T22:38:47 | Fase 6 | Congelación de base de clasificación | 170, 162 aptos | 0 |
| 2026-07-27T22:39:26 | Fases 7–9 | Clasificación offline + variables | 170, 31 dudosos | 0 |
| 2026-07-27T22:40:09 | Fases 10–11 | Excel + PRISMA | 170 | 0 |

**Observaciones:**
- Corpus piloto de 170 registros para validación del pipeline.
- 31 casos pendientes de revisión manual al cierre de sesión.
- Pipeline validado estructuralmente en este corpus inicial.

---

### S-002 — Re-ejecución de validación del corpus piloto
**Periodo:** 2026-07-27 (tarde)  
**Agente:** `PIPELINE`

Re-ejecución completa del pipeline sobre los 170 registros para verificar reproducibilidad. Resultados idénticos. Se confirma determinismo del flujo.

---

### S-003 — Corpus completo TICaP-509: Importación y normalización
**Periodo:** 2026-08-09  
**Fase:** Fase 1–3 sobre corpus 509  
**Agente:** `PIPELINE`

| Timestamp (UTC) | Fase | Acción | Registros | Errores |
|---|---|---|---|---|
| 2026-08-09T21:17:26 | Fase 1 | Importación del BibTeX maestro (509 registros) | 509 | 0 |
| 2026-08-09T21:17:26 | Fase 2 | Normalización completa | 509 | 0 |
| 2026-08-09T21:17:41 | Fase 3 | Detección de duplicados | 509, 15 marcados, 4 a revisión | 0 |
| 2026-08-09T21:20:03 | Fases 4–5 | Recuperación de abstracts | 509, 40 recuperados, 85 a revisión | 0 |

**Artefactos generados:**
- `TICaP-509/data/interim/registros_importados.jsonl`
- `TICaP-509/data/interim/registros_normalizados.jsonl`
- `TICaP-509/data/interim/registros_con_duplicados.jsonl`
- `TICaP-509/data/master/TICaP_master.bib`

---

### S-004 — Clasificación preliminar y preparación de revisión manual
**Periodo:** 2026-08-09 (continuación)  
**Fase:** Fases 6–9  
**Agente:** `PIPELINE` + `INVESTIGADOR`

- Base de clasificación congelada con 509 registros.
- Clasificación heurística offline ejecutada sin conexión a Internet.
- **40 registros con estado `DUDOSO`:** 31 por CE4 (duda piscicultura/pesca), 9 por CE5 (duda TIC como aporte).
- Revisión manual preparada y entregada al investigador.

---

### S-005 — Revisión manual del investigador (40 dudosos)
**Periodo:** 2026-08-09 — 2026-09-19  
**Fase:** Fase 9 — Revisión humana  
**Agente:** `INVESTIGADOR`

**Resultados de la revisión humana:**

| Estado previo | Decisión final | Total |
|---|---|---|
| `DUDOSO` (CE4/CE5) | `INCLUIR` | 6 |
| `DUDOSO` (CE4/CE5) | `EXCLUIR` | 34 |
| `INCLUIR` (automático) → reclasificado | `EXCLUIR` (CE3) | 1 (*TICAP-0236*) |

**Evidencia:** Archivo de revisión humana (SHA-256 verificado — no publicado por contener datos del corpus).

**Caso especial documentado — TICAP-0236:**
- Clasificación automática inicial: `INCLUIR` (falso positivo por palabras clave incidentales).
- Decisión humana: `EXCLUIR` bajo CE3.
- Justificación: Estudio histológico sin TIC como aporte central.

---

### S-006 — Consolidación final del corpus TICaP-509
**Periodo:** 2026-09-19  
**Fase:** Consolidación + Validación de integridad  
**Agente:** `PIPELINE` + `INVESTIGADOR`

**Resultados finales oficiales:**

| Decisión | Total |
|---|---|
| `INCLUIR` | **229** |
| `EXCLUIR` | **261** |
| `DUDOSO` | **0** |
| `DUPLICADO` | **18** |
| `TIPO_NO_ADMITIDO` | **1** |
| **TOTAL** | **509** |

**Validaciones de integridad ejecutadas: 17/17 ✅**  
**Pruebas automatizadas: 22/22 ✅**

**Hashes de integridad (archivos inmutables):**
- BibTeX original `mendeley_original.bib`: `d26d1edba88e4c4046b3336f56fdb681a2ae14239dc354ab0d25bbc740b373eb`
- Espejo `TICaP-509All.bib`: hash idéntico al original ✅
- Excel de revisión manual: `36c65f3a543117c0aa19f4cc37c8c6e5d70987d230f8055a41ad72dc7448ecdc` ✅

**Conteos PRISMA verificados:**
- Registros iniciales: 509
- Duplicados: 18
- Fuera del periodo: 0
- Tipos no admitidos: 1
- Abstracts existentes: 383
- Abstracts recuperados: 40
- Abstracts no encontrados: 14
- Incluidos: 229
- Excluidos: 261
- Dudosos: 0

---

### S-007 — Inicialización de control de versiones Git y publicación en GitHub
**Periodo:** 2026-09-19  
**Fase:** Gestión de configuración  
**Agente:** `PIPELINE` + `INVESTIGADOR`

- Repositorio Git inicializado en la raíz del proyecto.
- `.gitignore` configurado para excluir datos sensibles, BibTeX, Excel, PDFs y JSONL.
- Commit inicial: `f5069dc — Baseline reproducible TICaP-509`
- Repositorio publicado en: `https://github.com/Brokenearth/TICaP-Systematic-Mapping-Classification`
- **Publicado (sin datos del corpus):** scripts, tests, criteria (CSV), prompts, .agents/rules, plan.md, README.md, PROJECT_STATE.md.

---

### S-008 — Sesión de trazabilidad, bitácora y sincronización inter-fases (2026-11-21)
**Periodo:** 2026-11-21T19:15 — 2026-11-21T19:35  
**Fase:** Gestión de trazabilidad y gobernanza multi-proyecto  
**Agente:** `AGENTE_IA` (Antigravity)

**Actividades ejecutadas:**
1. Auditoría del repositorio local y remoto GitHub de Fase 1.
2. Creación de la bitácora oficial de trazabilidad (`BITACORA.md`).
3. Creación de `CHANGELOG.md` documentando versiones v0.1.0 a v1.0.0.
4. Actualización del `README.md` con badges, resultados consolidados y estructura de gobernanza.
5. Inclusión de `scripts/export_zotero.py` en el repositorio público (sin datos sensibles).
6. **Establecimiento del puente de comunicación inter-proyecto (`PUENTE_FASES.md`):**
   - Se formalizó la separación entre Fase 1 (cribado y selección PRISMA, 509 registros) y Fase 2 (clasificación temática multidimensional de los 229 estudios incluidos, en repo separado `Brokenearth/TICaP-Thematic-Classification`).
   - Se definió el contrato de datos inmutable sobre `TICaP_Zotero_01_Incluidos_229.bib` (SHA-256 `3061574178b087d6a1d179eaaf37c52ea713e5b128868216d012faa864978a89`).
   - Se actualizaron las reglas de contexto (`.agents/rules/project-context.md`) para evitar invasión de alcances entre agentes.

**Artefactos publicados en GitHub:**
- Commit: `df6b058 — docs: bitácora, changelog y README mejorado — Fase 1 (cribado 509 registros)`

---

## Estado de la siguiente fase (Fase 2 — Repositorio independiente)

La siguiente etapa del estudio corresponde a la **Fase 2 (Clasificación temática)**, alojada en el repositorio independiente [`Brokenearth/TICaP-Thematic-Classification`](https://github.com/Brokenearth/TICaP-Thematic-Classification):
- [x] Base congelada de 229 registros creada.
- [x] Taxonomía y clasificación preliminar por palabras clave generada.
- [ ] Revisión humana del piloto (20 registros en `data/manual/piloto_para_revision.csv`).
- [ ] Revisión del 20% adicional de estudios.
- [ ] Cierre reproducible F7 y exportaciones finales.

---

## Regla de actualización de esta bitácora

Esta bitácora se actualiza **por sesión de trabajo**, registrando:
1. Qué fase o actividad se ejecutó.
2. Qué agente la ejecutó (PIPELINE / INVESTIGADOR / AGENTE_IA).
3. Qué artefactos fueron creados o modificados.
4. Qué métricas de verificación se obtuvieron.
5. Cualquier decisión metodológica adoptada.

> [!NOTE]
> Los datos del corpus (títulos, abstracts, decisiones individuales) **nunca se incluyen** en esta bitácora. Solo se registran métricas agregadas, hashes de integridad y trazas de ejecución.
