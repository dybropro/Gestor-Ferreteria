import licensing
import sys

import os

def menu():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("="*40)
        print("   DYBROCORP - KEY GENERATOR SYSTEM   ")
        print("="*40)
        
        machine_id = input("\n[1] Ingresa el Machine ID del cliente (o 'S' para salir): ").strip().upper()
        
        if machine_id == 'S':
            break

        if not machine_id:
            print("Error: Machine ID requerido.")
            input("\nPresiona Enter para continuar...")
            continue

        print("\n[2] Selecciona el periodo de activación:")
        print("1. 7 Días (Prueba)")
        print("2. 15 Días (Prueba)")
        print("3. 1 Mes")
        print("4. 3 Meses")
        print("5. 6 Meses")
        print("6. 12 Meses (1 Año)")
        print("7. Otro (Personalizado en Meses)")
        print("8. Otro (Personalizado en Días)")
        
        opcion = input("Opción: ")
        
        try:
            duration = 0
            unit = 'M'
            if opcion == "1": duration = 7; unit = 'D'
            elif opcion == "2": duration = 15; unit = 'D'
            elif opcion == "3": duration = 1; unit = 'M'
            elif opcion == "4": duration = 3; unit = 'M'
            elif opcion == "5": duration = 6; unit = 'M'
            elif opcion == "6": duration = 12; unit = 'M'
            elif opcion == "7":
                duration = int(input("Ingresa cantidad de MESES: "))
                unit = 'M'
            elif opcion == "8":
                duration = int(input("Ingresa cantidad de DÍAS: "))
                unit = 'D'
            else:
                print("Opción no válida.")
                input("\nPresiona Enter para continuar...")
                continue
        except ValueError:
            print("Error: Ingresa un número válido para los meses/días.")
            input("\nPresiona Enter para continuar...")
            continue

        serial = licensing.generate_serial(machine_id, duration, unit)
        
        print("\n" + "*"*40)
        print(f"SERIAL GENERADO: {serial}")
        print("*"*40)
        
        # Intentar copiar al portapapeles en Windows
        try:
            os.system(f"echo {serial} | clip")
            print("\n[¡ÉXITO!] El código ha sido copiado al portapapeles automáticamente.")
        except:
            pass

        print("\nInstrucciones:")
        print("Envía este código al cliente para activar su aplicación.")
        print("="*40)
        
        if input("\n¿Deseas generar otro código? (S/N): ").strip().upper() != 'S':
            break

if __name__ == "__main__":
    menu()
    print("\nGracias por usar el sistema de DybroCorp.")
    input("Presiona Enter para cerrar...")
