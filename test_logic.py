import sqlite3
import factura
import os
from datetime import datetime

def test_logic():
    print("Iniciando prueba de lógica de negocio...")
    
    # 1. Setup DB and Dummy Product
    import database
    conn = database.conectar()
    cursor = conn.cursor()
    
    # Ensure tables exist
    import database
    database.crear_tablas()
    
    # Create dummy product
    cursor.execute("DELETE FROM productos WHERE codigo='TEST001'")
    cursor.execute("INSERT INTO productos (codigo, nombre, categoria, precio_compra, precio_venta, stock) VALUES (?, ?, ?, ?, ?, ?)",
                   ('TEST001', 'Tuerca de Prueba', 'General', 100, 200, 50))
    prod_id = cursor.lastrowid
    print(f"Producto de prueba creado. ID: {prod_id}")
    
    conn.commit()
    
    # 2. Simulate Sale
    carrito = [{
        "id": prod_id,
        "codigo": "TEST001",
        "nombre": "Tuerca de Prueba",
        "precio": 200,
        "cantidad": 5
    }]
    total = 1000
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        # Register Sale
        cursor.execute("INSERT INTO ventas (fecha, total) VALUES (?, ?)", (fecha, total))
        venta_id = cursor.lastrowid
        print(f"Venta registrada. ID: {venta_id}")
        
        # Register Details & Update Stock
        for item in carrito:
            cursor.execute("INSERT INTO detalle_venta (venta_id, producto_id, cantidad, precio_unitario) VALUES (?, ?, ?, ?)",
                           (venta_id, item['id'], item['cantidad'], item['precio']))
            cursor.execute("UPDATE productos SET stock = stock - ? WHERE id = ?", (item['cantidad'], item['id']))
            
        conn.commit()
        print("Stock actualizado y detalle guardado.")
        
        # Verify Stock Update
        cursor.execute("SELECT stock FROM productos WHERE id=?", (prod_id,))
        new_stock = cursor.fetchone()[0]
        print(f"Nuevo stock (esperado 45): {new_stock}")
        assert new_stock == 45
        
        # 3. Generate Invoice
        print("Generando PDF de prueba...")
        # Mock os.startfile to avoid opening window during test, or just let it fail silently if not interactive
        original_startfile = os.startfile
        os.startfile = lambda x: print(f"Mock: Abriendo archivo {x}")
        
        factura.generar_factura(carrito, total, venta_id, fecha)
        
        # Check if file exists
        filename = f"ticket_venta_{venta_id}.pdf"
        if os.path.exists(filename):
            print(f"Archivo {filename} generado correctamente.")
            # os.remove(filename) # Clean up
        else:
            print(f"ERROR: Archivo {filename} no encontrado.")
            
        os.startfile = original_startfile
        
    except Exception as e:
        print(f"Prueba fallida: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    test_logic()
