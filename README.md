# TICaP Systematic Mapping Classification

Pipeline reproducible para el mapeo sistemático de literatura científica sobre Tecnologías de la Información y las Comunicaciones (TIC) aplicadas a la piscicultura y acuicultura productiva.

Este repositorio contiene:
- Pipeline de procesamiento y normalización bibliográfica.
- Metodología y reglas de clasificación temática por título y abstract.
- Catálogo de criterios de pertinencia (CE1–CE10).
- Pruebas automatizadas de integración y regresión.
- Reglas de gobernanza, integridad de datos y reproducibilidad.
- Documentación del estado metodológico del proyecto.

> **Nota sobre los datos:** Los datasets bibliográficos, abstracts, hojas Excel de clasificación, archivos BibTeX, resultados detallados y documentos de revisión humana no se incluyen en el repositorio por razones de integridad, privacidad y gestión de datos.

---

## Requisitos e Instalación

Entorno estándar recomendado: Python 3.10+ (verificado en Python 3.12).

```bash
pip install -r requirements.txt
```

---

## Pruebas automatizadas

El proyecto incluye pruebas unitarias y de integración que validan el parser BibTeX, la normalización, la detección de duplicados y la consistencia del flujo de trabajo:

```bash
python -m unittest discover -s tests -v
```

---

## Estructura general

- `scripts/`: Módulos del pipeline (librería central de parsing, normalización, clasificación heurística y orquestador de fases).
- `tests/`: Batería de pruebas automatizadas unitarias y de flujo metodológico.
- `criteria/`: Catálogo formal y definiciones de los criterios de exclusión (CE1–CE10).
- `prompts/`: Instrucciones estructuradas para el cribado temático offline por título y abstract.
- `.agents/rules/`: Reglas de integridad, tratamiento de abstracts, jerarquía de revisión humana y continuidad técnica.
- `PROJECT_STATE.md`: Memoria persistente del proyecto con especificación de estado, diseño y arquitectura.

---

## Estado actual

- **Pipeline validado:** Flujo modular estabilizado y reproducible.
- **Clasificación consolidada:** Cribado completado bajo criterios CE1–CE10 y revisión humana de control.
- **Dudosos:** 0 casos dudosos pendientes de resolución.
- **Suite de pruebas:** Todas las pruebas automatizadas pasan satisfactoriamente.
