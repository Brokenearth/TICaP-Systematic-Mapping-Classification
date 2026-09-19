# Plan del mapeo sistemático TICaP 2020-2025

## Objetivo

Construir un flujo reproducible y trazable para conservar el BibTeX original,
normalizar sus registros, detectar duplicados, recuperar y validar abstracts,
clasificar exclusivamente por título y abstract, generar una matriz Excel y
obtener los conteos requeridos para PRISMA.

## Archivos oficiales

- Original inmutable: `data/raw/mendeley_original.bib`.
- Maestro único: `data/master/TICaP_master.bib`.
- Criterios: `criteria/CriteriosPertinencia-Título y Abstract.pdf`.
- Base cerrada de clasificación: `data/interim/base_clasificacion.csv`.
- Excel final: `output/excel/TICaP_clasificacion_titulo_abstract.xlsx`.
- Auditoría: `logs/registro_actividades.csv`.

Los originales conservados en la raíz tampoco se modifican. Sus hashes SHA-256
se registran en `logs/manifiesto_archivos.csv`.

## Estructura

- `data/raw`: entradas inmutables.
- `data/master`: único BibTeX maestro.
- `data/interim`: derivados regenerables.
- `data/manual`: decisiones y casos para revisión humana.
- `criteria`: documento oficial y catálogo fiel de criterios.
- `scripts`: programas separados por fase.
- `output`: resultados por abstracts, clasificación, revisión, Excel y reportes.
- `logs`: registro de actividades y errores.
- `prompts`: instrucciones versionadas para clasificación offline.
- `tests`: pruebas automatizadas.

## Fases, entradas, salidas y controles

### 0. Preparación

Entrada: archivos de la raíz. Salida: copias oficiales y manifiesto de hashes.
Control: coincidencia byte a byte y confirmación del periodo 2020-2025, ambos
inclusive, y de los tipos `article` e `inproceedings`.

### 1. Importación

Entrada: BibTeX original. Salidas: `registros_importados.jsonl` e `id_map.csv`.
Se asignan IDs estables `TICAP-0001` en orden de origen. Control: ningún registro
se pierde y todas las claves originales quedan trazadas.

### 2. Normalización

Se normalizan DOI, títulos para comparación, autores, años y tipos sin inventar
datos ni destruir los valores de origen. Salida:
`registros_normalizados.jsonl`. Control: igual cantidad e IDs que la importación.

### 3. Duplicados

Orden de detección: DOI idéntico; título normalizado idéntico; título parecido
con año y autores; revisión manual. No se borra nada. Se elige un principal y
se guardan grupos en `grupos_duplicados.csv`; candidatos inciertos se envían a
`data/manual/duplicados_por_revisar.csv`.

### 4. Recuperación de abstracts

Esta es la única fase que usa Internet. Orden: abstract del BibTeX, Crossref,
OpenAlex, Semantic Scholar, página oficial, búsqueda por título/autor/año y
revisión manual. Se conserva texto literal y procedencia. Nunca se genera,
resume, completa, combina o traduce un abstract. Sin evidencia se usa
`NO_ENCONTRADO`; candidatos inseguros no entran al maestro.

### 5. Calidad de abstracts

Se comprueban título, DOI, año, autores, integridad y reutilización. Estados:
`APTO_PARA_CLASIFICAR`, `REQUIERE_REVISION`, `SIN_ABSTRACT` y
`POSIBLE_ERROR_DE_COINCIDENCIA`. Solo los aptos se incorporan al maestro.

### 6. Base de clasificación

Se concilian todos los conteos y se crea una base cerrada con ID, título,
abstract, año y tipo. Se registran hashes de la base y los criterios. La falta
de abstract no equivale a exclusión.

### 7. Clasificación offline

Solo se usan la base cerrada y los criterios CE1-CE10. Se prohíben Internet,
APIs, páginas web, PDFs de artículos, texto completo y conocimiento externo.
Toda exclusión lleva criterio y justificación basada en título o abstract. Ante
evidencia insuficiente se usa `DUDOSO`.

Decisiones permitidas: `INCLUIR`, `EXCLUIR`, `DUDOSO`, `DUPLICADO`,
`FUERA_DE_PERIODO` y `TIPO_NO_ADMITIDO`.

### 8. Variables del mapeo

Para incluidos y dudosos se identifican, solo desde título/abstract, tecnología,
aplicación y categoría. Categorías iniciales: Gestión empresarial,
Automatización, Monitoreo ambiental, Alimentación, Crecimiento y biomasa,
Sanidad, Comportamiento, Control de calidad, Trazabilidad y certificación,
Apoyo a decisiones y Otra categoría emergente. La lista no es cerrada.

### 9. Revisión manual

Se revisan dudosos, abstracts inseguros, coincidencias, tipos y duplicados. Cada
cambio registra revisor, fecha, valor anterior, valor nuevo y motivo. La
decisión preliminar nunca se sobrescribe sin historial.

### 10. Excel

El Excel contiene exactamente: ID, Título, Abstract, Decisión, Criterio
aplicado, Justificación breve, Tecnología identificada, Aplicación
acuícola/piscícola, Categoría temática y Observación. Incluye el universo real,
IDs estables, decisiones uniformes, filtros y validaciones. No admite decisiones
vacías ni exclusiones sin criterio.

### 11. PRISMA

Se calculan desde datos trazables: iniciales, duplicados, fuera de periodo,
tipos no admitidos, abstracts existentes, recuperados, dudosos, no encontrados,
incluidos, excluidos, dudosos y pendientes manuales. Se documentan universo,
registros principales y evaluables para evitar doble conteo.

## Seguimiento

Cada ejecución registra fecha, fase, actividad, entrada, salida, procesados,
modificados, errores, observaciones, versión y hashes. Antes de avanzar se
validan entradas, conteos, salidas, incidencias y aprobación de la fase.

## Reglas generales

1. No borrar registros.
2. No modificar el BibTeX original.
3. No generar abstracts.
4. No clasificar utilizando Internet.
5. No excluir sin criterio.
6. Usar `DUDOSO` cuando falte evidencia.
7. Mantener un único BibTeX maestro.
8. Mantener un único Excel final.
9. Separar temporales y finales.
10. Registrar cada etapa.
11. Revisar una fase antes de iniciar la siguiente.
12. Solicitar confirmación antes de cambios masivos.
13. No crear datos ficticios.
14. Conservar la clasificación preliminar y toda corrección manual.

