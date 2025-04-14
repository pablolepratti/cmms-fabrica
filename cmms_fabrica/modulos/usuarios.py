import csv
import hashlib
import os

RUTA_CSV = os.path.join("data", "usuarios.csv")

# Cargar usuarios desde CSV
def cargar_usuarios():
    usuarios = []
    with open(RUTA_CSV, mode="r", newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            usuarios.append(row)
    return usuarios

# Hashear contraseña con SHA-256
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Validar login
def validar_login(usuario_input, password_input):
    usuarios = cargar_usuarios()
    hash_input = hash_password(password_input)
    for u in usuarios:
        if u["usuario"] == usuario_input and u["contraseña"] == hash_input:
            return True
    return False

# Verificar si el usuario es admin
def es_admin(usuario_input):
    usuarios = cargar_usuarios()
    for u in usuarios:
        if u["usuario"] == usuario_input:
            return u["rol"] == "admin"
    return False
