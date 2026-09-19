# PROJECT_STATE.md
**TICaP — Mapeo Sistemático de TIC aplicadas a Piscicultura**
_Estado verificado: 2026-09-19 | Última consolidación oficial: 2026-09-19_

---

## 1. Objetivo del proyecto

Mapeo sistemático de estudios de literatura científica sobre **Tecnologías de la Información y las Comunicaciones (TIC) aplicadas a la piscicultura y acuicultura productiva**, delimitado a la ventana temporal **2020–2025** (ambos años inclusive).

El objetivo es identificar, clasificar y sintetizar las tecnologías digitales (IoT, sensores, visión computacional, IA/ML, automatización, gemelos digitales, robótica submarina, plataformas de gestión, etc.) empleadas en el sector piscícola/acuícola para el monitoreo, control, alimentación y optimización de la producción acuícola.

El flujo metodológico produce:
- Una **matriz Excel oficial** con decisiones de inclusión/exclusión trazables y auditables.
- Un **BibTeX maestro** enriquecido con abstracts recuperados y validados.
- Los **conteos PRISMA** requeridos para el reporte de mapeo sistemático.

- **Tipos documentales admitidos:** `article` e `inproceedings`.
- **Criterios de pertinencia:** CE1–CE10 definidos en el documento oficial `CriteriosPertinencia-Título y Abstract.pdf`.

---

## 2. Estado actual

| Dimensión | Valor oficial |
|---|---|
| Corpus activo | **TICaP-509** |
| Registros reales verificados | **509** |
| Clasificación | **Final consolidada** |
| Revisión de dudosos | **Terminada** |
| DUDOSO | **0** |
| Validaciones de integridad | **17/17 correctas (0 fallos)** |
| Pruebas automatizadas del proyecto | **22/22 correctas (0 fallos)** |
| Control de versiones Git | **No inicializado** |

---

## 3. Arquitectura del proyecto

Estructura de directorios y componentes principales:

```
Metodologia Cursor Mapeo de estudios prueba/   ← Raíz del proyecto
│
├── TICaP-509/                  ← ENTORNO REPRODUCIBLE (Corpus 509)
│   ├── data/
│   │   ├── raw/                ← BibTeX original inmutable (mendeley_original.bib)
│   │   ├── interim/            ← Archivos intermedios del pipeline (JSONL, CSV)
│   │   ├── master/             ← BibTeX maestro enriquecido (TICaP_master.bib)
│   │   └── manual/             ← Decisiones y abstracts manuales
│   └── output/                 ← Salidas oficiales del corpus 509
│       ├── clasificacion/      ← clasificacion_preliminar.csv (CSV oficial consolidado)
│       ├── excel/              ← TICaP_clasificacion_titulo_abstract.xlsx (Excel oficial)
│       ├── excel completo/     ← Excel con abstracts manuales del investigador
│       ├── abstracts/          ← procedencia_abstracts.csv
│       ├── reportes/           ← resumen_prisma.csv y resumen_prisma.md
│       └── revision_manual/    ← casos_pendientes.xlsx (histórico)
│
├── TICaPALL/                   ← CARPETA DE ENTREGABLES (Espejo sincronizado)
│   ├── TICaP-509All.bib        ← Espejo del BibTeX original INMUTABLE
│   ├── masterall509.bib        ← Espejo del BibTeX maestro
│   ├── criteria/               ← Copia del PDF oficial de criterios
│   └── output/                 ← Espejo sincronizado de TICaP-509/output/
│
├── scripts/                    ← CÓDIGO DEL PIPELINE
│   ├── pipeline_lib.py         ← Lógica pura (parser BibTeX, normalizadores, clasificador)
│   ├── pipeline_steps.py       ← Orquestador de fases y manejo de I/O
│   ├── run_pipeline.py         ← Punto de entrada de línea de comandos (CLI)
│   ├── screening_reasons.py    ← Justificaciones manuales por ID (casos especiales)
│   └── README.md
│
├── tests/                      ← PRUEBAS AUTOMATIZADAS
│   ├── test_pipeline.py        ← Pruebas unitarias de funciones del pipeline (14 tests)
│   └── test_workflow.py        ← Pruebas de integración del flujo de trabajo (8 tests)
│
├── criteria/                   ← CRITERIOS DE PERTINENCIA
│   ├── CriteriosPertinencia-Título y Abstract.pdf  ← Documento oficial
│   ├── Criterios de Inclusión y Exclusión TICaP.md
│   └── catalogo_criterios_inclusion_exclusion.csv
│
├── logs/                       ← LOGS Y TRAZABILIDAD
│   ├── registro_actividades.csv← Historial de fases ejecutadas
│   └── manifiesto_archivos.csv ← Hashes SHA-256 de archivos críticos
│
├── output/                     ← OUTPUTS GENERALES Y REVISIÓN MANUAL
│   ├── revision_manual/        ← TICaPAll_revision_final_manual 3_09_26 (1).xlsx (EVIDENCIA HUMANA)
│   └── (otros outputs)         ← Salidas del corpus piloto de 170 registros
│
├── data/                       ← Corpus piloto de 170 registros (histórico)
├── prompts/                    ← Prompts de clasificación temática
├── plan.md                     ← Especificación metodológica general
├── TICaP-509/plan.md           ← Plan específico del corpus 509
└── PROJECT_STATE.md            ← Memoria persistente oficial del proyecto
```

