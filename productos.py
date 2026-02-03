import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3

def abrir_ventana_productos(filtro_inicial=None):
    ventana = tk.Toplevel()
    ventana.title("Gestión de Productos")
    ventana.geometry("1000x600")
    # ventana.resizable(False, False) # Permitir redimensionar para la tabla

    # Variable para guardar el ID del producto seleccionado para edición
    producto_seleccionado_id = None

    # Auto-refrescar al volver a la ventana
    def on_focus(event):
        if event.widget == ventana:
            # Mantener filtro si existe
            try: cargar_productos(entry_buscar.get())
            except: cargar_productos()
            
    ventana.bind("<FocusIn>", on_focus)

    # ---- CONEXIÓN BD ----
    def conectar():
        return sqlite3.connect("ferreteria.db")

    # ---- FUNCIONES ----
    def limpiar_campos():
        nonlocal producto_seleccionado_id
        producto_seleccionado_id = None
        entry_codigo.delete(0, tk.END)
        entry_nombre.delete(0, tk.END)
        entry_categoria.delete(0, tk.END)
        entry_precio_compra.delete(0, tk.END)
        entry_precio_venta.delete(0, tk.END)
        entry_precio_venta.delete(0, tk.END)
        entry_stock.delete(0, tk.END)
        entry_min_stock.delete(0, tk.END)
        entry_min_stock.insert(0, "5") # Default
        entry_codigo.focus()
        btn_guardar.config(text="Guardar producto")

    def cargar_productos(filtro=""):
        # Limpiar tabla actual
        for item in tree.get_children():
            tree.delete(item)

        conexion = conectar()
        cursor = conexion.cursor()

        if filtro:
            sql = """
                SELECT id, codigo, nombre, categoria, precio_compra, precio_venta, stock, stock_minimo 
                FROM productos 
                WHERE nombre LIKE ? OR codigo LIKE ?
            """
            filtro_sql = f"%{filtro}%"
            cursor.execute(sql, (filtro_sql, filtro_sql))
        else:
            cursor.execute("SELECT id, codigo, nombre, categoria, precio_compra, precio_venta, stock, stock_minimo FROM productos")
        
        productos = cursor.fetchall()
        for prod in productos:
            # Color logic
            stock = prod[6] or 0
            min_stock = prod[7] or 5
            tag = "ok"
            if stock <= 0: tag = "agotado"
            elif stock <= min_stock: tag = "bajo"
            
            tree.insert("", tk.END, values=prod, tags=(tag,))
        
        conexion.close()

    def guardar_producto():
        codigo = entry_codigo.get()
        nombre = entry_nombre.get()
        categoria = entry_categoria.get()
        precio_compra = entry_precio_compra.get()
        precio_venta = entry_precio_venta.get()
        stock = entry_stock.get()
        stock_mimimo = entry_min_stock.get()

        if codigo == "" or nombre == "":
            messagebox.showerror("Error", "Código y nombre son obligatorios")
            return

        conexion = conectar()
        cursor = conexion.cursor()

        try:
            if producto_seleccionado_id:
                # MODO EDICIÓN
                cursor.execute("""
                    UPDATE productos 
                    SET codigo=?, nombre=?, categoria=?, precio_compra=?, precio_venta=?, stock=?, stock_minimo=?
                    WHERE id=?
                """, (codigo, nombre, categoria, precio_compra, precio_venta, stock, stock_mimimo, producto_seleccionado_id))
                messagebox.showinfo("Éxito", "Producto actualizado correctamente")
            else:
                # MODO CREACIÓN
                cursor.execute("""
                    INSERT INTO productos (codigo, nombre, categoria, precio_compra, precio_venta, stock, stock_minimo)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (codigo, nombre, categoria, precio_compra, precio_venta, stock, stock_mimimo))
                messagebox.showinfo("Éxito", "Producto registrado correctamente")
            
            conexion.commit()
            limpiar_campos()
            cargar_productos()

        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "El código de barras ya existe (o hay conflicto en base de datos).")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error: {e}")
        finally:
            conexion.close()

    def seleccionar_producto(event):
        nonlocal producto_seleccionado_id
        seleccion = tree.selection()
        if not seleccion:
            return
        
        item = tree.item(seleccion[0])
        valores = item['values']
        # valores orden: id, codigo, nombre, categoria, p_compra, p_venta, stock

        producto_seleccionado_id = valores[0]
        
        entry_codigo.delete(0, tk.END)
        entry_codigo.insert(0, valores[1])
        
        entry_nombre.delete(0, tk.END)
        entry_nombre.insert(0, valores[2])
        
        entry_categoria.delete(0, tk.END)
        entry_categoria.insert(0, valores[3])
        
        entry_precio_compra.delete(0, tk.END)
        entry_precio_compra.insert(0, valores[4])
        
        entry_precio_venta.delete(0, tk.END)
        entry_precio_venta.insert(0, valores[5])
        
        entry_stock.delete(0, tk.END)
        entry_stock.delete(0, tk.END)
        entry_stock.insert(0, valores[6])

        entry_min_stock.delete(0, tk.END)
        try: entry_min_stock.insert(0, valores[7]) 
        except: entry_min_stock.insert(0, "5") # Handle old rows

        btn_guardar.config(text="Actualizar producto")

    def eliminar_producto():
        seleccion = tree.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Seleccione un producto para eliminar")
            return
        
        item = tree.item(seleccion[0])
        valores = item['values']
        prod_id = valores[0]
        prod_nombre = valores[2]

        confirmacion = messagebox.askyesno("Confirmar", f"¿Está seguro de eliminar '{prod_nombre}'?")
        if confirmacion:
            conexion = conectar()
            cursor = conexion.cursor()
            cursor.execute("DELETE FROM productos WHERE id=?", (prod_id,))
            conexion.commit()
            conexion.close()
            messagebox.showinfo("Éxito", "Producto eliminado")
            limpiar_campos()
            cargar_productos()

    def buscar_producto(event=None): # event para binding de tecla
        filtro = entry_buscar.get()
        cargar_productos(filtro)

    # ---- UI LAYOUT ----
    # Estilos específicos (si no se heredan, aunque deberían por ser Toplevel)
    # Sin embargo, aseguramos fondo
    ventana.configure(bg="#f0f2f5")

    contenedor = ttk.Frame(ventana, padding=10)
    contenedor.pack(fill="both", expand=True)

    # Frame izquierdo (Formulario)
    frame_form = ttk.Frame(contenedor, style="Card.TFrame", padding=20)
    frame_form.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

    ttk.Label(frame_form, text="Detalles del Producto", style="Subheader.TLabel").pack(pady=(0, 15))

    # Grid para formulario
    form_grid = ttk.Frame(frame_form, style="Card.TFrame")
    form_grid.pack(fill="x")

    def crear_campo(parent, label_text, row):
        ttk.Label(parent, text=label_text).grid(row=row, column=0, sticky="w", pady=(5, 0))
        entry = ttk.Entry(parent, font=("Segoe UI", 10))
        entry.grid(row=row+1, column=0, sticky="ew", pady=(0, 10))
        return entry

    # Form fields
    entry_codigo = crear_campo(form_grid, "Código de barras", 0)
    entry_nombre = crear_campo(form_grid, "Nombre del producto", 2)
    entry_categoria = crear_campo(form_grid, "Categoría", 4)
    entry_precio_compra = crear_campo(form_grid, "Precio compra", 6)
    entry_precio_venta = crear_campo(form_grid, "Precio venta", 8)
    entry_stock = crear_campo(form_grid, "Stock Actual", 10)
    entry_min_stock = crear_campo(form_grid, "Stock Mínimo (Alerta)", 12)
    
    btn_guardar = ttk.Button(frame_form, text="Guardar producto", style="Primary.TButton", command=guardar_producto)
    btn_guardar.pack(fill=tk.X, pady=(20, 5))

    btn_limpiar = ttk.Button(frame_form, text="Limpiar formulario", command=limpiar_campos)
    btn_limpiar.pack(fill=tk.X, pady=5)

    btn_eliminar = ttk.Button(frame_form, text="Eliminar seleccionado", command=eliminar_producto)
    btn_eliminar.pack(fill=tk.X, pady=5)

    # Frame derecho (Tabla y Búsqueda)
    frame_lista = ttk.Frame(contenedor)
    frame_lista.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    # Buscador
    frame_buscar = ttk.Frame(frame_lista, style="Card.TFrame", padding=10)
    frame_buscar.pack(fill=tk.X, pady=(0, 10))
    
    ttk.Label(frame_buscar, text="🔍").pack(side=tk.LEFT, padx=(0, 5))
    entry_buscar = ttk.Entry(frame_buscar, font=("Segoe UI", 11))
    entry_buscar.pack(side=tk.LEFT, fill=tk.X, expand=True)
    entry_buscar.bind("<KeyRelease>", buscar_producto)
    entry_buscar.insert(0, "Buscar...")
    entry_buscar.bind("<FocusIn>", lambda e: entry_buscar.delete(0, tk.END) if entry_buscar.get() == "Buscar..." else None)

    # Tabla
    columnas = ("id", "codigo", "nombre", "categoria", "p_compra", "p_venta", "stock", "min")
    tree = ttk.Treeview(frame_lista, columns=columnas, show="headings", selectmode="browse")
    
    # Configurar encabezados
    tree.heading("id", text="ID")
    tree.heading("codigo", text="Código")
    tree.heading("nombre", text="Nombre")
    tree.heading("categoria", text="Categoría")
    tree.heading("p_compra", text="P. Compra")
    tree.heading("p_venta", text="P. Venta")
    tree.heading("stock", text="Stock")
    tree.heading("min", text="Mín")

    # Configurar columnas
    tree.column("id", width=30, anchor="center")
    tree.column("codigo", width=100)
    tree.column("nombre", width=150)
    tree.column("categoria", width=100)
    tree.column("p_compra", width=80)
    tree.column("p_venta", width=80)
    tree.column("stock", width=50, anchor="center")
    tree.column("min", width=50, anchor="center")
    
    # Tags Colors
    tree.tag_configure("agotado", background="#ffcdd2") 
    tree.tag_configure("bajo", background="#fff9c4")    
    tree.tag_configure("ok", background="white")

    # Scrollbar
    scrollbar = ttk.Scrollbar(frame_lista, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Evento de selección
    tree.bind("<<TreeviewSelect>>", seleccionar_producto)

    # Cargar datos iniciales
    if filtro_inicial:
        entry_buscar.delete(0, tk.END)
        entry_buscar.insert(0, filtro_inicial)
        cargar_productos(filtro_inicial)
    else:
        cargar_productos()
