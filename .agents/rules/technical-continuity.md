# Continuidad Técnica y Prevención de Regresiones

Reglas técnicas orientadas a proteger la estabilidad del software, evitar regresiones en componentes críticos y preservar decisiones de deduplicación histórica.

## 1. Parser BibTeX

El parser propio del proyecto (`scripts/pipeline_lib.py`) cuenta con una corrección histórica crítica para el manejo de caracteres especiales y paréntesis en campos de texto:

- **Comportamiento protegido:** La presencia de enumeraciones textuales como `i)`, `ii)`, `iii)`, o paréntesis de aclaración tipo `(WOS)`, no debe alterar el conteo de delimitadores del parser ni provocar la absorción de campos posteriores (`title`, `year`, `author`) dentro del campo `abstract`.
- **Precedentes históricos:** Esta regresión afectó históricamente a los registros `TICAP-0007` y `TICAP-0062`, dejando títulos en blanco y asignando incorrectamente `FUERA_DE_PERIODO`.
- **Condiciones obligatorias para modificar el parser:**
  - Ejecutar y verificar la prueba de regresión `test_parses_fields_when_abstract_has_enumeration_parentheses` en `tests/test_pipeline.py`.
  - Mantener o ampliar la cobertura de pruebas de balance léxico.
  - No modificar la semántica ni el orden de asignación de los identificadores `TICAP-XXXX`.

---

## 2. Gestión de duplicados

1. **No eliminación física:** Los registros secundarios duplicados nunca deben eliminarse del archivo BibTeX ni de las bases tabulares; se marcan como `DUPLICADO` para auditoría metodológica completa.
2. **Criterio de registro principal:** La selección del registro principal frente al secundario se basa en la mayor completitud de datos (presencia de abstract original, DOI y metadatos bibliográficos completos). No alterar esta selección sin evidencia técnica verificable.
3. **Casos históricos que no deben revertirse:**
   - **`TICAP-0254` / `TICAP-0172`:** `TICAP-0254` (tesis en español de 2022) es la versión preliminar del artículo de revista en inglés `TICAP-0172` (2023). Debe mantenerse `TICAP-0172` como principal e incluirse/evaluarse, y `TICAP-0254` conservarse como duplicado secundario (`MANUAL_DUPLICATE_OF`).
   - **`TICAP-0440` / `TICAP-0475`:** `TICAP-0475` posee abstract completo y es el registro principal; `TICAP-0440` corresponde a la duplicación secundaria con menor información bibliográfica.
