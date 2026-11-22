# PUENTE_FASES.md — Contrato de comunicación entre Fase 1 y Fase 2

> [!IMPORTANT]
> Este archivo existe en **ambos repositorios** con contenido idéntico. Es la fuente de verdad compartida entre las dos fases del proyecto TICaP. Si se actualiza en uno, debe actualizarse en el otro.

---

## Repositorios vinculados

| Fase | Nombre | URL | Rama | Directorio local |
|---|---|---|---|---|
| **Fase 1** — Mapeo/Cribado | `TICaP-Systematic-Mapping-Classification` | https://github.com/Brokenearth/TICaP-Systematic-Mapping-Classification | `main` | `Metodologia Cursor Mapeo de estudios prueba/` |
| **Fase 2** — Clasificación temática | `TICaP-Thematic-Classification` | https://github.com/Brokenearth/TICaP-Thematic-Classification | `master` | `TICaP_Clasificacion/` |

---

## Qué produce Fase 1 y consume Fase 2

| Artefacto | Generado por | Consumido por | Ruta en Fase 1 | Ruta en Fase 2 |
|---|---|---|---|---|
| BibTeX de 229 incluidos | Fase 1 | Fase 2 | `zotero_export/TICaP_Zotero_01_Incluidos_229.bib` | `data/raw/TICaP_Zotero_01_Incluidos_229.bib` |
| IDs estables `TICAP-XXXX` | Fase 1 | Fase 2 | Asignados en Fase 1, Importación | Usados como claves únicas en clasificación |
| Criterios CE1–CE10 | Fase 1 | Referencia en Fase 2 | `criteria/catalogo_criterios.csv` | No se reimplementan |

---

## Contrato de datos — el archivo de transferencia

El único archivo que cruza de Fase 1 a Fase 2 es:

```
TICaP_Zotero_01_Incluidos_229.bib
SHA-256: 3061574178b087d6a1d179eaaf37c52ea713e5b128868216d012faa864978a89
Registros: 229
```

> [!CAUTION]
> Si Fase 1 necesitara regenerar este archivo (lo cual no está previsto — el corpus está cerrado), **debe notificarlo aquí** actualizando el hash y la fecha. Fase 2 no puede operar con un BibTeX diferente sin reiniciar su base congelada.

---

## Reglas de comunicación entre fases

1. **El corpus de 229 está cerrado.** Fase 1 no añadirá ni quitará registros. Fase 2 no reabrirá el cribado.
2. **Los IDs `TICAP-XXXX` son permanentes.** Ambas fases los usan como clave de trazabilidad.
3. **Fase 2 no modifica los archivos de Fase 1.** Solo lee el BibTeX de transferencia.
4. **Si Fase 1 publica una corrección** (ej. un abstract actualizado), debe registrarlo aquí con fecha, ID afectado y nuevo hash del archivo.
5. **Si Fase 2 descubre un error en un registro** (ej. metadatos incorrectos), lo documenta aquí y notifica a Fase 1 para que lo corrija en el BibTeX maestro.

---

## Estado actual de la transferencia

| Dato | Valor |
|---|---|
| Fecha de transferencia | 2026-09-19 |
| Registros transferidos | 229 (INCLUIR) |
| Hash verificado | ✅ `30615741…8a89` |
| BibTeX fuente en Fase 2 | Intacto (verificado 2026-10-20) |
| Cambios pendientes de Fase 1 → Fase 2 | **Ninguno** |
| Cambios pendientes de Fase 2 → Fase 1 | **Ninguno** |

---

## Registro de cambios cruzados

_Usar esta tabla cada vez que un cambio en una fase afecte a la otra._

| Fecha | Origen | Destino | Tipo | Descripción | IDs afectados | Acción requerida |
|---|---|---|---|---|---|---|
| _(sin cambios registrados)_ | — | — | — | — | — | — |

---

## Próximos puntos de sincronización previstos

| Evento | Fase que lo genera | Impacto en la otra | Cuándo |
|---|---|---|---|
| Cierre F7 Fase 2 (entrega final) | Fase 2 | Fase 1 referencia resultados en manuscrito | Tras F4 revisión humana |
| Diagrama PRISMA visual | Fase 1 | Fase 2 puede enlazarlo en reportes | Pendiente |
| Publicación del manuscrito | Ambas | Ambas cierran oficialmente | Futuro |

---

_Última actualización: 2026-11-21 — Sesión S-20261121-AGY_
