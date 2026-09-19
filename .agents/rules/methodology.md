# Metodología de Clasificación y Separación de Fases

Principios que rigen el proceso de cribado temático (*screening*) y la delimitación de fases metodológicas.

## 1. Clasificación temática

La clasificación temática (evaluación de pertinencia) debe operar exclusivamente con la siguiente información:
- ID del registro (`TICAP-XXXX`)
- Título
- Abstract
- Año de publicación
- Tipo documental (`article`, `inproceedings`)
- Criterios oficiales de pertinencia CE1–CE10 (`CriteriosPertinencia-Título y Abstract.pdf`)

### Prohibiciones expresas durante la clasificación:
- **No usar Internet:** Prohibido realizar búsquedas en la web, consultar páginas de revistas o invocar APIs externas durante el cribado temático.
- **No consultar texto completo:** La fase actual corresponde estrictamente a revisión por título y resumen.
- **No rellenar vacíos con conocimiento general:** No utilizar el conocimiento preentrenado del modelo o agente para deducir hechos no expresados en el título y abstract.

### Prioridad y fundamentación:
- El documento oficial de criterios CE1–CE10 tiene precedencia absoluta sobre cualquier inferencia o interpretación libre del agente.
- **Toda exclusión debe estar sustentada:** Ningún registro puede marcarse `EXCLUIR` sin asignar el código de criterio de exclusión correspondiente (CE1 a CE10).
- **Manejo de ambigüedad:** Si la información del título y abstract es insuficiente o contradictoria, debe clasificarse como `DUDOSO`. Nunca forzar una inclusión o exclusión inventando una conclusión.

---

## 2. Separación metodológica estricta

Es obligatorio mantener una separación conceptual y temporal estricta entre dos actividades metodológicas diferentes:

1. **Recuperación y verificación bibliográfica/abstracts:** Fase en la cual está permitido el acceso a Internet (APIs de Crossref, OpenAlex, Semantic Scholar y metadatos de sitios oficiales) únicamente para recuperar o validar el resumen oficial y metadatos del artículo.
2. **Clasificación temática:** Fase que evalúa la relevancia del estudio frente a las preguntas del mapeo. Debe ser 100% desconectada e insensible a fuentes externas.

Bajo ninguna circunstancia se debe recurrir a búsquedas en Internet para dirimir si un estudio debe incluirse o excluirse temáticamente.
