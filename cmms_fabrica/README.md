# 🛠️ CMMS FÁBRICA – Sistema Modular de Mantenimiento

**Autor:** Pablo Lepratti  
**Versión:** Abril 2025  
**Licencia:** Uso interno, técnico-operativo

---

## 📌 Descripción

Sistema modular de mantenimiento industrial (CMMS), desarrollado en Python + Streamlit, con almacenamiento en CSV, acceso desde celular o PC y registro completo de actividad técnica y operativa.

---

## 🎯 Objetivos

- Organizar activos, tareas, inventario y observaciones técnicas
- Registrar actividades internas y servicios tercerizados
- Generar reportes PDF para trazabilidad y presentación
- Ejecutar backups automáticos a Google Drive
- Monitorear el uso de almacenamiento y autolimpiarse

---

## 📂 Estructura del Proyecto

```
cmms_fabrica/
├── app.py                  # Interfaz principal (Streamlit)
├── README.md               # Este archivo
├── modulos/                # Todos los módulos funcionales
│   ├── usuarios.py, maquinas.py, tareas.py, etc.
├── data/                   # CSVs persistentes
│   ├── usuarios.csv, maquinas.csv, tareas.csv, etc.
├── reportes/               # PDF generados automáticamente
```

---

## 🧩 Funcionalidades por módulo

| Módulo            | Funcionalidad principal                                        |
|-------------------|---------------------------------------------------------------|
| `usuarios.py`     | Login con SHA-256, control de roles                           |
| `maquinas.py`     | Gestión de activos por sector y tipo                          |
| `tareas.py`       | Tareas mensuales + reactivas                                  |
| `observaciones.py`| Registro técnico diario con criticidad                        |
| `inventario.py`   | Repuestos e insumos (uso interno o externo)                   |
| `servicios_ext.py`| Mantenimientos tercerizados con vencimientos                  |
| `kpi.py`          | Indicadores clave internos y externos                         |
| `reportes.py`     | Generación de PDF                                             |
| `historial.py`    | Registro automático de todo evento                            |
| `backup.py`       | Backup automático a Google Drive con rclone                   |
| `almacenamiento.py` | Autolimpieza basada en peso real de los CSVs               |

---

## 🧠 Tecnologías utilizadas

- **Python 3.10+**
- **Streamlit** (interfaz web)
- **pandas** (manejo de datos)
- **fpdf** (PDF)
- **rclone** (para backups)
- **GitHub + Render** (despliegue cloud)

---

## 📱 Accesible desde celular

El sistema detecta si estás desde un móvil y te muestra una interfaz simplificada.

---

## 🛡️ Seguridad

- Contraseñas encriptadas (SHA-256)
- Registro de eventos técnico-operativos en `historial.csv`

---

## ☁️ Recomendación de despliegue

- Subir este repositorio a GitHub
- Crear Web Service en [Render.com](https://render.com/)
- Comando de inicio: `streamlit run app.py`
