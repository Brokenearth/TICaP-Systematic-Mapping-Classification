# Scripts del flujo TICaP

La lógica reutilizable está en `pipeline_lib.py`; la coordinación de fases y
sus archivos de entrada/salida está en `pipeline_steps.py`. El comando completo
es:

```powershell
python -m scripts.run_pipeline
```

Para una ejecución de prueba sin recuperación externa:

```powershell
python -m scripts.run_pipeline --sin-internet
```

Correspondencia funcional:

- `importacion`: `run_import`
- `normalizacion`: `run_normalization`
- `duplicados`: `run_duplicates`
- `abstracts`: `run_abstract_recovery`
- `clasificacion`: `run_prepare_classification` y `run_classification_offline`
- `validacion`: `validate_abstract_candidate` y `validate_classification_rows`
- `exportacion`: `run_export`, Excel y conteos PRISMA

La clasificación offline no realiza ninguna llamada de red. Las únicas
funciones de red están encapsuladas en la recuperación de abstracts.

