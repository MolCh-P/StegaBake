def encriptar_mensaje(mensaje, receta):
    # Convertir mensaje a código numérico
    codigo = [ord(char) for char in mensaje]
    
    # Reemplazar números en la receta
    receta_modificada = receta
    for i, numero in enumerate(codigo):
        receta_modificada = receta_modificada.replace(f'{{{i}}}', str(numero))
    
    return receta_modificada

# Ejemplo de receta con marcadores
receta_base = """
Receta: Pastel de Chocolate
Ingredientes:
- Harina: {0} tazas
- Azúcar: {1} tazas
- Leche: {2} tazas
Procedimiento:
1. Mezclar los ingredientes.
2. Hornear a 180°C durante {3} minutos.
"""
mensaje = "Hola"
receta_codificada = encriptar_mensaje(mensaje, receta_base)
print(receta_codificada)


# DECODIFICAR
def decodificar_mensaje(receta_codificada):
    # Extraer números de la receta
    import re
    numeros = re.findall(r'\d+', receta_codificada)
    
    # Convertir números a texto
    mensaje = ''.join([chr(int(num)) for num in numeros])
    return mensaje

# Decodificar la receta
mensaje_decodificado = decodificar_mensaje(receta_codificada)
print(mensaje_decodificado)