**Distinción funcional clara:**
- **Entorno reproducible TICaP-509:** Espacio autónomo de ejecución del pipeline donde se procesan los datos desde `raw` hasta `output`.
- **Carpeta de entregables TICaPALL:** Concentrador final para distribución, sincronizado con las salidas de `TICaP-509`.
- **Scripts:** Biblioteca compartida e independiente de la raíz de datos.
- **Revisión manual:** Almacena la evidencia histórica documental aportada directamente por el investigador.
- **Historial de Cursor:** Recurso local opcional no versionado en el repositorio y no necesario para operar el proyecto; `PROJECT_STATE.md` y las reglas en `.agents/rules/` constituyen las fuentes persistentes normales de contexto.

---

## 4. Stack tecnológico

El entorno utiliza exclusivamente componentes confirmados en el repositorio:

| Componente | Tecnología verificada | Observación |
|---|---|---|
| Lenguaje | **Python 3.12.10** | Entorno estándar |
| Manipulación de Excel | **openpyxl 3.1.5** | Única dependencia externa requerida (`requirements.txt`) |
| Formato de datos tabulares | **CSV** | Estándar RFC 4180 con `utf-8-sig` para compatibilidad con Excel |
| Formato bibliográfico | **BibTeX** | Parser propio robusto implementado en `scripts/pipeline_lib.py` |
| Intercambio estructurado | **JSONL** | Registros intermedios entre fases |
| Documentación y reportes | **Markdown (.md)** | GitHub Flavored Markdown |
| Hojas de cálculo | **Microsoft Excel (.xlsx)** | Formato oficial para revisión y entrega |
| Pruebas automatizadas | **unittest** | Biblioteca estándar de Python |
| Red / Recuperación web | **urllib** | Biblioteca estándar de Python (sin dependencia de `requests`) |
| Control de versiones | **Ninguno (No Git)** | Verificado: no existe carpeta `.git` |

---

## 5. Archivos oficiales

### Inmutables (NO modificar bajo ninguna circunstancia)

| Ruta | Función | Tipo | Estado |
|---|---|---|---|
| `TICaP-509/data/raw/mendeley_original.bib` | BibTeX original exportado de Mendeley con los 509 registros. Hash SHA-256: `d26d1edba88e4c4046b3336f56fdb681a2ae14239dc354ab0d25bbc740b373eb` | Entrada | Inmutable |
| `TICaPALL/TICaP-509All.bib` | Espejo del BibTeX original en la carpeta de entregables. Hash idéntico al original. | Entrada / Espejo | Inmutable |
| `output/revision_manual/TICaPAll_revision_final_manual 3_09_26 (1).xlsx` | **Evidencia histórica documental de la revisión humana.** Contiene las columnas `Decisión Inicial` y `Decisión Final` del investigador. Fuente primaria de las decisiones humanas sobre dudosos y TICAP-0236. | Revisión manual | Inmutable (NO sobrescribir) |
| `CriteriosPertinencia-Título y Abstract.pdf` | Documento oficial rector de los criterios CE1–CE10. | Criterios | Inmutable |

