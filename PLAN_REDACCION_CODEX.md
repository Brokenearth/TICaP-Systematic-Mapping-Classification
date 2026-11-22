# Plan de Trabajo y Guía de Navegación para Codex / Agente Redactor en Overleaf

> **Propósito:** Esta guía está diseñada para que un agente de IA con capacidades de navegación web (browsing), como **Codex**, explore de forma autónoma los repositorios públicos del proyecto **TICaP** en GitHub, extraiga los datos empíricos y metodológicos verificados, y proceda a redactar o actualizar las secciones del artículo científico en **Overleaf** sin incurrir en alucinaciones numéricas.

---

## 1. Misión del Agente

Actúas como coautor académico experto en **mapeos sistemáticos de literatura (Systematic Literature Reviews / Systematic Mapping Studies)** bajo el estándar **PRISMA 2020** y en redacción científica en **LaTeX / Overleaf**.

Tu objetivo es:
1. Navegar por los dos repositorios públicos en GitHub del proyecto TICaP.
2. Extraer las estadísticas oficiales, taxonomía, justificaciones y conteos consolidados.
3. Redactar las secciones correspondientes del manuscrito (Metodología, Resultados, Discusión) entregando código LaTeX listo para compilar en Overleaf.

---

## 2. Repositorios de Consulta (Fuentes de Verdad)

Ambos repositorios son **públicos** y deben ser consultados mediante tu herramienta de navegación web:

### Repositorio 1: Fase 1 — Selección y Mapeo PRISMA
- **URL Base:** `https://github.com/Brokenearth/TICaP-Systematic-Mapping-Classification`
- **Archivos prioritarios a consultar:**
  - `README.md`: Resumen general, ventana temporal (2020–2025) y tabla oficial consolidada de conteos PRISMA.
  - `criteria/catalogo_criterios.csv`: Definición exacta de los 10 criterios de exclusión (CE1–CE10).
  - `PUENTE_FASES.md`: Contrato metodológico de transición entre la selección y la clasificación temática; explicación del universo de 229 estudios incluidos.
  - `PROJECT_STATE.md` / `BITACORA.md`: Resolución documentada de casos límite (falsos positivos como TICAP-0236 y resolución de los 40 dudosos).

### Repositorio 2: Fase 2 — Clasificación Temática Multidimensional
- **URL Base:** `https://github.com/Brokenearth/TICaP-Thematic-Classification`
- **Archivos prioritarios a consultar:**
  - `contexto/taxonomia.md`: Definición formal de las seis áreas del objetivo 1 (OE1: Gestión, Automatización, Monitoreo ambiental, Crecimiento/Sanidad, Control de calidad, Trazabilidad) y del catálogo de tecnologías (OE2: IoT, Sensores, Visión, Robótica, IA/DL, etc.).
  - `output/runs/completa_20261020T202024Z/reportes/resumen_tematico.md`: Frecuencias absolutas por área y tecnología, solapamientos multietiqueta y patrones temporales.
  - `output/runs/completa_20261020T202024Z/matrices/estudios.csv`: Matriz tabular con los 229 estudios y sus etiquetas temáticas asociadas.

---

## 3. Cifras y Datos Inmutables (No Alucinar)

El agente debe validar que cualquier texto o tabla en LaTeX coincida estrictamente con los siguientes valores consolidados:

* **Ventana temporal:** 2020 a 2025 (ambos inclusive).
* **Corpus inicial identificado:** 509 registros bibliográficos.
* **Duplicados identificados:** 18 registros.
* **Tipos documentales no admitidos:** 1 registro.
* **Total de estudios evaluados por título/abstract:** 490 registros.
* **Estudios excluidos:** 261 registros (cada uno respaldado por un criterio CE1–CE10).
* **Estudios incluidos en la síntesis temática:** **229 estudios**.
* **Dudosos pendientes:** 0 (todos resueltos y auditados).

---

## 4. Instrucciones Específicas por Sección del Manuscrito

### Sección A: Metodología del Mapeo Sistemático (PRISMA 2020)
1. **Preguntas de Investigación (RQs):** Redactar las preguntas orientadas a identificar las áreas productivas de aplicación (OE1), las tecnologías digitales emergentes (OE2) y los métodos/validaciones empíricas empleadas (OE3).
2. **Criterios de Elegibilidad:** Construir una tabla en LaTeX (`booktabs`) que liste los criterios de exclusión CE1 a CE10 a partir de `criteria/catalogo_criterios.csv`.
3. **Flujo de Selección PRISMA:** Generar el diagrama de flujo PRISMA 2020 utilizando código LaTeX (`tikz` o mediante una tabla estructurada paso a paso) reflejando:
   - Identificación (509) → Deduplicación (-18) y Tipo no admitido (-1) → Cribado por título/abstract (490) → Excluidos (-261) → Incluidos para síntesis cualitativa/cuantitativa (**229**).
4. **Reproducibilidad y Trazabilidad:** Describir brevemente que el proceso fue orquestado con pipelines automatizados deterministas, validación con pruebas unitarias y congelación con hashes SHA-256 (referenciar el repositorio abierto).

### Sección B: Resultados y Clasificación Temática
1. **Distribución por Áreas Productivas (OE1):**
   - Presentar la distribución de los 229 estudios explicando que el sistema es **multietiqueta** (un estudio puede abordar monitoreo ambiental y a la vez alimentación automatizada).
   - Datos clave: Monitoreo ambiental (área predominante con más del 95% de presencia), seguido de Automatización y Gestión.
2. **Tecnologías Digitales Identificadas (OE2):**
   - Tabular las tecnologías: IoT, Redes de Sensores, Robótica/UAVs, Visión por Computador, Deep Learning/Machine Learning.
   - Analizar la evolución temporal por año (2020 al 2025) a partir de los datos de `resumen_tematico.md`.
