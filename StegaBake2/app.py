from flask import Flask, render_template, request, redirect, url_for, send_file
import os
import random

app = Flask(__name__) #Instancia de Flask que actúa como el servidor principal de la aplicación

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
        
        # Verificar que la clave sea válida
        if not clave.isdigit():
            return "<h1>Error: La clave debe ser un número.</h1><a href='/'>Regresar</a>"
        
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
        
        # Verificar que la clave sea válida
        if not clave.isdigit():
            return "<h1>Error: La clave debe ser un número.</h1><a href='/'>Regresar</a>"
        
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


# Función para encriptar mensaje
def cifrado_xor(texto, clave):
    """
    Aplica un cifrado XOR al texto usando la clave proporcionada.
    """
    return ''.join(chr(ord(char) ^ clave) for char in texto)

def encriptar_mensaje(mensaje, plantilla_receta, clave):
    """
    Cifra el mensaje usando XOR con una clave proporcionada por el usuario.
    """
    # Convertir la clave a un entero si no lo es
    clave = int(clave)
    
    # Aplicar cifrado XOR
    mensaje_cifrado = cifrado_xor(mensaje, clave)
    
    # Convertir el mensaje cifrado a códigos ASCII
    codigo = [str(ord(char)) for char in mensaje_cifrado]
    
    ingredientes = plantilla_receta.split('\n')
    receta_codificada = []

    codigo_index = 0
    for linea in ingredientes:
        if '{cantidad}' in linea:
            if codigo_index < len(codigo):
                receta_codificada.append(linea.replace('{cantidad}', codigo[codigo_index]))
                codigo_index += 1
            else:
                numero_aleatorio = random.randint(32, 500)
                receta_codificada.append(linea.replace('{cantidad}', str(numero_aleatorio)))
        else:
            receta_codificada.append(linea)
    
    return '\n'.join(receta_codificada)

def decodificar_receta(receta, clave):
    """
    Decodifica una receta cifrada usando XOR con la clave proporcionada.
    """
    # Convertir la clave a un entero si no lo es
    clave = int(clave)
    
    lineas = receta.split('\n')
    codigo = []
    for linea in lineas:
        palabras = linea.split()
        for palabra in palabras:
            if palabra.isdigit():
                codigo.append(chr(int(palabra)))
    
    # Reconstruir el mensaje cifrado y descifrarlo
    mensaje_cifrado = ''.join(codigo)
    mensaje = cifrado_xor(mensaje_cifrado, clave)
    
    return mensaje


if __name__ == '__main__':
    app.run(debug=True)
