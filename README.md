# 🏭 CMMS Fábrica

Sistema de Gestión de Mantenimiento Preventivo (CMMS) desarrollado en **Python + Streamlit**, conectado a una base de datos **PostgreSQL** desplegada en **Render**.

Este sistema fue creado para uso real en una planta industrial, con datos de maquinaria crítica, tareas programadas, observaciones técnicas e inventario asociado. Es una herramienta práctica para mantenimiento diario.

---

## 🚀 Funcionalidades principales

- ✅ Login seguro con roles (admin / usuario)
- ✅ Inicialización automática de base de datos
- ✅ Importación de datos desde `.csv`
- ✅ Dashboard con métricas clave
- ✅ Registro de tareas realizadas
- ✅ Historial con trazabilidad de máquina y usuario
- ✅ Carga y visualización de observaciones técnicas
- ✅ Inventario con vínculo a máquina asociada

---

## 🧰 Tecnologías utilizadas

- [Python 3](https://www.python.org/)
- [Streamlit](https://streamlit.io/)
- [PostgreSQL](https://www.postgresql.org/)
- [psycopg2](https://pypi.org/project/psycopg2-binary/)
- [dotenv](https://pypi.org/project/python-dotenv/)

---

## 📂 Estructura del proyecto

```
cmms-fabrica/
├── cmms_app.py           # Script principal
├── requirements.txt      # Dependencias
├── .env                  # Variables de entorno (no subir al repo)
├── cmms_data/            # Archivos .csv con datos reales
│   ├── maquinas.csv
│   ├── tareas.csv
│   ├── inventario.csv
│   ├── observaciones.csv
│   ├── historial.csv
│   └── usuarios.csv
```

---

## ⚙️ Instalación local

1. **Clonar el repositorio**
```bash
git clone https://github.com/tu_usuario/cmms-fabrica.git
cd cmms-fabrica
```

2. **Crear archivo `.env` con las variables de conexión PostgreSQL**
```dotenv
DB_HOST=...
DB_NAME=...
DB_USER=...
DB_PASSWORD=...
DB_PORT=5432
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Ejecutar la app**
```bash
streamlit run cmms_app.py
```

---

## 🧪 Datos de prueba para login

```txt
Usuario: pablo
Contraseña: admin123
Rol: admin
```

---

## 🌐 Despliegue en Render

- Crear servicio PostgreSQL en Render
- Subir `.env` con datos de conexión
- Configurar:
  - **Build command:** `pip install -r requirements.txt`
  - **Start command:** `streamlit run cmms_app.py`

---

## 📌 Notas adicionales

- El botón "Inicializar Base de Datos" solo debe usarse una vez (o si vacías la DB).
- Los archivos CSV cargan datos automáticamente si la tabla está vacía.
- Las tareas vencidas se calculan en base a 30 días desde la última ejecución.

---

## 👷 Autor

Pablo Lepratti  
Electromecánico industrial & Desarrollador de soluciones Mantenimiento + IA

📧 pablolepratti@gmail.com

---

> "Transformando datos de fábrica en decisiones inteligentes."