### Modificables / Generados por el pipeline y consolidación

| Ruta | Función | Tipo | Modificable |
|---|---|---|---|
| `TICaP-509/data/master/TICaP_master.bib` | BibTeX maestro enriquecido con abstracts recuperados. Solo almacena campos bibliográficos y de abstract; por diseño no contiene campos de decisión/criterio. | Salida | Sí (vía pipeline) |
| `TICaPALL/masterall509.bib` | Espejo del BibTeX maestro en entregables. | Salida / Espejo | Sí (vía sincronización) |
| `TICaP-509/output/clasificacion/clasificacion_preliminar.csv` | **Fuente de verdad oficial de la clasificación.** Estado final consolidado de los 509 registros. | Salida oficial | Sí (vía consolidación) |
| `TICaP-509/output/excel/TICaP_clasificacion_titulo_abstract.xlsx` | Excel oficial de clasificación con las 10 columnas oficiales. | Salida oficial | Sí (vía exportador) |
| `TICaP-509/output/excel completo/TICaPAll_clasificacion_titulo_abstract.xlsx` | Excel de trabajo enriquecido con abstracts manuales del investigador y recomendaciones preliminares. | Intermedio / Trabajo | Sí |
| `TICaP-509/output/reportes/resumen_prisma.csv` | Resumen de conteos de flujo PRISMA en formato CSV. | Salida oficial | Sí (vía reporte PRISMA) |
| `TICaP-509/output/reportes/resumen_prisma.md` | Resumen de conteos de flujo PRISMA en formato Markdown. | Salida oficial | Sí (vía reporte PRISMA) |
| `TICaP-509/data/interim/registros_importados.jsonl` | Registros crudos importados con ID asignado (Fase 1). | Intermedio | Sí |
| `TICaP-509/data/interim/registros_normalizados.jsonl` | Registros con campos limpios y normalizados (Fase 2). | Intermedio | Sí |
| `TICaP-509/data/interim/registros_con_duplicados.jsonl` | Registros con marcas de duplicación (Fase 3). | Intermedio | Sí |
| `TICaP-509/data/interim/registros_con_abstracts.jsonl` | Registros con abstracts recuperados e integrados (Fase 4–5). | Intermedio | Sí |
| `TICaP-509/data/interim/base_clasificacion.csv` | Base previa a la ejecución del clasificador temático (Fase 6). | Intermedio | Sí |
| `TICaP-509/output/abstracts/procedencia_abstracts.csv` | Auditoría de procedencia y estado de cada abstract. | Salida | Sí |
| `logs/registro_actividades.csv` | Bitácora cronológica de ejecuciones de fases. | Log | Sí (append-only) |
| `logs/manifiesto_archivos.csv` | Hashes de verificación de integridad. | Log | Sí (actualizable) |

#### Estructura de columnas oficiales del Excel (10 columnas):
`ID | Título | Abstract | Decisión | Criterio aplicado | Justificación breve | Tecnología identificada | Aplicación acuícola/piscícola | Categoría temática | Observación`

---

## 6. Pipeline

El pipeline de screening sistemático se ejecuta de forma reproducible por fases:

```powershell
python -m scripts.run_pipeline --root "TICaP-509"
```

### Fases reales del flujo:

