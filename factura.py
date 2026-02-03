from reportlab.pdfgen import canvas
import utils
from reportlab.lib.units import mm
import sqlite3
import os

def generar_factura(carrito, total, venta_id, fecha, cliente_data="Público General", medio_pago="Efectivo", impuesto=0, subtotal=0):
    # Configuración de tamaño para impresora térmica de 80mm
    # Ancho 80mm (aprox 226 puntos)
    # Alto dinámico según items
    width = 80 * mm
    height = 190 * mm + (len(carrito) * 10 * mm) 
    
    nombre_archivo = f"ticket_venta_{venta_id}.pdf"

    c = canvas.Canvas(nombre_archivo, pagesize=(width, height))
    
    # Coordenadas iniciales
    y = height - 10 * mm
    x_margin = 5 * mm

    conn = sqlite3.connect("ferreteria.db")
    cursor = conn.cursor()
    
    # Obtener configuración
    config = {}
    keys = ["empresa_nombre", "empresa_nit", "empresa_direccion", "empresa_telefono"]
    for k in keys:
        cursor.execute("SELECT valor FROM configuracion WHERE clave=?", (k,))
        res = cursor.fetchone()
        config[k] = res[0] if res else ""
    conn.close()

    # Estilos cabecera
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(width/2, y, config.get("empresa_nombre", "FERRETERÍA"))
    y -= 5 * mm
    c.setFont("Helvetica", 8)
    c.drawCentredString(width/2, y, config.get("empresa_nit", ""))
    y -= 5 * mm
    c.drawCentredString(width/2, y, config.get("empresa_direccion", ""))
    y -= 4 * mm
    c.drawCentredString(width/2, y, config.get("empresa_telefono", ""))
    y -= 8 * mm
    
    c.setFont("Helvetica", 8)
    c.drawString(x_margin, y, f"Fecha: {fecha}")
    y -= 4 * mm
    c.drawString(x_margin, y, f"Ticket #: {venta_id}")
    y -= 6 * mm
    
    # Información Cliente
    c.setFont("Helvetica-Bold", 8)
    c.drawString(x_margin, y, "CLIENTE:")
    y -= 4 * mm
    c.setFont("Helvetica", 8)

    if isinstance(cliente_data, dict):
        c.drawString(x_margin, y, f"Nombre: {cliente_data.get('nombre', '')}")
        y -= 3.5 * mm
        c.drawString(x_margin, y, f"NIT/CC: {cliente_data.get('cedula', '')}")
        y -= 3.5 * mm
        c.drawString(x_margin, y, f"Tel: {cliente_data.get('telefono', '')}")
        y -= 3.5 * mm
        c.drawString(x_margin, y, f"Dir: {cliente_data.get('direccion', '')}")
    else:
        c.drawString(x_margin, y, str(cliente_data))
    
    y -= 6 * mm
    
    c.line(x_margin, y, width - x_margin, y)
    y -= 4 * mm
    
    # Encabezados de tabla
    c.setFont("Helvetica-Bold", 8)
    c.drawString(x_margin, y, "Cant")
    c.drawString(x_margin + 10*mm, y, "Prod")
    c.drawRightString(width - x_margin, y, "Total")
    y -= 4 * mm
    
    # Items
    c.setFont("Helvetica", 8)
    for item in carrito:
        nombre_corto = (item["nombre"][:20] + '..') if len(item["nombre"]) > 20 else item["nombre"]
        subtotal = item["precio"] * item["cantidad"]
        
        c.drawString(x_margin, y, str(item["cantidad"]))
        c.drawString(x_margin + 10*mm, y, nombre_corto)
        c.drawRightString(width - x_margin, y, utils.formato_moneda(subtotal))
        y -= 4 * mm
        
    c.line(x_margin, y, width - x_margin, y)
    y -= 6 * mm
    
    # Total
    c.setFont("Helvetica-Bold", 12)
    c.drawString(x_margin, y, "TOTAL A PAGAR:")
    c.drawRightString(width - x_margin, y, utils.formato_moneda(total))
    y -= 5 * mm

    # Desglose Impuestos
    c.setFont("Helvetica", 9)
    c.drawString(x_margin, y, "Subtotal:")
    c.drawRightString(width - x_margin, y, utils.formato_moneda(subtotal))
    y -= 4 * mm
    c.drawString(x_margin, y, "Impuestos (IVA):")
    c.drawRightString(width - x_margin, y, utils.formato_moneda(impuesto))
    y -= 6 * mm

    # Medio de Pago
    c.setFont("Helvetica-Bold", 9)
    c.drawString(x_margin, y, f"Medio de Pago: {medio_pago}")
    y -= 8 * mm
    
    c.setFont("Helvetica", 8)
    c.drawCentredString(width/2, y, "¡Gracias por su compra!")
    
    c.save()

    # Abrir factura automáticamente
    try:
        os.startfile(nombre_archivo)
    except Exception as e:
        print(f"Error al abrir PDF: {e}")
