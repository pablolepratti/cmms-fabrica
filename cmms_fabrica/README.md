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
├── README.md
├── docs/
├── tests/
└── cmms_fabrica/
    ├── app.py                      # Lanzador principal (Streamlit)
    ├── requirements.txt            # Dependencias de runtime
    ├── requirements-dev.txt        # Dependencias para testing
    ├── crud/                       # CRUDs y trazabilidad (historial)
    └── modulos/                    # Módulos de login, reportes y utilidades
```

---

## 📌 Normas Aplicadas

Este CMMS está alineado con:

- **ISO 55001** → Gestión de activos físicos a lo largo de su ciclo de vida  
- **ISO 14224** → Estructura de datos y análisis de fallas en mantenimiento industrial  
- **ISO 9001:2015** → Gestión de calidad, trazabilidad documental y acciones correctivas

---

## 🛠️ Cómo Ejecutarlo

1. Clonar este repositorio y ubicarse en la raíz del proyecto (`cmms-fabrica/`).
2. Crear un entorno virtual (recomendado).
3. Instalar dependencias de runtime (archivo dentro de `cmms_fabrica/`):

```bash
pip install -r cmms_fabrica/requirements.txt
```

4. Crear archivo `.env` en la raíz del repositorio (`cmms-fabrica/.env`) con:

```env
MONGO_URI=mongodb://<host>:<puerto>/
DB_NAME=cmms
```

- `MONGO_URI` es **obligatoria**.
- `DB_NAME` es opcional (si no se define, el sistema usa `cmms` por defecto).

5. Iniciar la aplicación desde la raíz del repositorio con:

```bash
streamlit run cmms_fabrica/app.py
```

6. (Opcional) Para correr pruebas, instalar dependencias de desarrollo:

```bash
pip install -r cmms_fabrica/requirements-dev.txt
```

7. Ejecutar tests desde la raíz del repositorio:

```bash
PYTHONPATH=cmms_fabrica pytest -q
```

---

## 📬 Contacto

**Desarrollado por:** Pablo Lepratti  
📧 pablolepratti@gmail.com
🔗 Proyecto en contexto real de mantenimiento industrial – Uruguay

---

> *“Este sistema nació para organizar el mantenimiento en planta, pero creció como una herramienta robusta, trazable y adaptable a nuevas fábricas.”*
