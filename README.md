🏭 CMMS Fábrica – Portable

CMMS orientado a mantenimiento industrial con trazabilidad operativa e integración con MongoDB.

🧭 Modelo conceptual vigente

La aplicación se alinea con dos vistas complementarias:

Jerarquía técnica:
Sistema > Subsistema > Equipo

Nivel funcional:
Proceso > Activo > Componente

Este modelo conceptual convive con el esquema operativo actual de la aplicación para mantener compatibilidad con datos históricos.

🔒 Compatibilidad de datos (sin ruptura)
El campo pertenece_a se mantiene como relación padre operativa vigente entre registros
El campo nivel (cuando exista en el registro) representa la jerarquía técnica (sistema, subsistema, equipo)
No se requieren renombres de colecciones ni migraciones masivas
🧱 Núcleo CMMS

Módulos centrados en la gestión técnica de activos y mantenimiento:

Activos técnicos
Planes preventivos
Tareas correctivas
Tareas técnicas
Observaciones técnicas
Calibraciones
Servicios técnicos
🧩 Módulos auxiliares (no núcleo conceptual)

Estos módulos se mantienen como soporte de operación y análisis:

Inventario técnico
Consumos técnicos
Grafo CMMS
Reportes técnicos
KPIs y tablero de seguimiento
✅ Capacidades principales
CRUD completo por dominio técnico
Trazabilidad mediante colección historial
Gestión de usuarios y roles
Integración con MongoDB (conexion_mongo.py)
Alineación con ISO 55001, ISO 14224 e ISO 9001
🛠️ Ejecución local

Instalar dependencias:

pip install -r cmms_fabrica/requirements.txt

Definir variables de entorno en .env:

MONGO_URI=mongodb://<host>:<puerto>/
DB_NAME=cmms

Ejecutar la app:

streamlit run cmms_fabrica/app.py

(Opcional) pruebas:

pip install -r cmms_fabrica/requirements-dev.txt
PYTHONPATH=cmms_fabrica pytest -q

🔄 Lógica de operación

Detectar → Ejecutar → Registrar → Validar → Mejorar

Revisión obligatoria cada 15 días.

⚠️ Criterio de priorización

Las intervenciones se priorizan según criticidad:

🔴 Crítico → parada de línea o riesgo de seguridad
🟠 Alto → impacto en producción
🟡 Medio → degradación del rendimiento
🟢 Bajo → sin impacto relevante

La criticidad se evalúa en base a:

Impacto en producción
Riesgo de seguridad
Estado del activo
Reincidencia

La criticidad define prioridad, no urgencia percibida.

🎯 Filosofía de uso
El CMMS es la única fuente de verdad
Toda acción se registra
Simplicidad > complejidad
El sistema se adapta al técnico
La mejora se basa en lo ejecutado
📋 Tipos de tareas
Correctivas → fallas reales + RCA
Preventivas → tareas planificadas
Técnicas → análisis y gestión
Observaciones → hallazgos
📊 Resultado esperado

Sistema:

Ordenado
Trazable
Repetible
Aplicable en cualquier fábrica
📋 Normas

Alineado con:

ISO 55001
ISO 9001
ISO 14224
🌱 Escalabilidad
Integración con sensores (IoT)
Automatización
IA sobre historial
👤 Autor

Pablo Lepratti

“El sistema no representa la fábrica. Representa cómo el técnico la entiende.”
