from flask import Flask, render_template, request, redirect, url_for, send_file
import os
import random
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import base64

app = Flask(__name__)

# Ruta al índice
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para esconder el mensaje
@app.route('/hideMessage', methods=['GET', 'POST'], endpoint='hideMessage')
def esconder():
    if request.method == 'POST':
        mensaje = request.form['mensaje']
        clave = request.form['clave']
        
        # Verificar que la clave tenga 16, 24 o 32 caracteres (requerido para AES)
        if len(clave) not in [16, 24, 32]:
            return "<h1>Error: La clave debe tener 16, 24 o 32 caracteres.</h1><a href='/'>Regresar</a>"
        
        # Cargar plantilla de receta desde un archivo
        plantilla_path = "plantilla_receta.txt"
        if not os.path.exists(plantilla_path):
            return "<h1>Error: No se encontró la plantilla de receta.</h1><a href='/'>Regresar</a>"
        
        with open(plantilla_path, 'r') as file:
            plantilla_receta = file.read()
        
        # Encriptar mensaje
        receta_codificada = encriptar_mensaje(mensaje, plantilla_receta, clave)
        
        # Guardar receta en un archivo
        filepath = "receta.txt"
        with open(filepath, 'w') as file:
            file.write(receta_codificada)
        
        # Descargar archivo generado
        return send_file(filepath, as_attachment=True)
    
    return render_template('hideMessage.html')

# Ruta para decodificar el mensaje
@app.route('/decodificar', methods=['GET', 'POST'])
def decodificar():
    if request.method == 'POST':
        receta = None
        clave = request.form['clave']
        
        # Verificar que la clave tenga 16, 24 o 32 caracteres
        if len(clave) not in [16, 24, 32]:
            return "<h1>Error: La clave debe tener 16, 24 o 32 caracteres.</h1><a href='/'>Regresar</a>"
        
        # Procesar archivo o texto ingresado
        if 'archivo' in request.files and request.files['archivo'].filename != '':
            file = request.files['archivo']
            receta = file.read().decode('utf-8')
        else:
            receta = request.form['receta']
        
        if not receta:
            return "<h1>Error: No se ingresó una receta válida.</h1><a href='/'>Regresar</a>"
        
        # Decodificar mensaje
        mensaje_decodificado = decodificar_receta(receta, clave)
        return f"<h1>Mensaje decodificado: {mensaje_decodificado}</h1><a href='/'>Regresar</a>"
    
    return render_template('decodificar.html')

# Función para encriptar usando AES
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os
import base64

def encriptar_mensaje(mensaje, plantilla_receta, clave):
    """
    Cifra el mensaje usando AES con una clave proporcionada por el usuario.
    """
    # Convertir clave a bytes (UTF-8)
    clave_bytes = clave.encode('utf-8')
    
    # Inicializar AES en modo CBC con un vector de inicialización aleatorio
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(clave_bytes), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    
    # Padding del mensaje (asegura longitud válida)
    padder = padding.PKCS7(128).padder()  # 128 bits = 16 bytes
    mensaje_padded = padder.update(mensaje.encode('utf-8')) + padder.finalize()
    
    # Cifrar el mensaje
    mensaje_cifrado = encryptor.update(mensaje_padded) + encryptor.finalize()
    
    # Convertir a base64 para texto plano y UTF-8
    mensaje_cifrado_b64 = base64.b64encode(iv + mensaje_cifrado).decode('utf-8')
    
    # Insertar el mensaje cifrado en la plantilla de receta
    receta_codificada = plantilla_receta.replace('{cantidad}', mensaje_cifrado_b64)
    return receta_codificada


def decodificar_receta(receta, clave):
    """
    Decodifica una receta cifrada usando AES con la clave proporcionada.
    """
    # Extraer mensaje cifrado en base64 desde la receta
    mensaje_cifrado_b64 = receta.split('{cantidad}')[-1].strip()
    
    # Convertir clave a bytes (UTF-8)
    clave_bytes = clave.encode('utf-8')
    
    # Decodificar base64 a bytes
    mensaje_cifrado = base64.b64decode(mensaje_cifrado_b64.encode('utf-8'))
    
    # Extraer IV y mensaje cifrado
    iv = mensaje_cifrado[:16]
    mensaje_cifrado_sin_iv = mensaje_cifrado[16:]
    
    # Inicializar AES en modo CBC con el IV extraído
    cipher = Cipher(algorithms.AES(clave_bytes), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    
    # Descifrar el mensaje
    mensaje_padded = decryptor.update(mensaje_cifrado_sin_iv) + decryptor.finalize()
    
    # Quitar padding
    unpadder = padding.PKCS7(128).unpadder()  # 128 bits = 16 bytes
    mensaje = unpadder.update(mensaje_padded) + unpadder.finalize()
    
    # Decodificar a UTF-8
    return mensaje.decode('utf-8')


if __name__ == '__main__':
    app.run(debug=True)
