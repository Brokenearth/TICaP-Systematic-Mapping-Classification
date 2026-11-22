# Contexto del Proyecto y Principios de Trabajo

Este repositorio contiene el flujo de trabajo reproducible del proyecto **TICaP** (*Tecnologías de la Información y las Comunicaciones aplicadas a Piscicultura/Acuicultura*), enfocado en la **Fase 1: Mapeo sistemático y cribado de literatura científica (2020–2025)**.

## Arquitectura de dos fases y comunicación inter-proyecto

El proyecto TICaP está dividido estrictamente en dos fases y dos repositorios independientes:

1. **Fase 1 (este proyecto / repositorio):**
   - **Repositorio:** `Brokenearth/TICaP-Systematic-Mapping-Classification` (directorio local: `Metodologia Cursor Mapeo de estudios prueba`).
   - **Alcance:** Pipeline de importación, normalización, deduplicación, recuperación/validación de abstracts, cribado por pertinencia (CE1–CE10), revisión humana de dudosos y PRISMA sobre el corpus de 509 registros.
   - **Entregable transferido a Fase 2:** `zotero_export/TICaP_Zotero_01_Incluidos_229.bib` (229 registros incluidos con decisiones consolidadas).

2. **Fase 2 (proyecto separado):**
   - **Repositorio:** `Brokenearth/TICaP-Thematic-Classification` (directorio local: `TICaP_Clasificacion`).
   - **Alcance:** Clasificación temática multidimensional de los 229 estudios incluidos según objetivos de propuesta (OE1), tecnologías (OE2), métodos (OE3) y temas adicionales.
   - **Regla:** Fase 1 NO debe asumir ni invadir la taxonomía o clasificación temática fina de Fase 2.

3. **Contrato de sincronización (`PUENTE_FASES.md`):**
   - El archivo `PUENTE_FASES.md` define el contrato de datos compartido entre ambos repositorios.
   - Si se requiere actualizar algún dato que cruce entre fases (ej. errata en un metadato bibliográfico), debe registrarse en `PUENTE_FASES.md` y actualizarse en ambos repositorios.

## Reglas operativas

1. **Lectura previa obligatoria:** Antes de iniciar cualquier tarea sustancial, es obligatorio leer `PROJECT_STATE.md` y `PUENTE_FASES.md` en la raíz del repositorio.
2. **Historial de Cursor (recurso local opcional):** La conversación histórica de Cursor es un recurso local opcional que no forma parte del repositorio versionado y no es necesaria para operar el proyecto. `PROJECT_STATE.md` y las reglas en `.agents/rules/` constituyen las fuentes persistentes normales y suficientes de contexto técnico y metodológico.
3. **Prevalencia del estado real:** El estado verificable y auditable de los archivos reales del repositorio prevalece siempre sobre cualquier afirmación en documentación histórica, chats o notas preliminares.
4. **No reabrir fases terminadas:** No rehacer ni reiniciar procesos ya completados y validados (como extracción de abstracts, deduplicación o resolución de dudosos) sin una razón técnica o metodológica justificada y verificable.
5. **Estabilidad de decisiones:** No replantear ni refactorizar decisiones metodológicas o arquitectónicas ya adoptadas simplemente por preferencia estilística o criterio subjetivo de un nuevo agente.