1. **Importación (`run_import`):** Lectura del BibTeX original con parser propio. Extrae campos bibliográficos respetando caracteres especiales y llaves anidadas.
2. **Normalización (`run_normalization`):** Limpieza de títulos, normalización de autores, validación de año (2020–2025) y tipo documental (`article`, `inproceedings`).
3. **IDs estables (asignados en Fase 1):** Asignación secuencial determinista `TICAP-0001` a `TICAP-0509` en el orden de aparición en el `.bib` original. Los IDs nunca se alteran.
4. **Detección de duplicados (`run_duplicates`):** Detección jerárquica: DOI idéntico → Título normalizado idéntico → Similitud léxica alta + año + autores.
5. **Recuperación de abstracts (`run_abstract_recovery`):** Búsqueda progresiva en fuentes externas por APIs y metadatos web vía `urllib`.
6. **Control de calidad (`validate_abstract_candidate`):** Validación cruzada obligatoria de coincidencia de título, DOI, año y autor para cualquier abstract externo.
7. **Clasificación preliminar (`run_classification_offline`):** Evaluación heurística determinista basada en reglas de inclusión/exclusión según palabras clave temáticas y criterios CE1–CE10.
8. **Identificación de variables (subfase de clasificación):** Extracción de tecnología digital, aplicación piscícola y categoría temática.
9. **Revisión manual:** Contrastación y enriquecimiento de abstracts y casos dudosos por el investigador humano.
10. **Consolidación:** Aplicación de las decisiones finales del investigador humano (`output/revision_manual/...`) sobre los casos dudosos y falsos positivos al CSV oficial.
11. **Excel (`run_export`):** Generación del libro `.xlsx` oficial formateado con anchos de columna, cabeceras y estilos.
12. **PRISMA (`update_prisma`):** Cálculo y generación de métricas de flujo PRISMA en CSV y Markdown.
13. **Publicación/Sincronización en TICaPALL (`publish_ticapall`):** Copia exacta y validación de hash de los entregables oficiales en `TICaPALL/`.

---

## 7. Decisiones metodológicas permanentes

Estas decisiones son pilares metodológicos del proyecto y no deben modificarse:

1. **No modificar el BibTeX original:** `mendeley_original.bib` y `TICaP-509All.bib` son de solo lectura; representan el estado primario de la búsqueda.
2. **No borrar registros:** Ningún registro se elimina físicamente. Los duplicados se marcan `DUPLICADO` y se conservan para auditoría completa.
3. **Mantener trazabilidad:** Toda decisión, cambio de estado y origen de abstract debe ser explicable por su procedencia y registros de log.
4. **Mantener IDs `TICAP-XXXX`:** Los identificadores asignados son permanentes e inmutables en todas las fases y entregables.
5. **Separar recuperación de abstracts y clasificación:** La conexión a Internet y uso de APIs está estrictamente restringido a la recuperación de abstracts.
6. **No usar Internet durante la clasificación temática:** La clasificación temática se ejecuta 100% offline basándose únicamente en los datos contenidos en el registro.
7. **No excluir sin criterio:** Todo registro con decisión `EXCLUIR` debe tener asociado un código oficial de exclusión (CE1 a CE10).
8. **No inventar datos:** Prohibido inferir, rellenar, traducir o asumir datos bibliográficos o de resumen no sustentados en la evidencia documental.
9. **Unicidad de entregables maestros:** Un único BibTeX maestro enriquecido y un único Excel oficial de clasificación.
10. **Independencia de dependencias pesadas:** Uso exclusivo de biblioteca estándar de Python y `openpyxl`.

---

## 8. Reglas de abstracts

Directrices estrictas para el tratamiento de resúmenes:

- **No generar abstracts:** Prohibido el uso de IA generativa o paráfrasis para crear resúmenes sintéticos.
- **No completar frases:** Si un abstract en la fuente está truncado o incompleto, se conserva en su estado real.
- **No combinar textos:** Prohibido fusionar fragmentos de distintas bases de datos para armar un abstract compuesto.
- **No sustituir abstracts por resúmenes propios:** Las notas del investigador van en la columna `Observación`, nunca sustituyendo el campo `Abstract`.
- **Mantener procedencia:** Todo abstract lleva su etiqueta de procedencia en `procedencia_abstracts.csv` (`EXISTENTE_BIBTEX`, `RECUPERADO`, `MANUAL_INVESTIGADOR`, etc.).
- **Validar coincidencia:** Verificación obligatoria de título, DOI, año y autor antes de aceptar cualquier abstract recuperado de servicios externos.

---

## 9. Clasificación

### Información permitida durante la clasificación temática
La clasificación offline opera exclusivamente sobre:
- ID del registro (`TICAP-XXXX`)
- Título
- Abstract
- Año de publicación
- Tipo documental (`article`, `inproceedings`)
- Criterios oficiales de pertinencia CE1–CE10

### Valores oficiales de decisión

