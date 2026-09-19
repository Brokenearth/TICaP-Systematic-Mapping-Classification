# Clasificación TICaP por título y abstract

Trabaja sin Internet y sin consultar páginas web, APIs, PDFs, texto completo o
conocimiento externo. Usa únicamente:

- ID
- Título
- Abstract
- Año
- Tipo documental
- Criterios CE1-CE10 del documento oficial

Devuelve una decisión uniforme: `INCLUIR`, `EXCLUIR`, `DUDOSO`,
`DUPLICADO`, `FUERA_DE_PERIODO` o `TIPO_NO_ADMITIDO`.

Reglas:

1. No asumas información ausente.
2. Toda exclusión temática debe indicar un código CE.
3. La justificación debe apoyarse directamente en título o abstract.
4. Usa `DUDOSO` cuando la evidencia sea insuficiente o contradictoria.
5. La falta de abstract no implica exclusión automática.
6. Solo extrae tecnología, aplicación y categoría para `INCLUIR` o `DUDOSO`.
7. No alteres el texto de título o abstract.

