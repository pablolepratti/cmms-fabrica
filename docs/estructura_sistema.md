# Estructura del Sistema

Los módulos se agrupan en `crud/` y `modulos/` para facilitar el mantenimiento y la escalabilidad del CMMS.

## Timestamps
La coleccion `historial` almacena los eventos con el campo `fecha_evento`. Este valor se genera en `crud/generador_historial.py` y representa la fecha y hora efectivas de cada actualizacion.
Otros registros guardan `fecha_registro` para indicar cuando se creo la entrada, pero el orden cronologico y los filtros de reportes siempre se basan en `fecha_evento`.