| Decisión | Definición |
|---|---|
| `INCLUIR` | Cumple pertinencia temática completa (TIC aplicada a piscicultura/acuicultura productiva 2020–2025). |
| `EXCLUIR` | Aplica formalmente al menos un criterio de exclusión CE1–CE10. |
| `DUDOSO` | Evidencia insuficiente o ambigua en título/abstract. **Actualmente = 0**, pero se mantiene como valor formal del sistema para cualquier corrida o corpus futuro. |
| `DUPLICADO` | Registro duplicado secundario (el registro principal se evalúa independientemente). |
| `FUERA_DE_PERIODO` | Año fuera del rango 2020–2025. |
| `TIPO_NO_ADMITIDO` | Documento de tipo distinto a `article` o `inproceedings` (ej. libros, tesis no clasificadas). |

---

## 10. Revisión humana

Trazabilidad de la resolución de registros dudosos:

```
Clasificación automática inicial
    ↓
40 DUDOSO (31 por CE4 [duda piscicultura/pesca] y 9 por CE5 [duda TIC como aporte])
    ↓
Revisión humana del investigador
(Archivo de evidencia: output/revision_manual/TICaPAll_revision_final_manual 3_09_26 (1).xlsx)
    ↓
6 INCLUIR  +  34 EXCLUIR
    ↓
0 DUDOSO restantes
```

### Regla permanente sobre etiquetas intermedias:
Las etiquetas generadas en fases intermedias:
- `Dudoso (incluir)`
- `Dudoso (excluir)`

eran **estados/recomendaciones de revisión previa para el investigador**, y **NO deben convertirse automáticamente en decisiones oficiales por el pipeline**. La decisión canónica definitiva fue establecida por la revisión humana en la columna `Decisión Final` del archivo de revisión.

---

## 11. TICAP-0236

Registro de caso especial resuelto:

| Atributo | Detalle |
|---|---|
| ID | `TICAP-0236` |
| Título | *Histological description of the digestive tract of commercially produced pirarucu (Arapaima gigas)* |
| Decisión final | **EXCLUIR** |
| Criterio aplicado | **CE3** |
| Procedencia | **Decisión humana del investigador** |
| Justificación | `INV: El abstract corresponde a una descripción histológica del tracto digestivo de pirarucú de producción comercial. No presenta TIC como aporte central. El INCLUIR automático fue un falso positivo de palabras clave (software/monitoreo). Decisión humana confirmada: CE3.` |
| Historial | Inicialmente clasificado como `INCLUIR` por el clasificador automático debido a la presencia incidental de términos técnicos. Identificado por el investigador como falso positivo evidente y reclasificado a `EXCLUIR` bajo CE3. |

---

## 12. Gestión de duplicados

### Lógica del pipeline:
1. **Detección por DOI idéntico:** Confirmación automática de duplicación.
2. **Detección por título normalizado idéntico:** Confirmación automática.
3. **Detección por similitud alta:** Pasa a revisión o regla manual documentada.
4. **Conservación:** El registro con mayor completitud (abstract, DOI, metadatos) se conserva como principal; el secundario se marca `DUPLICADO`. Los duplicados **no se eliminan físicamente** para preservar la integridad del conteo original (509).

### Casos históricos importantes:
- **`TICAP-0254` / `TICAP-0172`:** `TICAP-0254` (tesis en español de 2022) corresponde al trabajo previo del artículo de revista internacional en inglés `TICAP-0172` (2023, *Journal of Supercomputing*). Se conservó `TICAP-0172` como principal y `TICAP-0254` quedó marcado como `DUPLICADO` vía `MANUAL_DUPLICATE_OF`.
- **`TICAP-0440` / `TICAP-0475`:** Registros con títulos prácticamente idénticos. `TICAP-0440` tenía nota manual de duplicado y menor completitud; `TICAP-0475` tenía abstract completo y quedó como principal.
- **`TICAP-0410`:** Marcado como `DUPLICADO` a partir de verificación manual de contenido redundante.

---

## 13. Bugs históricos solucionados

