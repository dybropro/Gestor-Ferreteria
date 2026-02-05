import factura
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
import utils
import sqlite3

def abrir_ventana_ventas(rol_usuario="vendedor"):
    # Definir ventana y estilos dentro de la función o usar estilos globales si ya existen
    ventana = tk.Toplevel()
    utils.setup_window(ventana, "Punto de Venta Profesional")
    ventana.state('zoomed')
    ventana.configure(bg="#f0f2f5")

    # Variables de estado
    carrito = []
    
    # Cargar Configuración de Impuestos
    impuesto_pct = 0
    try:
        import database
        conn = database.conectar()
        cur = conn.cursor()
        cur.execute("SELECT valor FROM configuracion WHERE clave='impuesto_porcentaje'")
        res = cur.fetchone()
        if res: impuesto_pct = float(res[0])
        conn.close()
    except: pass
    
    # Variable global (en closure) para cliente
    cliente_actual_id = None
    cliente_data_completa = {}

    # ---- FUNCIONES LÓGICAS ----

    def buscar_producto(event=None):
        busqueda = entry_busqueda.get()
        if busqueda == "": return

        import database
        conexion = database.conectar()
        cursor = conexion.cursor()

        # 1. Buscar por código exacto
        cursor.execute("SELECT id, nombre, precio_venta, stock, codigo FROM productos WHERE codigo=?", (busqueda,))
        producto = cursor.fetchone()

        # 2. Si no, buscar por nombre
        if not producto:
             cursor.execute("SELECT id, nombre, precio_venta, stock, codigo FROM productos WHERE nombre LIKE ?", (f'%{busqueda}%',))
             resultados = cursor.fetchall()
             if len(resultados) == 1:
                 producto = resultados[0]
             elif len(resultados) > 1:
                 seleccionar_producto(resultados)
                 conexion.close()
                 return

        conexion.close()

        if producto:
            agregar_al_carrito(producto)
            entry_busqueda.delete(0, tk.END)
        else:
            messagebox.showerror("Error", "Producto no encontrado", parent=ventana)

    def seleccionar_producto(resultados):
        top = tk.Toplevel(ventana)
        top.title("Seleccionar")
        top.geometry("500x300")
        
        tree = ttk.Treeview(top, columns=("nombre", "precio"), show="headings")
        tree.heading("nombre", text="Producto"); tree.column("nombre", width=300)
        tree.heading("precio", text="Precio"); tree.column("precio", width=100)
        tree.pack(fill="both", expand=True)
        
        for p in resultados:
            tree.insert("", tk.END, values=(p[1], utils.formato_moneda(p[2])), tags=(str(p[0]),)) # store ID in tag or map
            # Better: store full obj in specific dict or list map, but index logic works too
            
        # Map back to results
        result_map = {str(p[1]): p for p in resultados} # Map by name (risky if duplicates) - use index
        
        # Simple listbox alternative approach used in previous version was removed, 
        # using treeview for consistency but simpler to bind selection
        def on_select(evt):
            sel = tree.selection()
            if not sel: return
            item = tree.item(sel[0])
            # Find in results (inefficient but safe for small lists)
            for p in resultados:
                if p[1] == item['values'][0]:
                    agregar_al_carrito(p)
                    top.destroy()
                    entry_busqueda.delete(0, tk.END)
                    return
        
        tree.bind("<Double-1>", on_select)

    def agregar_al_carrito(producto):
        id_prod, nombre, precio, stock, codigo = producto

        if stock <= 0:
            if not messagebox.askyesno("Alerta Stock", f"El producto '{nombre}' no tiene stock (0). ¿Agregar de todas formas?", parent=ventana):
                return
        
        # Check stock mínimo alert
        # (Optional: Query stock_mimimo if needed)

        # check duplicate
        for item in carrito:
            if item['id'] == id_prod:
                item['cantidad'] += 1
                actualizar_lista()
                return

        carrito.append({
            "id": id_prod, "codigo": codigo, "nombre": nombre,
            "precio": precio, "cantidad": 1
        })
        actualizar_lista()

    def buscar_cliente_bd(event=None):
        nonlocal cliente_actual_id, cliente_data_completa
        query = entry_cliente.get().strip()
        if not query: return
        
        import database
        conn = database.conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT id, cedula, nombre, telefono, direccion FROM clientes WHERE cedula = ? OR nombre LIKE ?", (query, f"%{query}%"))
        res = cursor.fetchone()
        conn.close()
        
        if res:
            cliente_actual_id = res[0]
            entry_cliente.delete(0, tk.END)
            entry_cliente.insert(0, res[2])
            cliente_data_completa = {"cedula": res[1], "nombre": res[2], "telefono": res[3], "direccion": res[4]}
            lbl_info_cliente.config(text=f"NIT: {res[1]} | Tel: {res[3]}", foreground="green")
        else:
            cliente_actual_id = None
            lbl_info_cliente.config(text="Cliente Nuevo / Casual", foreground="#666")

    def actualizar_lista():
        for i in tree_cart.get_children(): tree_cart.delete(i)
        
        subtotal_venta = 0
        for item in carrito:
            sub = item['precio'] * item['cantidad']
            tree_cart.insert("", tk.END, values=(item['nombre'], item['cantidad'], utils.formato_moneda(item['precio']), utils.formato_moneda(sub)))
            subtotal_venta += sub
        
        val_imp = subtotal_venta * (impuesto_pct / 100)
        total = subtotal_venta + val_imp
        
        lbl_subtotal.config(text=f"Subtotal: {utils.formato_moneda(subtotal_venta)}")
        lbl_impuesto.config(text=f"Impuesto ({impuesto_pct}%): {utils.formato_moneda(val_imp)}")
        label_total.config(text=utils.formato_moneda(total))

    def modificar_cantidad(event):
        item = tree_cart.selection()
        if not item: return
        idx = tree_cart.index(item[0])
        
        prod = carrito[idx]
        new_cant = simpledialog.askinteger("Cantidad", f"Nueva cantidad para {prod['nombre']}:", 
                                           initialvalue=prod['cantidad'], minvalue=1)
        if new_cant:
            # Validar stock real BD
            import database
            conn = database.conectar()
            cur = conn.cursor()
            cur.execute("SELECT stock from productos WHERE id=?", (prod['id'],))
            s = cur.fetchone()[0]
            conn.close()
            
            if new_cant > s:
                messagebox.showwarning("Stock Insuficiente", f"Solo hay {s} unidades disponibles.", parent=ventana)
                return

            carrito[idx]['cantidad'] = new_cant
            actualizar_lista()

    def eliminar_item(event):
        if rol_usuario != "admin":
            messagebox.showerror("Acceso Denegado", "Solo el ADMINISTRADOR puede eliminar items del carrito.", parent=ventana)
            return

        item = tree_cart.selection()
        if not item: return
        
        idx = tree_cart.index(item[0])
        prod_name = carrito[idx]['nombre']
        
        if messagebox.askyesno("Confirmar", f"¿Eliminar '{prod_name}' del carrito?", parent=ventana):
            del carrito[idx]
            actualizar_lista()

    def finalizar_venta(es_credito=False):
        nonlocal cliente_actual_id, cliente_data_completa
        if not carrito: return messagebox.showwarning("Error", "Carrito vacio", parent=ventana)
        
        # Recalcular
        subtotal = sum(i['precio']*i['cantidad'] for i in carrito)
        impuesto = subtotal * (impuesto_pct/100)
        total = subtotal + impuesto
        
        medio = "Crédito" if es_credito else combo_pago.get()
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cli_nombre = entry_cliente.get().strip() or "Público General"
        
        if es_credito:
            if not cliente_actual_id: return messagebox.showerror("Error", "Debe seleccionar un cliente para fiar", parent=ventana)
            if not messagebox.askyesno("Confirmar", f"¿Fiar venta por {utils.formato_moneda(total)}?", parent=ventana): return

        import database
        conn = database.conectar()
        try:
            # Venta Header
            cur = conn.execute("""INSERT INTO ventas (fecha, total, cliente, cliente_id, metodo_pago, impuesto) 
                                VALUES (?,?,?,?,?,?)""", (fecha, total, cli_nombre, cliente_actual_id, medio, impuesto))
            vid = cur.lastrowid
            
            # Detalle
            for i in carrito:
                conn.execute("INSERT INTO detalle_venta (venta_id, producto_id, cantidad, precio_unitario) VALUES (?,?,?,?)",
                             (vid, i['id'], i['cantidad'], i['precio']))
                # Descontar stock
                conn.execute("UPDATE productos SET stock = stock - ? WHERE id=?", (i['cantidad'], i['id']))
            
            # Credito
            if es_credito:
                conn.execute("""INSERT INTO creditos (cliente_id, venta_id, fecha_inicio, monto_total, saldo_pendiente, estado)
                                VALUES (?,?,?,?,?,'PENDIENTE')""", (cliente_actual_id, vid, fecha[:10], total, total))
            
            conn.commit()
            
            # PDF
            datos = cliente_data_completa if cliente_data_completa else {"nombre": cli_nombre}
            factura.generar_factura(carrito, total, vid, fecha, datos, medio, impuesto, subtotal)
            
            messagebox.showinfo("OK", "Venta registrada", parent=ventana)
            
            # Reset
            carrito.clear()
            actualizar_lista()
            entry_cliente.delete(0, tk.END)
            lbl_info_cliente.config(text="")
            cliente_actual_id = None 
            cliente_data_completa = {}
            
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Error", str(e), parent=ventana)
        finally:
            conn.close()

    # ---- INTERFAZ GRAFICA ----
    main_frame = ttk.Frame(ventana, padding=20)
    main_frame.pack(fill="both", expand=True)

    # 1. Header
    header = ttk.Frame(main_frame, style="Card.TFrame", padding=15)
    header.pack(fill="x", pady=(0,15))
    
    # Cliente
    f_cli = ttk.Frame(header)
    f_cli.pack(side=tk.LEFT, fill="x", expand=True, padx=(0,10))
    ttk.Label(f_cli, text="Cliente (Buscar):").pack(anchor="w")
    entry_cliente = ttk.Entry(f_cli, font=("Segoe UI", 11)); entry_cliente.pack(fill="x")
    entry_cliente.bind("<Return>", buscar_cliente_bd); entry_cliente.bind("<FocusOut>", buscar_cliente_bd)
    lbl_info_cliente = ttk.Label(f_cli, text=""); lbl_info_cliente.pack(anchor="w")

    # Prod
    f_prod = ttk.Frame(header)
    f_prod.pack(side=tk.LEFT, fill="x", expand=True)
    ttk.Label(f_prod, text="Buscar Producto:").pack(anchor="w")
    entry_busqueda = ttk.Entry(f_prod, font=("Segoe UI", 11)); entry_busqueda.pack(fill="x")
    entry_busqueda.bind("<Return>", lambda event: buscar_producto())
    entry_busqueda.focus_set()

    # 2. Lista
    list_frame = ttk.Frame(main_frame, style="Card.TFrame")
    list_frame.pack(fill="both", expand=True, pady=(0,15))
    
    tree_cart = ttk.Treeview(list_frame, columns=("nombre", "cant", "precio", "sub"), show="headings")
    tree_cart.heading("nombre", text="Producto"); tree_cart.column("nombre", width=300)
    tree_cart.heading("cant", text="Cant"); tree_cart.column("cant", width=50, anchor="center")
    tree_cart.heading("precio", text="Precio"); tree_cart.column("precio", width=100, anchor="e")
    tree_cart.heading("sub", text="Subtotal"); tree_cart.column("sub", width=100, anchor="e")
    tree_cart.pack(side=tk.LEFT, fill="both", expand=True)
    
    scrol = ttk.Scrollbar(list_frame, command=tree_cart.yview); scrol.pack(side=tk.RIGHT, fill="y")
    tree_cart.config(yscroll=scrol.set)
    
    # Bindings para edición
    tree_cart.bind("<Double-1>", modificar_cantidad)
    tree_cart.bind("<Delete>", eliminar_item)
    # Menu contextual click derecho
    menu_context = tk.Menu(ventana, tearoff=0)
    menu_context.add_command(label="✏️ Cambiar Cantidad", command=lambda: modificar_cantidad(None))
    menu_context.add_command(label="❌ Eliminar (Admin)", command=lambda: eliminar_item(None))
    
    def show_popup(event):
        try: 
            tree_cart.selection_set(tree_cart.identify_row(event.y))
            menu_context.tk_popup(event.x_root, event.y_root)
        finally: 
            menu_context.grab_release()

    tree_cart.bind("<Button-3>", show_popup)

    # 3. Footer
    footer = ttk.Frame(main_frame)
    footer.pack(fill="x")
    
    # Left controls
    ctrl = ttk.Frame(footer)
    ctrl.pack(side=tk.LEFT)
    ttk.Label(ctrl, text="Pago:").pack(side=tk.LEFT)
    combo_pago = ttk.Combobox(ctrl, values=["Efectivo", "Tarjeta", "Transferencia"], state="readonly", width=12)
    combo_pago.current(0); combo_pago.pack(side=tk.LEFT, padx=5)
    
    ttk.Button(ctrl, text="Cancelar Carrito", command=lambda: [carrito.clear(), actualizar_lista()]).pack(side=tk.LEFT, padx=10)
    
    style = ttk.Style()
    style.configure("W.TButton", background="#ff9800", foreground="white", font=("Segoe UI", 10, "bold"))
    ttk.Button(ctrl, text="FIAR / CRÉDITO", style="W.TButton", command=lambda: finalizar_venta(True)).pack(side=tk.LEFT, padx=10)
    ttk.Button(ctrl, text="PAGAR (F5)", style="Primary.TButton", command=lambda: finalizar_venta(False)).pack(side=tk.LEFT)
    
    # Right totals
    tot = ttk.Frame(footer, style="Card.TFrame", padding=10)
    tot.pack(side=tk.RIGHT)
    lbl_subtotal = ttk.Label(tot, text="Sub: $0"); lbl_subtotal.pack(anchor="e")
    lbl_impuesto = ttk.Label(tot, text=f"IVA ({impuesto_pct}%): $0"); lbl_impuesto.pack(anchor="e")
    label_total = ttk.Label(tot, text="$0", font=("Segoe UI", 20, "bold"), foreground="#1a73e8"); label_total.pack(anchor="e")

    ventana.bind("<F5>", lambda e: finalizar_venta(False))
