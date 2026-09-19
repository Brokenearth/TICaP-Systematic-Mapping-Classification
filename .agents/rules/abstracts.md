# Reglas para la Gestión de Abstracts

Directrices rigurosas para la obtención, validación y tratamiento de resúmenes científicos en el proyecto.

## Reglas obligatorias sobre el contenido de abstracts

1. **Nunca generar abstracts sintéticos:** Está terminantemente prohibido utilizar modelos de lenguaje o generación de texto para redactar abstracts ausentes o inventar contenidos.
2. **Nunca completar frases:** Si un abstract en su fuente de origen se encuentra cortado, incompleto o truncado por límite de caracteres, debe conservarse tal como fue extraído.
3. **Nunca combinar fragmentos:** No fusionar partes de abstracts provenientes de diferentes repositorios para crear una versión compuesta.
4. **No sustituir por resúmenes propios:** Los comentarios, notas o síntesis elaboradas por el agente o investigador no deben grabarse en el campo `abstract`. Su lugar es la columna `Observación`.
5. **No traducir el original:** Los abstracts deben conservarse en su idioma original de publicación. Nunca sustituir el texto original por una traducción automática.
6. **Separación de notas administrativas:** Advertencias, notas de descarte o notas operativas (como *"Sin abstract disponible"* o *"Duplicado"*) no deben almacenarse como texto científico en el campo de abstract.

## Validación y procedencia

1. **Trazabilidad de origen:** Todo abstract recuperado externamente debe registrar explícitamente su procedencia (`BIBTEX`, `CROSSREF`, `OPENALEX`, `SEMANTIC_SCHOLAR`, `SCRAPING_OFICIAL`, `MANUAL_INVESTIGADOR`) en los registros de auditoría (`procedencia_abstracts.csv`).
2. **Validación cruzada obligatoria:** Antes de incorporar un abstract recuperado por API externa, debe comprobarse la concordancia estricta de:
   - Título normalizado.
   - DOI.
   - Año de publicación.
   - Coincidencia de al menos un autor principal.
3. **Tratamiento ante dudas:** Si la coincidencia entre el registro y la respuesta de la API no es inequívoca, el abstract debe marcarse como `POSIBLE_ERROR_DE_COINCIDENCIA` o `REQUIERE_REVISION`, sin integrarse automáticamente.
4. **Eficiencia en duplicados:** No realizar consultas externas para recuperar abstracts de registros marcados como duplicados si el registro principal ya cuenta con abstract completo.
