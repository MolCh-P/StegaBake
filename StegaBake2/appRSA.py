from flask import Flask, render_template, request, redirect, url_for, send_file
import os
import random

# Generación de claves RSA manualmente
def generar_claves():
    # Elegimos dos números primos grandes
    p = 61  # Primer número primo
    q = 53  # Segundo número primo
    
    # Calculamos n y φ(n)
    n = p * q
    phi_n = (p - 1) * (q - 1)
    
    # Elegimos e (debe ser coprimo con φ(n))
    e = 17  # 17 es un número pequeño que es coprimo con φ(n)
    
    # Calculamos d (inverso de e mod φ(n))
    d = mod_inverse(e, phi_n)
    
    # Claves pública y privada
    public_key = (e, n)
    private_key = (d, n)
    
    return public_key, private_key

def mod_inverse(a, m):
    """
    Calcula el inverso multiplicativo de a mod m usando el algoritmo extendido de Euclides.
    """
    m0, x0, x1 = m, 0, 1
    while a > 1:
        q = a // m
        m, a = a % m, m
        x0, x1 = x1 - q * x0, x0
    if x1 < 0:
        x1 += m0
    return x1

def encriptar_rsa(mensaje, clave_publica):
    """
    Encripta el mensaje usando RSA con la clave pública.
    """
    e, n = clave_publica
    mensaje_cifrado = [pow(ord(c), e, n) for c in mensaje]
    return mensaje_cifrado

def desencriptar_rsa(mensaje_cifrado, clave_privada):
    """
    Desencripta el mensaje usando RSA con la clave privada.
    """
    d, n = clave_privada
    mensaje_descifrado = ''.join([chr(pow(c, d, n)) for c in mensaje_cifrado])
    return mensaje_descifrado

# Instancia de Flask
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
        filepath = "recetario.txt"
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
    mensaje_cifrado_xor = cifrado_xor(mensaje, clave)
    
    # Generar claves RSA
    clave_publica, clave_privada = generar_claves()

    # Encriptar el mensaje con RSA
    mensaje_cifrado_rsa = encriptar_rsa(mensaje_cifrado_xor, clave_publica)

    # Convertir el mensaje cifrado a códigos (como antes con XOR)
    codigo = [str(num) for num in mensaje_cifrado_rsa]

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
                codigo.append(int(palabra))
    
    # Desencriptar el mensaje con RSA
    clave_publica, clave_privada = generar_claves()
    mensaje_cifrado_rsa = codigo
    mensaje_cifrado_xor = desencriptar_rsa(mensaje_cifrado_rsa, clave_privada)

    # Desencriptar el mensaje con XOR
    mensaje = cifrado_xor(mensaje_cifrado_xor, clave)
    
    return mensaje

if __name__ == '__main__':
    app.run(debug=True)
