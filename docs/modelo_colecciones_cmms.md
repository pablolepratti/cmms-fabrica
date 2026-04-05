📦 MODELO DE COLECCIONES – CMMS PORTABLE (v4.1)



📌 PROPÓSITO



Definir la estructura de datos del CMMS centrado en el activo técnico.



👉 Todo se registra. Todo es trazable.



📌 CRITERIO DE MODELADO



El sistema se interpreta con dos lógicas:



1\. Jerarquía técnica

Sistema → Subsistema → Equipo



2\. Nivel funcional

Proceso → Activo → Componente



👉 Uso operativo, sin modificar la base.



📌 CRITERIO OPERATIVO



Toda entidad registrada debe surgir de:



Análisis técnico previo  

Evaluación de criticidad  



👉 No se registran eventos sin criterio técnico.



🧩 COLECCIONES



1\. activos\_tecnicos



👉 Núcleo del sistema. Representa todos los activos.



Incluye:

Equipos, sistemas, infraestructura, instrumentos, activos externos



Campos:



id\_activo\_tecnico  

nombre  

tipo\_activo  

nivel  

activo\_padre (opcional)  

ubicacion  

estado  

responsable  

observaciones  



\---



2\. planes\_preventivos



👉 Define qué se hace y cuándo.



Campos:



id\_plan  

id\_activo\_tecnico  

frecuencia  

unidad\_frecuencia  

proxima\_fecha  

ultima\_fecha  

responsable  

estado  

proveedor\_externo (opcional)  

observaciones  

usuario\_registro  



\---



3\. tareas\_correctivas



👉 Falla real + resolución + RCA.



👉 Toda tarea correctiva debe tener criticidad definida.



Campos:



id\_tarea  

id\_activo\_tecnico  

fecha\_evento  

descripcion\_falla  

modo\_falla  

causa\_raiz  

metodo\_rca  

acciones\_rca  

rca\_requerido  

rca\_completado  

usuario\_rca  

responsable  

proveedor\_externo (opcional)  

estado  

usuario\_registro  

observaciones  



\---



4\. tareas\_tecnicas



👉 Análisis y gestión técnica.



Tipos:



relevamiento  

diagnóstico  

gestión  

presupuesto  



Campos:



id\_tarea\_tecnica  

id\_activo\_tecnico (opcional)  

fecha\_evento  

descripcion  

tipo\_tecnica  

responsable  

proveedor\_externo (opcional)  

estado  

usuario\_registro  

observaciones  



\---



5\. observaciones



👉 Registro de anomalías detectadas.



👉 Base del mantenimiento predictivo.



👉 Toda observación debe ser evaluada técnicamente y clasificada por criticidad.



Escala a:



tarea correctiva  

tarea preventiva  



Campos:



id\_observacion  

id\_activo\_tecnico  

fecha\_evento  

descripcion  

tipo\_observacion  

reportado\_por  

estado  

usuario\_registro  

observaciones  



\---



6\. servicios\_externos



👉 Soporte técnico externo.



Campos:



id\_proveedor  

nombre  

especialidad  

contacto  

telefono  

correo  

observaciones  



\---



7\. historial



👉 Trazabilidad total automática.



Función:



Consolidar eventos  

Registrar acciones del sistema  



Campos:



id\_evento  

id\_activo\_tecnico  

fecha\_evento  

tipo\_evento  

id\_origen  

descripcion  

usuario\_registro  

proveedor\_externo (opcional)  

observaciones  



\---



8\. usuarios



👉 Control de acceso y trazabilidad.



\---



🔗 RELACIONES CLAVE



Todo gira en torno a activos\_tecnicos  

Todas las tareas generan historial  

observaciones alimenta acciones  

tareas\_tecnicas dispara decisiones  

servicios\_externos apoya ejecución  



\---



📌 CRITERIO DE DISEÑO



Modelo simple  

Ejecutable en planta  

Independiente de la fábrica  

Centrado en el técnico  



\---



📊 RESULTADO



Sistema:



Coherente  

Trazable  

Escalable  

Portable

