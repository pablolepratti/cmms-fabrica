# 🏭 CMMS Fábrica – Versión 3.4

**Computerized Maintenance Management System (CMMS)** desarrollado en contexto real de fábrica, centrado en activos técnicos, jerarquía funcional y trazabilidad total.

🔧 Organiza tareas correctivas, preventivas, técnicas, observaciones, calibraciones y servicios externos.  
📊 Compatible con auditorías, revisiones operativas y planificación de mantenimiento a corto y largo plazo.

---

## 🚀 Características Principales

- ✅ **Activo técnico como eje central** (`activos_tecnicos`)
- ✅ **Jerarquía funcional** (`pertenece_a`) para agrupar sistemas y subactivos
- ✅ **CRUDs completos por tipo de tarea**
- ✅ **Trazabilidad automática**: todo queda registrado en la colección `historial`
- ✅ **Login con gestión de usuarios y roles (admin / técnico)**
- ✅ **Dashboard de KPIs técnico-operativos**
- ✅ **Exportación de reportes técnicos (PDF y Excel)**
- ✅ **Visual oscuro y responsive en Streamlit**
- ✅ **Base de datos MongoDB conectada vía `conexion_mongo.py`**
- ✅ **Alineado con normas ISO 55001, 9001:2015 y 14224**

---

## 📁 Estructura del Proyecto

```bash
cmms-fabrica/
├── app.py                          # Lanzador principal (menú general)
├── crud/                           # CRUDs principales (v3.4)
│   ├── crud_activos_tecnicos.py
│   ├── crud_tareas_correctivas.py
│   ├── crud_planes_preventivos.py
│   ├── crud_tareas_tecnicas.py
│   ├── crud_observaciones.py
│   ├── crud_calibraciones.py
│   ├── crud_servicios_externos.py
│   └── dashboard_kpi_historial.py
├── modulos/                        # Módulos complementarios y de sistema
│   ├── app_login.py
│   ├── app_usuarios.py
│   ├── app_reportes.py
│   ├── conexion_mongo.py
│   ├── estilos.py
│   └── ../crud/generador_historial.py
├── activos/                        # Carpeta técnica por activo (checklists, fotos, planos)
├── docs/                           # Documentación e instructivos
│   └── checklist_cruds_activos_tecnicos.md  # Comparativa de campos por CRUD
├── reportes/                       # PDFs generados por el sistema
└── requirements.txt                # Dependencias Python
```

---

## 📌 Normas Aplicadas

Este CMMS está alineado con:

- **ISO 55001** → Gestión de activos físicos a lo largo de su ciclo de vida  
- **ISO 14224** → Estructura de datos y análisis de fallas en mantenimiento industrial  
- **ISO 9001:2015** → Gestión de calidad, trazabilidad documental y acciones correctivas

---

## 🛠️ Cómo Ejecutarlo

1. Clonar este repositorio
2. Crear un entorno virtual (opcional pero recomendado)
3. Instalar dependencias:

```bash
pip install -r requirements.txt
```

4. Iniciar la aplicación con:

```bash
streamlit run app.py
```

5. Conectar a tu base de datos MongoDB (configurado en `modulos/conexion_mongo.py`)
6. Crear un archivo `.env` con las variables `MONGO_URI` y opcionalmente `DB_NAME`

---

## 📬 Contacto

**Desarrollado por:** Pablo Lepratti  
📧 pablolepratti@gmail.com
🔗 Proyecto en contexto real de mantenimiento industrial – Uruguay

---

> *“Este sistema nació para organizar el mantenimiento en planta, pero creció como una herramienta robusta, trazable y adaptable a nuevas fábricas.”*