### Parser BibTeX: manejo de paréntesis dentro de abstracts
- **Problema detectado:** El parser original utilizaba el conteo de profundidad de paréntesis ordinarios como condición de corte en la segmentación de campos BibTeX. Cuando un abstract contenía enumeraciones textuales como `(i)`, `(ii)`, `(iii)` o aclaraciones tipo `(WOS)`, se corrompía la profundidad léxica, absorbiendo los campos subsiguientes (`title`, `year`, `author`) dentro del cuerpo del abstract. Esto provocaba que el título quedara vacío y el año sin detectar, asignando erróneamente `FUERA_DE_PERIODO`.
- **Registros afectados:** `TICAP-0007` (*Gmez2023*) y `TICAP-0062` (*Li2022*).
- **Solución implementada:** Se reescribió `_split_top_level` en `scripts/pipeline_lib.py` para aislar campos delimitados por llaves `{...}` o comillas `"..."`, independizando completamente el balance de paréntesis en el contenido del abstract.
- **Protección activa:** Prueba unitaria `test_parses_fields_when_abstract_has_enumeration_parentheses` en `tests/test_pipeline.py`.

---

## 14. Resultados finales oficiales

Resultados consolidados oficiales verificados al 2026-09-19 en `TICaP-509/output/clasificacion/clasificacion_preliminar.csv`, `TICaP_clasificacion_titulo_abstract.xlsx`, `resumen_prisma.csv` y sus espejos en `TICaPALL`:

| Decisión | Total |
|---|---|
| **INCLUIR** | **229** |
| **EXCLUIR** | **261** |
| **DUDOSO** | **0** |
| **DUPLICADO** | **18** |
| **TIPO_NO_ADMITIDO** | **1** |
| **TOTAL** | **509** |

---

## 15. Pruebas y validaciones

Estado de verificación automatizada del proyecto:

- **17/17 validaciones de consolidación correctas (0 fallos):**
  1. Total de registros = 509
  2. Unicidad de IDs (509 IDs únicos TICAP-0001 a TICAP-0509)
  3. Total INCLUIR = 229
  4. Total EXCLUIR = 261
  5. Total DUDOSO = 0
  6. Total DUPLICADO = 18
  7. Total TIPO_NO_ADMITIDO = 1
  8. TICAP-0236 confirmado EXCLUIR
  9. TICAP-0236 criterio CE3
  10. 6 ex-dudosos confirmados en INCLUIR
  11. 34 ex-dudosos confirmados en EXCLUIR
  12. Excel de revisión manual intacto (hash SHA-256 inalterado)
  13. BibTeX original `TICaP-509` intacto
  14. BibTeX original espejo `TICaPALL` intacto
  15. Archivos de `TICaPALL/output/` sincronizados (hash idéntico)
  16. Excel oficial generado con 509 filas y 10 columnas
  17. PRISMA CSV y MD coincidentes con los conteos consolidados

- **22/22 pruebas automatizadas del proyecto correctas (`tests/`):**
  - `tests/test_pipeline.py`: 14 pruebas unitarias passed.
  - `tests/test_workflow.py`: 8 pruebas de integración passed.
  - Tiempo de ejecución: ~0.23 s.
  - 0 fallos, 0 errores.
  - **No fue necesario modificar código para hacerlas pasar.**

---

## 16. Integridad

Garantías de integridad verificadas:

1. **BibTeX originales idénticos:** `TICaP-509/data/raw/mendeley_original.bib` y `TICaPALL/TICaP-509All.bib` tienen exactamente el mismo hash SHA-256 (`d26d1edba88e4c4046b3336f56fdb681a2ae14239dc354ab0d25bbc740b373eb`). No sufrieron ninguna alteración.
2. **Excel de revisión humana intacto:** `output/revision_manual/TICaPAll_revision_final_manual 3_09_26 (1).xlsx` conserva su hash SHA-256 íntegro (`36c65f3a543117c0aa19f4cc37c8c6e5d70987d230f8055a41ad72dc7448ecdc`).
3. **Entregables sincronizados en TICaPALL:** Todos los archivos publicados en `TICaPALL/output/` son réplicas exactas con verificación de hash respecto a `TICaP-509/output/`.
4. **BibTeX maestro puro:** `TICaP_master.bib` y `masterall509.bib` contienen exclusivamente campos bibliográficos y resúmenes; por diseño metodológico no se han inyectado campos de decisión, criterio o justificación en los archivos BibTeX.

---

## 17. Trabajo terminado

Fases e hitos formalmente completados:

