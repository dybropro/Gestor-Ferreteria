import licensing
import sys

def menu():
    print("="*40)
    print("   DYBROCORP - KEY GENERATOR SYSTEM   ")
    print("="*40)
    
    machine_id = input("\n[1] Ingresa el Machine ID del cliente: ").strip().upper()
    
    if not machine_id:
        print("Error: Machine ID requerido.")
        return

    print("\n[2] Selecciona el periodo de activación:")
    print("1. 1 Mes")
    print("2. 3 Meses")
    print("3. 6 Meses")
    print("4. 12 Meses (1 Año)")
    print("5. Otro (Personalizado)")
    
    opcion = input("Opción: ")
    
    months = 0
    if opcion == "1": months = 1
    elif opcion == "2": months = 3
    elif opcion == "3": months = 6
    elif opcion == "4": months = 12
    elif opcion == "5":
        months = int(input("Ingresa cantidad de meses: "))
    else:
        print("Opción no válida.")
        return

    serial = licensing.generate_serial(machine_id, months)
    
    print("\n" + "*"*40)
    print(f"SERIAL GENERADO: {serial}")
    print("*"*40)
    print("\nInstrucciones:")
    print("Envía este código al cliente para activar su aplicación.")
    print("="*40)

if __name__ == "__main__":
    menu()
