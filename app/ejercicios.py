def crear_persona (nombre,edad):
    return { 
        "nombre" : nombre, 
        "edad" : edad     
    } 

def mayores_a_diez(numeros): 
    resultado = []
    for n in numeros:
        if n > 10: 
            resultado.append(n)
    return resultado
    
def dividir(a, b):
    try: 
        return a / b
    except ZeroDivisionError: 
        return "No se puede dividir por cero"
        