- [x] Construcción y estabilización del pipeline automatizado modular (scripts en `scripts/`).
- [x] Depuración y protección del parser BibTeX (soporte para caracteres y paréntesis en abstracts).
- [x] Consolidación del corpus activo completo de 509 registros (`TICaP-509`).
- [x] Recuperación y validación cruzada de abstracts faltantes (383 originales + 40 recuperados + 69 completados manualmente).
- [x] Detección y marcado trazable de 18 duplicados y 1 tipo no admitido.
- [x] Clasificación preliminar de screening por título y abstract.
- [x] Revisión manual de los 40 registros dudosos completada por el investigador.
- [x] Resolución documentada de los 40 dudosos (6 INCLUIR, 34 EXCLUIR).
- [x] Resolución documentada de TICAP-0236 (falso positivo reclasificado a EXCLUIR por CE3).
- [x] Clasificación final consolidada: 229 INCLUIR, 261 EXCLUIR, 0 DUDOSO, 18 DUPLICADO, 1 TIPO_NO_ADMITIDO.
- [x] Actualización de reportes PRISMA (Markdown y CSV).
- [x] Sincronización completa de la carpeta de entregables `TICaPALL`.
- [x] Ejecución y superación de las 17 validaciones de integridad.
- [x] Ejecución y superación de las 22 pruebas automatizadas sin fallos.

---

## 18. Trabajo pendiente

Clasificación de actividades pendientes estrictamente verificables a partir del objetivo del mapeo y los artefactos existentes:

### A. Mantenimiento del pipeline
- El pipeline se encuentra estable y completo para el corpus 509. Solo requeriría mantenimiento si en el futuro se amplía la ventana de años o se añade una nueva fuente bibliográfica.
- Inicialización formal del repositorio Git para el seguimiento de versiones (actualmente no existe `.git`).

### B. Análisis temático posterior (sobre el corpus de 229 INCLUIR)
- Tabulación agregada de frecuencias y cruces multidimensionales a partir de las columnas ya extraídas en el Excel:
  - `Categoría temática` (ej. monitoreo de calidad de agua, conteo de biomasa, alimentación automatizada, etc.).
  - `Tecnología identificada` (IoT, Visión artificial, Redes Neuronales/Deep Learning, Sensores acústicos, etc.).
  - `Aplicación acuícola/piscícola` (monitoreo ambiental, detección de enfermedades, control de crecimiento).
- Análisis de evolución temporal por año de publicación (2020 a 2025).

### C. Producción de tablas y gráficos
- Generación del diagrama de flujo PRISMA en formato visual estructurado (SVG/PNG o Mermaid) para inclusión en manuscrito.
- Construcción de gráficos de distribución de tecnologías y aplicaciones.

### D. Redacción del informe / artículo científico
- Redacción de la sección metodológica del mapeo sistemático basada en los criterios CE1–CE10 y el flujo reproducible documentado.
- Redacción de resultados y discusión basados en la síntesis de los 229 estudios incluidos.

---

## 19. Próximo paso

Habiendo finalizado formalmente la consolidación de clasificación, la recuperación de abstracts y la resolución de todos los registros dudosos (DUDOSO = 0) y de TICAP-0236, el siguiente paso metodológico inmediato es:

**Iniciar el análisis temático y síntesis cuantitativa sobre los 229 registros con decisión INCLUIR:**
1. Extraer y consolidar la matriz de frecuencias por `Categoría temática`, `Tecnología identificada` y `Aplicación acuícola/piscícola` contenidas en `TICaP-509/output/excel/TICaP_clasificacion_titulo_abstract.xlsx`.
2. Generar el diagrama visual PRISMA 2020 a partir de los datos finales (`resumen_prisma.csv`).

---

## 20. Regla de actualización

Este documento `PROJECT_STATE.md` constituye la **memoria persistente oficial** del proyecto y debe actualizarse únicamente cuando ocurra un cambio sustancial en:
- Los conteos oficiales de clasificación (`INCLUIR`, `EXCLUIR`, `DUDOSO`, etc.).
- La definición o número de registros del corpus activo.
- La arquitectura de directorios o reubicación de carpetas principales.
- La lista o función de los archivos oficiales e inmutables.
- Las fases, algoritmos o dependencias del pipeline.
- Los criterios de pertinencia CE.
- El estado de terminación de las fases del proyecto.

---
_Fin del documento oficial de estado._
