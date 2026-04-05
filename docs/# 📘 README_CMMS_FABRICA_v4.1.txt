📘 CMMS FÁBRICA – Portable (v4.2)

🧭 Objetivo

Sistema CMMS portable centrado en el activo técnico.

Permite:

Organizar el mantenimiento
Registrar y trazar todas las acciones
Analizar fallas y comportamiento de activos
Generar mejora continua

🧱 Alcance

Incluye:

Sistemas industriales
Equipos de producción
Infraestructura técnica
Instrumentos
Servicios externos

🧩 Modelo de uso

El sistema se interpreta con dos lógicas:

1. Jerarquía técnica
Sistema → Subsistema → Equipo

2. Nivel funcional
Proceso → Activo → Componente

Definiciones:

Proceso → flujo o etapa
Activo → equipo físico
Componente → parte interna

👉 Se implementa mediante:

activo_padre → relaciones
nivel → jerarquía

Sin modificar la base de datos.

📦 Estructura del sistema

Colecciones principales

activos_tecnicos
planes_preventivos
tareas_correctivas
tareas_tecnicas
observaciones
calibraciones
servicios_externos
historial
usuarios

Funcionalidades

CRUD completo por colección
Registro automático en historial
Dashboard de KPIs
Reportes
Login con roles

🔄 Lógica de operación

→ Detectar → Analizar → Ejecutar → Registrar → Validar → Mejorar

📌 Regla clave:
Toda intervención inicia con análisis técnico y evaluación de criticidad.

📆 Revisión obligatoria cada 15 días.

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
