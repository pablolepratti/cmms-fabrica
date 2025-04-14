import os
import subprocess
from datetime import datetime
from modulos.historial import log_evento

# Nombre del remoto de rclone configurado
REMOTO = "cmms_drive"
FECHA = datetime.today().strftime("%Y-%m-%d")

def backup_data():
    origen = "data/"
    destino = f"{REMOTO}:/cmms_fabrica/data/"
    comando = ["rclone", "copy", origen, destino, "--update"]
    subprocess.run(comando)
    log_evento("sistema", "Backup realizado", "data/", "backup", f"Backup de data realizado el {FECHA}")

def backup_reportes():
    origen = "reportes/"
    destino = f"{REMOTO}:/cmms_fabrica/reportes/"
    comando = ["rclone", "copy", origen, destino, "--update"]
    subprocess.run(comando)
    log_evento("sistema", "Backup realizado", "reportes/", "backup", f"Backup de reportes realizado el {FECHA}")

def backup_completo():
    backup_data()
    backup_reportes()
