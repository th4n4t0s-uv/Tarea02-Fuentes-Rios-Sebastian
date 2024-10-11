# Ricardo Gil, Esteban Quinteros, Sebastián Fuentes
import requests
import getopt
import sys
import os
import time

URL_API = "https://api.maclookup.app/v2/macs/"

def obtener_fabricante_mac(mac): # Esta función obtiene el nombre del fabricante asociado a una dirección MAC, utilizando una API externa para realizar la consulta
    tiempo_inicio = time.time()  # Inicio del temporizador
    try:
        respuesta = requests.get(URL_API + mac) # Se realiza una solicitud a la URL de la API, concatenando la dirección MAC al final de la URL.
        respuesta.raise_for_status() # Comprobación del estado de respuesta. En caso de que la solicitud HTTP falle, entrega una excepción.
        datos = respuesta.json() # Formato JSON para obtener los datos; la API devolverá un diccionario JSON con información del fabricante.
        tiempo_fin = time.time() # Fin del temporizador
        tiempo_respuesta = int((tiempo_fin - tiempo_inicio) * 1000) # Se entrega el tiempo de respuesta en ms

        # Verificación si existe el campo "company" en la respuesta
        if 'company' in datos and datos['company']: # Si se encuentra la clave 'company' dentro de los datos, indica que se obtuvo la información del fabricante correctamente.
            return datos['company'], tiempo_respuesta
        else: # Si no se encuentra la clave 'company' o si la MAC es inválida o no está en la base de datos, significa que la API no pudo asociar la dirección MAC a un fabricante.
            return "Fabricante no encontrado", tiempo_respuesta
    except requests.RequestException as e:
        return f"Error en la solicitud: {e}", None
     # En caso de que la API falle se entrega un mensaje de error, junto con un "none" como espacio vacio en el tiempo de respuesta

def mostrar_ayuda(): # Se muestra indicaciones de uso del programa
    print("Uso: OUILookup.py --mac <mac> | --arp | [--help]")
    print("--mac: MAC a consultar. Ej: aa:bb:cc:00:00:00.")
    print("--arp: Muestra los fabricantes de los host disponibles en la tabla ARP.")
    print("--help: Muestra este mensaje y termina.")

def obtener_tabla_arp(): # Ejecuta el comando arp para obtener las direcciones MAC desde la tabla ARP y devolverlas en una lista.
    if os.name == "nt":  # Para dispositivos Windows
        salida_arp = os.popen('arp -a').read()
    
    mac_addresses = [] # Se crea una lista vacia, donde se almacenarán las direcciones MAC que se encuentren en la tabla ARP.

    for linea in salida_arp.splitlines():
        if os.name == "nt": # En Windows, las MAC suelen estar en la columna 2
            partes = linea.split()
            if len(partes) >= 2 and '-' in partes[1]:
                mac_addresses.append(partes[1].replace('-', ':'))  # Se cambia '-' por ':' para estandarizar
    
    return mac_addresses


def main(): # Función principal para la ejecución del programa; procesa los argumentos dados por la línea de comandos
    # e interpreta qué funcion utilizar dependiendo de lo que desea el usuario.
    try:
        opciones, argumentos = getopt.getopt(sys.argv[1:], "", ["mac=", "arp", "help"])
    except getopt.GetoptError as error: # Si el usuario ingresa una opción no valida o con errores de sintaxis, se captura el error,
        # se detiene el programa y se muestra el error asociado.
        print(error)
        sys.exit(2)
    
    if not opciones: # En caso de que el usuario no ingrese ninguna opción se ejecuta la funcion de ayuda nuevamente.
        mostrar_ayuda()
        sys.exit(2)

    for opcion, argumento in opciones: # Bucle que recorre las opciones y argumentos proporcionados
        if opcion == "--mac": # Consulta el fabricante de una dirección MAC
            direccion_mac = argumento
            fabricante, tiempo_respuesta = obtener_fabricante_mac(direccion_mac)
            print(f"Dirección MAC: {direccion_mac}")
            print(f"Fabricante: {fabricante}")
            if tiempo_respuesta:
                print(f"Tiempo de respuesta: {tiempo_respuesta} ms")
            #Se indica en pantalla la dirección MAC, el nombre del fabricante asociado a la MAC y el tiempo de respuesta válido
        elif opcion == "--arp": # Se utiliza para obtener una tabla ARP local con las direcciones físicas y sus fabricantes
            direcciones_mac = obtener_tabla_arp()
            if not direcciones_mac: # En caso de no encontrar direcciones MAC
                print("No se encontraron direcciones MAC en la tabla ARP.")
                sys.exit(1)
            print("MAC/Fabricante:")
            for mac in direcciones_mac:
                fabricante, _ = obtener_fabricante_mac(mac)
                print(f"{mac} / {fabricante}")
        elif opcion == "--help": # Se utiliza para mostrar el menú de ayuda de instrucciones del programa
            mostrar_ayuda()

if __name__ == "__main__":
    main()