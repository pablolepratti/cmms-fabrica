# 🏭 CMMS Fábrica – Portable

CMMS orientado a mantenimiento industrial con trazabilidad operativa e integración con MongoDB.

## 🧭 Modelo conceptual vigente (fuentes en `/docs`)

La aplicación se alinea con dos vistas complementarias:

- **Jerarquía técnica:** Sistema → Subsistema → Equipo
- **Nivel funcional:** Proceso → Activo → Componente

Este modelo convive con el esquema operativo actual para conservar compatibilidad histórica.

## 🔒 Compatibilidad de datos (sin ruptura)

Para evitar migraciones silenciosas:

- Se mantiene **`pertenece_a`** como relación padre operativa vigente.
- Se usa **`nivel`** (cuando existe) para expresar jerarquía técnica.
- Se conserva **`tipo`** como campo persistido en activos (equivalente operativo de `tipo_activo` conceptual).
- No se renombraron colecciones persistidas ni campos críticos existentes.

## 🧱 Núcleo CMMS (implementación activa)

- Activos técnicos
- Planes preventivos
- Tareas correctivas
- Tareas técnicas
- Observaciones técnicas
- Calibraciones
- Servicios técnicos externos
- Historial técnico
- Usuarios y roles

## 🧩 Módulos auxiliares (soporte operativo)

- Inventario técnico
- Consumos técnicos
- Grafo CMMS
- Reportes técnicos
- KPIs y tablero de seguimiento
- Asistentes técnicos (IA)

## ✅ Capacidades principales

- CRUD por dominio técnico.
- Registro de trazabilidad en colección `historial`.
- Gestión de usuarios y roles.
- Integración con MongoDB (`conexion_mongo.py`).
- Alineación operativa con ISO 55001, ISO 14224 e ISO 9001.

## 🛠️ Ejecución local

Instalar dependencias:

```bash
pip install -r cmms_fabrica/requirements.txt
```

Definir variables de entorno en `.env`:

```bash
MONGO_URI=mongodb://<host>:<puerto>/
DB_NAME=cmms
```

Ejecutar la app:

```bash
streamlit run cmms_fabrica/app.py
```

Pruebas (opcional):

```bash
pip install -r cmms_fabrica/requirements-dev.txt
PYTHONPATH=. pytest -q
```

## 🔄 Lógica de operación

Detectar → Analizar → Ejecutar → Registrar → Validar → Mejorar

Revisión obligatoria cada 15 días.

## ⚠️ Criterio de priorización

Las intervenciones se priorizan según criticidad:

- 🔴 Crítico → parada de línea o riesgo de seguridad.
- 🟠 Alto → impacto en producción.
- 🟡 Medio → degradación del rendimiento.
- 🟢 Bajo → sin impacto relevante.

La criticidad se evalúa con:

- Impacto en producción
- Riesgo de seguridad
- Estado del activo
- Reincidencia

La criticidad define prioridad (no urgencia percibida).

## 🎯 Filosofía de uso

- El CMMS es la única fuente de verdad.
- Toda acción se registra.
- Simplicidad > complejidad.
- El sistema se adapta al técnico.
- La mejora se basa en lo ejecutado.

## 📋 Tipos de tareas

- Correctivas → fallas reales + RCA
- Preventivas → tareas planificadas
- Técnicas → análisis y gestión
- Observaciones → hallazgos

## 📋 Normas

Alineado con:

- ISO 55001
- ISO 9001
- ISO 14224

## 👤 Autor

Pablo Lepratti

> “El sistema no representa la fábrica. Representa cómo el técnico la entiende.”
