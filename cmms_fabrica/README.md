# 🏭 CMMS Fábrica

Sistema de gestión de mantenimiento computarizado (CMMS) desarrollado en Python + Streamlit + MongoDB para uso en fábricas industriales.

---

## 🚀 Características principales

- Registro y edición de máquinas
- Gestión de tareas de mantenimiento preventivo
- Carga de historial y observaciones
- Cambio de IDs manuales sin afectar la integridad de los datos
- Conexión directa con MongoDB Atlas
- Interfaz accesible y simple vía Streamlit

---

## 📦 Requisitos

- Python 3.10 o superior
- MongoDB Atlas
- Las librerías del `requirements.txt`

---

## 🔧 Instalación rápida

```bash
git clone https://github.com/pablolepratti/cmms-fabrica.git
cd cmms-fabrica
pip install -r requirements.txt
```

Luego crear un archivo `.env` en la raíz:

```
MONGO_URI=tu_url_de_mongodb
```

---

## ▶️ Ejecutar el sistema

```bash
streamlit run app.py
```

---

## 🗂️ Estructura

```
cmms-fabrica/
│
├── app.py                      # Menú principal
├── requirements.txt            # Dependencias con versiones
├── .env                        # Configuración Mongo (no se sube)
├── modulos/                    # Módulos funcionales
├── data/                       # Datos locales temporales
└── README.md                   # Este archivo
```

---

> Hecho con 💻 por Pablo D. Lepratti