# 🏭 CMMS Fábrica – Modelo Conceptual Evolutivo

CMMS orientado a mantenimiento industrial con trazabilidad operativa e integración con MongoDB.

## 🧭 Modelo conceptual vigente

La aplicación se alinea con dos vistas complementarias:

- **Jerarquía técnica:** `Sistema > Subsistema > Equipo`
- **Nivel funcional:** `Proceso > Activo > Componente`

> Este modelo conceptual **convive con el esquema operativo actual** de la aplicación para mantener compatibilidad con datos históricos.

## 🔒 Compatibilidad de datos (sin ruptura)

- El campo **`pertenece_a`** se mantiene como relación padre operativa vigente entre registros.
- El campo **`nivel`** (cuando exista en el registro) representa la jerarquía técnica (`sistema`, `subsistema`, `equipo`).
- No se requieren renombres de colecciones ni migraciones masivas para adoptar el nuevo marco conceptual.

## 🧱 Núcleo CMMS

Módulos centrados en la gestión técnica de activos y mantenimiento:

- Activos técnicos
- Planes preventivos
- Tareas correctivas
- Tareas técnicas
- Observaciones técnicas
- Calibraciones
- Servicios técnicos

## 🧩 Módulos auxiliares (no núcleo conceptual)

Estos módulos se mantienen como soporte de operación y análisis:

- Inventario técnico
- Consumos técnicos
- Grafo CMMS
- Reportes técnicos
- KPIs y tablero de seguimiento

## ✅ Capacidades principales

- CRUD completo por dominio técnico.
- Trazabilidad en colección `historial`.
- Gestión de usuarios y roles.
- Integración con MongoDB vía `conexion_mongo.py`.
- Enfoque compatible con ISO 55001, ISO 14224 e ISO 9001:2015.

## 🛠️ Ejecución local

1. Instalar dependencias:

```bash
pip install -r cmms_fabrica/requirements.txt
```

2. Definir variables de entorno en `.env`:

```env
MONGO_URI=mongodb://<host>:<puerto>/
DB_NAME=cmms
```

3. Ejecutar la app:

```bash
streamlit run cmms_fabrica/app.py
```

4. (Opcional) instalar dependencias de desarrollo y correr pruebas:

```bash
pip install -r cmms_fabrica/requirements-dev.txt
PYTHONPATH=cmms_fabrica pytest -q
```
