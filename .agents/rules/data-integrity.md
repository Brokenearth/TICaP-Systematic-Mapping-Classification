# Integridad de Datos y Trazabilidad

Reglas estrictas e inviolables para preservar la integridad de los datos bibliográficos, clasificaciones y artefactos generados.

## Reglas obligatorias

1. **Inmutabilidad del BibTeX original:** Nunca modificar los archivos BibTeX de entrada original (`mendeley_original.bib` y su espejo `TICaP-509All.bib`). Representan la evidencia primaria de la búsqueda documental.
2. **Prohibición de borrado físico:** Nunca eliminar registros del dataset para cuadrar números o descartar registros. Todos los registros del corpus original deben preservarse para fines de auditoría.
3. **Estabilidad de identificadores:** Los IDs `TICAP-XXXX` asignados son permanentes, deterministas e inmutables. Nunca renumerar ni reasignar IDs existentes.
4. **Trazabilidad de duplicados:** Los registros duplicados se marcan con decisión `DUPLICADO` y se vinculan al registro principal correspondiente. No se borran del corpus.
5. **No sobrescritura silenciosa:** Nunca sobrescribir archivos maestros o bases consolidadas sin validación previa y registro explícito del motivo.
6. **Separación de capas:** Mantener una distinción estricta entre archivos originales (`raw`), archivos intermedios de trabajo (`interim`) y entregables finales consolidados (`output`).
7. **Preservación del Excel de revisión humana:** El archivo de revisión manual del investigador (`output/revision_manual/...`) es evidencia histórica primaria; bajo ninguna circunstancia debe ser sobrescrito o regenerado por procesos automáticos.
8. **Sincronización con TICaPALL:** Todas las salidas publicadas en la carpeta de entregables `TICaPALL/` deben corresponder de forma exacta y con validación de hash a los resultados consolidados de `TICaP-509/`.
9. **Verificación post-modificación:** Tras cualquier modificación masiva de datos, es obligatorio ejecutar las pruebas unitarias y verificar las reglas de integridad (conteos totales, unicidad de IDs y consistencia de decisiones).

## Procedimiento para modificaciones masivas

Antes de aplicar cualquier cambio masivo o script de transformación sobre los datos, el agente debe:
- Especificar con precisión qué archivos serán modificados.
- Confirmar qué archivos permanecerán intactos e inalterados.
- Esperar confirmación o justificar la necesidad conforme a la metodología del proyecto.
