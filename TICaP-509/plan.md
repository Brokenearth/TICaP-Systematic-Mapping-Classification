# Plan TICaP-509 (volumen ampliado)

Esta carpeta es el entorno de trabajo reproducible del corpus de 509 registros.
Los entregables principales se publican en `TICaPALL/`.

## Reglas

- El flujo es el mismo que el mapeo de 170 registros.
- El original en `TICaPALL/TICaP-509All.bib` no se modifica.
- La copia canónica inmutable es `data/raw/mendeley_original.bib`.
- El maestro de trabajo es `data/master/TICaP_master.bib`.
- El Excel final de trabajo es `output/excel/TICaP_clasificacion_titulo_abstract.xlsx`.
- Periodo: 2020-2025 inclusive.
- Tipos admitidos: `article` e `inproceedings`.
- Clasificación solo por título y abstract, sin Internet.

## Ejecución

Desde la raíz del proyecto:

```powershell
python -m scripts.run_pipeline --root "TICaP-509" --excel-abstracts "output/excel completo/TICaPAll_clasificacion_titulo_abstract.xlsx"
```

Eso reclasifica y publica en `TICaPALL/` el maestro `masterall509.bib`, el Excel final y los reportes.
