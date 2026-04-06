# Instalación del CMMS

1. Clona el repositorio.
2. Crea un entorno virtual y activa.
3. Instala las dependencias con `pip install -r cmms_fabrica/requirements.txt`.
4. Configura las variables en `.env`:
   - `MONGO_URI`
   - `DB_NAME` (opcional, default: `cmms`)
5. Ejecuta `streamlit run cmms_fabrica/app.py`.