3. **Cruces Multidimensionales:**
   - Destacar la convergencia tecnológica común: sensores de calidad de agua integrados con IoT y algoritmos de visión computacional para estimación de biomasa o conteo de peces.

### Sección C: Discusión, Brechas y Amenazas a la Validez
1. **Brechas Identificadas:**
   - La escasa presencia de estudios en **Trazabilidad y Certificación** (OE1-F), lo que representa una oportunidad abierta de investigación.
   - La necesidad de validar en campo/producción comercial frente a experimentos únicamente a nivel de laboratorio o prototipo preliminar.
2. **Amenazas a la Validez:**
   - Limitación del cribado a título y abstract.
   - Posible sobreasignación de ciertas tecnologías (ej. drones/UAVs catalogados ampliamente bajo robótica de monitoreo).

---

## 5. Reglas Estrictas de Estilo, Voz y Gramática (Patrón del Autor)

A partir de la inspección de la redacción ya existente en el manuscrito en Overleaf, el agente **debe apegarse rigurosamente** a las siguientes pautas lingüísticas y convenciones:

1. **Persona Gramatical y Voz:**
   - **Primera persona del plural activa (plural de modestia / equipo de investigación):** El autor utiliza consistentemente expresiones como:
     - *"el grupo de investigadores analizamos el periodo..."*
     - *"consideramos que el periodo adecuado..."*
     - *"presentamos nuestras preguntas de investigación..."*
     - *"hemos planteado las siguientes preguntas específicas..."*
     - *"hemos realizado este mapeo de estudios..."*
     - *"describimos brevemente cada una de las etapas..."*
   - **Voz pasiva refleja / impersonal para procedimientos metodológicos:**
     - *"las preguntas de investigación fueron formuladas..."*
     - *"se definió a partir del análisis previo..."*
     - *"se aplicaron filtros para depurar los resultados..."*
   - **PROHIBICIÓN:** Nunca utilizar primera persona del singular (*"analicé", "propongo"*).

2. **Nomenclatura y Convenciones de Siglas Oficiales:**
   - **`TICaP`**: Tecnologías de la Información y las Comunicaciones aplicadas a la Piscicultura.
   - **`MS`**: Mapeo Sistemático.
   - **`PG`**: Pregunta General (*PG. ¿Cuáles son las TICaP en el periodo 2020-2025?*).
   - **`PE`**: Preguntas Específicas (*PE1: tendencias emergentes; PE2: enfoques metodológicos y resultados; PE3: distribución en las 6 áreas*).

3. **Referencias Cruzadas y Comandos Internos:**
   - Usar `\figref{etiqueta}` para figuras (ej. `\figref{MS-methodology}`).
   - Usar `\secref{etiqueta}` para secciones (ej. `\secref{sec:ant}`).
   - Usar `\tabref{etiqueta}` para tablas.
   - Citas bibliográficas en el texto: seguir la convención de autor-año de la revista (`authoryear`).

---

## 6. REGLA INVIOLABLE: INTEGRIDAD DEL FORMATO Y PLANTILLA RIAI

> [!CAUTION]
> **POR NINGÚN MOTIVO SE DEBE MODIFICAR EL FORMATO, CLASE O PLANTILLA DE OVERLEAF.**

1. **Plantilla oficial:** El proyecto utiliza la plantilla oficial de la **Revista Iberoamericana de Automática e Informática Industrial (RIAI)**:
   - Clase: `\documentclass[5p,times,authoryear]{RIAIarticle}`
   - Estilos: `crc_RIAI.sty`, `elsarticle-harv.bst`.
   - Compilador obligatorio: **PDFLaTeX** (no usar XeLaTeX ni LuaLaTeX).
2. **Prohibición de alterar el preámbulo:** No modificar márgenes, fuentes, espaciados, metadatos de cabecera de RIAI ni redefinir comandos de la revista.
3. **Punto exacto de inserción en `main.tex`:**
   - La redacción original del autor avanza hasta la línea ~462 en `\subsection{Todos los artículos}`.
   - A partir de la línea ~465 comienza el texto de ejemplo/relleno de la plantilla RIAI (`\subsection{Inserción de tablas}`, `\subsection{Ecuaciones}`, apéndices de muestra).
   - El nuevo contenido redactado (Fase de Cribado, Diagrama PRISMA, Resultados de Clasificación) debe reemplazar dicho texto de relleno **sin tocar la estructura de cierre del documento** (`\bibliography{...}`, `\end{document}`).
4. **Manejo de Tablas Anchas:** Dado que el formato es a 2 columnas (`5p`), si se incluye una tabla ancha (como la de criterios CE1–CE10 o la matriz PRISMA), se debe utilizar el entorno `table*` (con asterisco) o salir temporalmente del entorno de columnas según el estándar de RIAI, sin romper el flujo de lectura.

---

## 7. Reglas de Salida para Overleaf (Formato LaTeX)

* **Entornos limpios:** Emplear sintaxis estándar de LaTeX compatible con los paquetes ya cargados en la plantilla RIAI (`booktabs`, `amsmath`, `graphicx`, `hyperref`, `cite`).
* **Tablas profesionales:** Usar exclusivamente `\toprule`, `\midrule`, `\bottomrule`; no usar líneas verticales (`|`).
* **Citas bibliográficas:** Cuando cites ejemplos de estudios específicos del corpus, emplea las claves de citación estables `\cite{TICAP-XXXX}`.
* **Entrega modular:** Generar bloques de código `.tex` completos y listos para reemplazar las subsecciones pendientes en `main.tex`.
