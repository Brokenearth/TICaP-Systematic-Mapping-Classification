# Principios de Revisión Humana y Jerarquía de Decisiones

Definición de la autoridad metodológica y el flujo de resolución humana en el proyecto TICaP.

## Principio fundamental de jerarquía

Ninguna clasificación automática, inferencia heurística o recomendación asistida por IA tiene prioridad sobre una decisión humana explícitamente documentada por el investigador del proyecto.

## Flujo metodológico de decisión

El proceso de screening distingue siempre tres etapas secuenciales:

$$\text{Clasificación automática / preliminar} \longrightarrow \text{Revisión humana} \longrightarrow \text{Decisión final consolidada}$$

- La etapa automática genera una primera aproximación y aísla los casos que requieren análisis experto.
- La decisión final es aquella confirmada tras el criterio del investigador.

## Tratamiento de etiquetas de revisión intermedia

Las etiquetas generadas en fases previas o intermedias:
- `Dudoso (incluir)`
- `Dudoso (excluir)`

constituyen **estados de trabajo o recomendaciones de revisión**, no valores de decisión canónica.

**Regla de aplicación:**
- Bajo ninguna circunstancia el pipeline o un agente deben transformar automáticamente `Dudoso (incluir)` en `INCLUIR` ni `Dudoso (excluir)` en `EXCLUIR` sin una regla explícita o confirmación humana documentada.

## Preservación de justificaciones humanas

1. **Prefijo `INV:`:** Las justificaciones originadas en la revisión experta humana se identifican con el prefijo `INV:`. Estas justificaciones deben preservarse íntegras y no deben sobrescribirse con explicaciones automáticas genéricas.
2. **Contradicciones aparentes:** Si se identifica una discrepancia o tensión aparente entre una decisión humana y el texto de su justificación, el agente **nunca debe corregirla silenciosamente**. Debe registrar la observación y solicitar confirmación explícita al usuario.
