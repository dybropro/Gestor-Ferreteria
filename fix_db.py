import sqlite3

def fix():
    try:
        import database
        conn = database.conectar()
        cursor = conn.cursor()
        
        # Columnas faltantes para Clientes
        cols = [
            ("fecha_nacimiento", "TEXT"),
            ("ciudad", "TEXT"),
            ("etiquetas", "TEXT"),
            ("info_tributaria", "TEXT")
        ]
        
        print("Migrando Tabla Clientes...")
        for col, tipo in cols:
            try:
                cursor.execute(f"ALTER TABLE clientes ADD COLUMN {col} {tipo}")
                print(f" [+] Columna agregada: {col}")
            except Exception as e:
                if "duplicate" in str(e):
                    print(f" [.] Columna ya existe: {col}")
                else:
                    print(f" [!] Error en {col}: {e}")

        # Columnas para Ventas
        try:
            cursor.execute("ALTER TABLE ventas ADD COLUMN cliente_id INTEGER")
            print(" [+] Columna agregada: cliente_id en ventas")
        except Exception as e:
            pass

        conn.commit()
        conn.close()
        print("Migracion completada exitosamente.")
        
    except Exception as e:
        print(f"Error fatal: {e}")

if __name__ == "__main__":
    fix()
