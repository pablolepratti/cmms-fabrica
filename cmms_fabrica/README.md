# 🏭 CMMS Fábrica – Versión 3.4

**Computerized Maintenance Management System (CMMS)** desarrollado en contexto real de fábrica, centrado en activos técnicos y trazabilidad total.

🔧 Organiza tareas correctivas, preventivas, técnicas, observaciones, calibraciones y servicios externos.  
📊 Compatible con auditorías, revisiones operativas y planificación de mantenimiento a corto y largo plazo.

---

## 🚀 Características Principales

- ✅ **Activo técnico como eje central** (`activos_tecnicos`)
- ✅ **CRUDs funcionales por tipo de tarea**
- ✅ **Trazabilidad automática** (todo queda registrado en `historial`)
- ✅ **Login con roles (admin / técnico)**
- ✅ **Dashboard de KPIs técnico-operativos**
- ✅ **Estilo visual oscuro y responsive**
- ✅ **Almacenamiento en MongoDB (conexión en `conexion_mongo.py`)**
- ✅ **Alineado con normas ISO 55001, 9001:2015, 14224**

---

## 📁 Estructura del Proyecto

```bash
cmms-fabrica/
├── app.py                      # Lanzador principal (menú general)
├── crud/                       # CRUDs actualizados (v3.4)
│   ├── crud_activos_tecnicos.py
│   ├── crud_tareas_correctivas.py
│   ├── crud_planes_preventivos.py
│   ├── crud_tareas_tecnicas.py
│   ├── crud_observaciones.py
│   ├── crud_calibraciones.py
│   ├── crud_servicios_externos.py
│   └── dashboard_kpi_historial.py
├── modulos/                    # Módulos heredados (en transición)
│   ├── app_login.py
│   ├── app_usuarios.py
│   ├── app_reportes.py
│   ├── conexion_mongo.py
│   ├── cambiar_ids.py
│   └── estilos.py
├── docs/                       # Documentación y estructura de fábrica
├── activos/                    # Carpeta técnica por máquina (checklists, fotos, planos)
├── reportes/                   # PDFs generados
└── requirements.txt            # Dependencias

