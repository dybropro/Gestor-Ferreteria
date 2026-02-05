import sqlite3
import time

def debug_stock():
    try:
        import database
        conn = database.conectar()
        cur = conn.cursor()
        
        # 1. Crear producto de prueba
        codigo = f"TEST_{int(time.time())}"
        cur.execute("INSERT INTO productos (codigo, nombre, categoria, precio_compra, precio_venta, stock) VALUES (?,?,?,?,?,?)",
                   (codigo, "Producto Test", "Test", 100, 200, 10))
        prod_id = cur.lastrowid
        conn.commit()
        
        print(f"Producto creado. ID: {prod_id}, Stock Inicial: 10")
        
        # 2. Simular Venta (Descuento de stock)
        # Lógica exacta de ventas.py
        cant_vendida = 2
        print(f"Vendiendo {cant_vendida} unidades...")
        
        cur.execute("UPDATE productos SET stock = stock - ? WHERE id=?", (cant_vendida, prod_id))
        conn.commit()
        
        # 3. Verificar Stock
        cur.execute("SELECT stock FROM productos WHERE id=?", (prod_id,))
        new_stock = cur.fetchone()[0]
        
        print(f"Stock Final en DB: {new_stock}")
        
        if new_stock == 8:
            print("SUCCESS: El stock se descontó correctamente.")
        else:
            print(f"FAILURE: El stock debería ser 8, pero es {new_stock}")
            
        # Limpieza
        cur.execute("DELETE FROM productos WHERE id=?", (prod_id,))
        conn.commit()
        
        conn.close()
        
    except Exception as e:
        print(f"ERROR Fatal: {e}")

if __name__ == "__main__":
    debug_stock()
