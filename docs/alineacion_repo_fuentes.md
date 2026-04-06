# Alineación Repo ↔ Fuentes Oficiales (/docs)

Fecha de auditoría: 2026-04-05.

## Estado actual de alineación

### 1) Alineado

- Colecciones núcleo operativas presentes en código: `activos_tecnicos`, `planes_preventivos`, `tareas_correctivas`, `tareas_tecnicas`, `observaciones`, `calibraciones`, `servicios_externos`, `historial`, `usuarios`.
- Enfoque de trazabilidad con `historial` implementado y utilizado por módulos CRUD.
- Jerarquía técnica representada operativamente mediante `nivel` (opcional) y relación padre mediante `pertenece_a`.
- Estructura general de módulos (`crud/`, `modulos/`) coincide con lo definido en la documentación técnica del repositorio.

### 2) Parcialmente alineado

- **Modelo conceptual vs. persistencia**:
  - Fuentes oficiales usan `tipo_activo` y `activo_padre`.
  - Código vigente persiste `tipo` y `pertenece_a`.
  - Se mantiene compatibilidad, pero requiere mapeo explícito en documentación.
- **Regla de criticidad obligatoria**:
  - Las fuentes operativas indican criticidad obligatoria en correctivas/observaciones.
  - El código no exige campo de criticidad persistido en todos los formularios.
- **Trazabilidad homogénea**:
  - Existe `CMMSRepository` con validación de `id_activo_tecnico`, pero solo se aplica en `tareas_correctivas`; el resto de CRUDs todavía registra en forma directa.

### 3) Desalineado / legado detectado

- `docs/setup.md` tenía comandos de ejecución/despliegue en rutas antiguas (`requirements.txt` y `app.py` en raíz).
- Referencias documentales antiguas sin distinguir explícitamente entre modelo conceptual y campos persistidos en producción.
- Algunos módulos auxiliares (`inventario`, `consumos`) usan nomenclaturas heredadas (`maquina_compatible`) que no están en el modelo conceptual principal.

## Decisiones tomadas (cambios seguros aplicados)

1. **No se tocaron colecciones persistidas ni campos en MongoDB.**
2. Se actualizó documentación para dejar explícito el criterio de compatibilidad:
   - Conceptual: `activo_padre` / `tipo_activo`.
   - Operativo vigente: `pertenece_a` / `tipo`.
3. Se corrigió guía de instalación para reflejar rutas reales del repositorio.
4. Se actualizó README principal para alinear lenguaje operativo, alcance real y comandos válidos.

## Pendientes de riesgo medio/alto (NO implementados)

### Riesgo medio

- Estandarizar labels/UI para reflejar explícitamente el mapeo conceptual ↔ operativo en todos los formularios.
- Incorporar validaciones funcionales de criticidad (sin cambiar persistencia existente).

### Riesgo alto

- Renombrar campos persistidos (`tipo` → `tipo_activo`, `pertenece_a` → `activo_padre`).
- Renombrar colecciones o introducir migraciones de datos.
- Unificar todos los CRUDs bajo `CMMSRepository` sin plan de transición y pruebas integrales.

## Criterio de transición recomendado

- Mantener esquema actual por compatibilidad.
- Aplicar dualidad documental y de UI (mostrar término conceptual + campo operativo real).
- Cuando se planifique una migración, hacerlo con estrategia versionada, scripts de backfill, rollback y validación por ambiente.
