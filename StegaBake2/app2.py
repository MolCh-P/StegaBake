import rsa
from flask import Flask, render_template, request, send_file
import os
import random

app = Flask(__name__)

# Generar claves RSA
(public_key, private_key) = rsa.newkeys(512)

# Ruta al índice
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para esconder el mensaje usando RSA y XOR
@app.route('/hideMessage', methods=['GET', 'POST'], endpoint='hideMessage')
def esconder():
    if request.method == 'POST':
        mensaje = request.form['mensaje']
        clave = request.form['clave']

        # Validar clave
        if not clave.isdigit():
            return "<h1>Error: La clave debe ser un número.</h1><a href='/'>Regresar</a>"
        clave = int(clave)

        # Validar mensaje
        if not mensaje:
            return "<h1>Error: El mensaje no puede estar vacío.</h1><a href='/'>Regresar</a>"

        # Convertir el mensaje en ASCII y aplicar XOR
        mensaje_cifrado_xor = ''.join(chr(ord(char) ^ clave) for char in mensaje)

        # Encriptar el mensaje cifrado con RSA
        try:
            mensaje_cifrado_rsa = rsa.encrypt(mensaje_cifrado_xor.encode('utf-8'), public_key)
        except Exception as e:
            return f"<h1>Error al encriptar con RSA: {e}</h1><a href='/'>Regresar</a>"

        # Convertir los valores encriptados a una lista de números
        valores_codificados = list(mensaje_cifrado_rsa)

        # Cargar plantilla de receta
        plantilla_path = "plantilla_receta.txt"
        if not os.path.exists(plantilla_path):
            return "<h1>Error: No se encontró la plantilla de receta.</h1><a href='/'>Regresar</a>"

        with open(plantilla_path, 'r') as file:
            plantilla_receta = file.read()

        # Sustituir los valores en los marcadores {cantidad}
        marcador = "{cantidad}"
        for valor in valores_codificados:
            if marcador in plantilla_receta:
                plantilla_receta = plantilla_receta.replace(marcador, str(valor), 1)

        # Guardar la receta resultante
        filepath = "receta.txt"
        with open(filepath, 'w') as file:
            file.write(plantilla_receta)

        return send_file(filepath, as_attachment=True)

    return render_template('hideMessage.html')

# Ruta para decodificar el mensaje
@app.route('/decodificar', methods=['GET', 'POST'])
def decodificar():
    if request.method == 'POST':
        clave = request.form['clave']

        # Validar clave
        if not clave.isdigit():
            return "<h1>Error: La clave debe ser un número.</h1><a href='/'>Regresar</a>"
        clave = int(clave)

        # Procesar archivo cargado o texto ingresado
        receta = None
        if 'archivo' in request.files and request.files['archivo'].filename != '':
            file = request.files['archivo']
            receta = file.read().decode('utf-8')
        else:
            receta = request.form['receta']

        if not receta:
            return "<h1>Error: No se ingresó una receta válida.</h1><a href='/'>Regresar</a>"

        # Extraer valores codificados desde la receta
        valores_codificados = []
        for linea in receta.split('\n'):
            for palabra in linea.split():
                if palabra.isdigit():  # Solo números
                    valores_codificados.append(int(palabra))

        # Reconstruir el mensaje cifrado RSA (como bytes)
        try:
            mensaje_cifrado_rsa = bytes(valores_codificados)
            mensaje_cifrado_xor = rsa.decrypt(mensaje_cifrado_rsa, private_key).decode('utf-8')
        except Exception as e:
            return f"<h1>Error al descifrar mensaje: {e}</h1><a href='/'>Regresar</a>"

        # Descifrar el mensaje usando XOR
        try:
            mensaje_descifrado = ''.join(chr(ord(char) ^ clave) for char in mensaje_cifrado_xor)
        except Exception as e:
            return f"<h1>Error al descifrar con XOR: {e}</h1><a href='/'>Regresar</a>"

        return f"<h1>Mensaje decodificado: {mensaje_descifrado}</h1><a href='/'>Regresar</a>"

    return render_template('decodificar.html')



if __name__ == '__main__':
    app.run(debug=True)
