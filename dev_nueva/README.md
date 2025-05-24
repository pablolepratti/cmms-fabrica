
# 🧠 CMMS Fábrica – Sistema de Mantenimiento Centrado en el Activo Técnico

Sistema desarrollado para gestionar de forma clara y robusta el mantenimiento preventivo, correctivo y técnico en una fábrica real.  
Diseñado para ser **funcional**, **modular**, y compatible con futuros sistemas inteligentes como MIA.

---

## 🏗️ Evolución del Proyecto

### 🧱 CMMS viejo
- Sistema operativo funcional pero caótico
- Módulos aislados con colecciones independientes
- MongoDB sin normalizar, sin eje central
- Estructura difícil de mantener y extender

### ⚠️ Intento previo de nueva versión
- Intento de reorganización no funcional
- Desvinculación entre tareas y activos
- No se logró consolidar en producción

### ✅ Versión actual (2025)
- Modelo **centrado en el activo técnico**
- Migración completa y limpia de MongoDB viejo
- Normalización con orientación a normas ISO / RAMI 4.0
- Estructura modular, clara, documentada y extensible

---

## 🧠 Modelo Operativo

Cada activo técnico contiene:

- Tareas preventivas
- Tareas correctivas
- Tareas técnicas
- Calibraciones (si aplica)
- Observaciones técnicas
- Historial de eventos
- Repuestos usados
- Reportes por activo

Todo se maneja desde una sola colección: `cmms.activos_tecnicos`

---

## 📦 Estructura del Proyecto

```
cmms_fabrica/
├── app.py                   ← Menú principal (Streamlit)
├── requirements.txt
├── .gitignore
├── README.md
├── modulos/
│   ├── app_activos.py
│   ├── app_mantenimiento.py
│   ├── app_tareas.py
│   ├── app_tareas_tecnicas.py
│   ├── app_calibracion.py
│   ├── app_observaciones.py
│   └── app_reportes.py
```

---

## 🚀 Cómo usar

1. Clonar el repositorio:
```bash
git clone https://github.com/pablolepratti/cmms-fabrica.git
cd cmms-fabrica
```

2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

3. Ejecutar el sistema:
```bash
streamlit run app.py
```

---

## 🔧 Requisitos

- Python 3.9+
- MongoDB local o Atlas
- Librerías: `streamlit`, `pymongo`, `pandas`, `openpyxl`

---

## 🛣️ Planes futuros

- Integración con MIA (monitoreo inteligente)
- Módulo de compras y stock automatizado
- Exportación de reportes automáticos
- Control de vencimientos por calendario

---

Desarrollado por **Pablo Lepratti** – 2025  
Este proyecto es público y está en evolución continua 🚀
