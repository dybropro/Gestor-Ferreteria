import sqlite3
import csv
from datetime import datetime
from tkinter import messagebox
import os

def exportar_ventas_dia(parent_win=None):
    fecha_hoy = datetime.now().strftime("%Y-%m-%d") # Formato en BD suele ser YYYY-MM-DD

    conn = sqlite3.connect("ferreteria.db")
    cursor = conn.cursor()

    # Query para ventas del día
    query = """
        SELECT v.id, v.fecha, v.cliente, v.total, 
               p.codigo, p.nombre, d.cantidad, d.precio_unitario, (d.cantidad * d.precio_unitario) as subtotal
        FROM ventas v
        JOIN detalle_venta d ON v.id = d.venta_id
        JOIN productos p ON d.producto_id = p.id
        WHERE v.fecha LIKE ?
        ORDER BY v.id DESC
    """
    
    cursor.execute(query, (f"{fecha_hoy}%",))
    filas = cursor.fetchall()
    conn.close()

    if not filas:
        messagebox.showinfo("Reportes", "No hay ventas registradas hoy para exportar.", parent=parent_win)
        return

    # Nombre del archivo
    filename = f"Reporte_Ventas_{fecha_hoy}.csv"
    
    try:
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter=';') # ; para que Excel lo abra mejor en regiones con , decimal
            writer.writerow(["ID VENTA", "FECHA", "CLIENTE", "TOTAL VENTA", 
                             "CODIGO PROD", "PRODUCTO", "CANTIDAD", "PRECIO UNIT", "SUBTOTAL LINEA"])
            writer.writerows(filas)
            
        messagebox.showinfo("Éxito", f"Reporte generado: {filename}\n\nSe ha guardado en la carpeta del programa.", parent=parent_win)
        os.startfile(filename)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo generar el reporte: {e}", parent=parent_win)
