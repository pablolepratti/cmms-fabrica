# Comparación de CRUDs frente al Estándar de Activos Técnicos

Este informe resume la alineación de los principales CRUDs del sistema con el estándar de campos definidos para `activos_tecnicos`.

## Estándar de campos para un activo técnico

- `id_activo_tecnico`
- `nombre`
- `ubicacion`
- `tipo`
- `estado`
- `pertenece_a` *(opcional)*
- `usuario_registro`
- `fecha_registro`

## Revisión de módulos CRUD

| Módulo | Campos clave utilizados | Cumple estándar |
| ------ | ---------------------- | --------------- |
| `crud_activos_tecnicos.py` | `id_activo_tecnico`, `nombre`, `ubicacion`, `tipo`, `estado`, `pertenece_a`, `usuario_registro`, `fecha_registro` | ✅ |
| `crud_tareas_correctivas.py` | `id_activo_tecnico`, `id_tarea`, `descripcion_falla`, `fecha_evento`, `usuario_registro` | Parcial |
| `crud_planes_preventivos.py` | `id_activo_tecnico`, `id_plan`, `descripcion`, `fecha_evento`, `usuario_registro` | Parcial |
| `crud_tareas_tecnicas.py` | `id_activo_tecnico` *(opcional)*, `id_tarea_tecnica`, `descripcion`, `fecha_evento`, `usuario_registro` | Parcial |
| `crud_observaciones.py` | `id_activo_tecnico`, `id_observacion`, `descripcion`, `fecha_evento`, `usuario_registro` | Parcial |
| `crud_calibraciones_instrumentos.py` | `id_activo_tecnico`, `id_calibracion`, `descripcion`, `fecha_evento`, `usuario_registro` | Parcial |
| `crud_servicios_externos.py` | `id_activo_tecnico`, `id_proveedor`, `descripcion`, `fecha_realizacion`, `usuario_registro` | Parcial |

La columna *Cumple estándar* indica si el módulo implementa todos los campos obligatorios del estándar. Aquellos marcados como **Parcial** poseen `id_activo_tecnico` pero no todos los campos de la tabla base, lo cual es aceptable según su naturaleza (tareas o eventos asociados).

## Checklist de alineación

- [x] Cada CRUD registra `usuario_registro` y fecha de creación para trazabilidad.
- [x] Los eventos quedan centralizados en la colección `historial` vía `generador_historial.py`.
- [ ] Documentar en futuros desarrollos los campos específicos de cada CRUD para facilitar auditorías.

