import tkinter as tk
import utils
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

class ComprasWindow:
    def __init__(self, root):
        self.root = root
        utils.setup_window(self.root, "Gestión de Compras (Entrada de Inventario)", "1100x700")
        self.root.configure(bg="#f0f2f5")

        self.cart = []
        self.proveedor_id = None

        # --- Layout Principal ---
        main_frame = ttk.Frame(root, padding=20)
        main_frame.pack(fill="both", expand=True)

        # 1. Cabecera (Proveedor y Ref)
        header = ttk.Frame(main_frame, style="Card.TFrame", padding=15)
        header.pack(fill="x", pady=(0, 15))

        ttk.Label(header, text="Proveedor:", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w")
        self.combo_prov = ttk.Combobox(header, width=40, state="readonly")
        self.combo_prov.grid(row=1, column=0, padx=5, sticky="w")
        
        ttk.Label(header, text="N° Factura / Referencia:", font=("Segoe UI", 10, "bold")).grid(row=0, column=1, sticky="w")
        self.entry_ref = ttk.Entry(header, width=20)
        self.entry_ref.grid(row=1, column=1, padx=5, sticky="w")

        self.cargar_proveedores()

        # 2. Agregar Productos
        prod_frame = ttk.Frame(main_frame, style="Card.TFrame", padding=15)
        prod_frame.pack(fill="x", pady=(0, 15))

        ttk.Label(prod_frame, text="Buscar Producto:").pack(side=tk.LEFT)
        self.entry_search = ttk.Entry(prod_frame, width=30)
        self.entry_search.pack(side=tk.LEFT, padx=5)
        self.entry_search.bind("<Return>", self.buscar_producto)

        self.lbl_prod_sel = ttk.Label(prod_frame, text="Ninguno", font=("Segoe UI", 9, "italic"), foreground="blue")
        self.lbl_prod_sel.pack(side=tk.LEFT, padx=10)

        ttk.Label(prod_frame, text="Cant:").pack(side=tk.LEFT)
        self.entry_cant = ttk.Entry(prod_frame, width=8)
        self.entry_cant.pack(side=tk.LEFT, padx=5)
        self.entry_cant.insert(0, "1")

        ttk.Label(prod_frame, text="Costo Unitario:").pack(side=tk.LEFT)
        self.entry_costo = ttk.Entry(prod_frame, width=12)
        self.entry_costo.pack(side=tk.LEFT, padx=5)

        ttk.Button(prod_frame, text="Agregar (+)", command=self.agregar_item).pack(side=tk.LEFT, padx=10)

        # 3. Lista (Carrito de Compra)
        list_frame = ttk.Frame(main_frame, style="Card.TFrame")
        list_frame.pack(fill="both", expand=True, pady=(0, 15))

        cols = ("id", "producto", "cantidad", "costo", "subtotal")
        self.tree = ttk.Treeview(list_frame, columns=cols, show="headings", height=10)
        self.tree.heading("producto", text="Producto")
        self.tree.heading("cantidad", text="Cant")
        self.tree.heading("costo", text="Costo Unit")
        self.tree.heading("subtotal", text="Subtotal")
        
        self.tree.column("id", width=0, stretch=False)
        self.tree.pack(fill="both", expand=True)

        # 4. Footer
        footer = ttk.Frame(main_frame)
        footer.pack(fill="x")
        
        self.lbl_total = ttk.Label(footer, text="Total Compra: $0", font=("Segoe UI", 16, "bold"))
        self.lbl_total.pack(side=tk.RIGHT)
        
        ttk.Button(footer, text="GUARDAR COMPRA", style="Primary.TButton", command=self.guardar_compra).pack(side=tk.RIGHT, padx=20)
        
        # Variables temp
        self.temp_prod = None # (id, nombre, costo_actual)

    def conectar(self):
        return sqlite3.connect("ferreteria.db")

    def cargar_proveedores(self):
        self.map_prov = {}
        conn = self.conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT id, razon_social FROM proveedores")
        values = []
        for pid, name in cursor.fetchall():
            self.map_prov[name] = pid
            values.append(name)
        self.combo_prov['values'] = values
        conn.close()

    def buscar_producto(self, event):
        q = self.entry_search.get()
        conn = self.conectar()
        res = conn.execute("SELECT id, nombre, precio_compra FROM productos WHERE codigo LIKE ? OR nombre LIKE ?", (q, f"%{q}%")).fetchone()
        conn.close()
        
        if res:
            self.temp_prod = res
            self.lbl_prod_sel.config(text=res[1])
            self.entry_costo.delete(0, tk.END)
            self.entry_costo.insert(0, str(int(res[2])))
            self.entry_cant.focus()
        else:
            self.lbl_prod_sel.config(text="No encontrado")
            self.temp_prod = None

    def agregar_item(self):
        if not self.temp_prod: return
        
        try:
            cant = int(self.entry_cant.get())
            costo = float(self.entry_costo.get())
        except ValueError:
            messagebox.showwarning("Error", "Cantidad y Costo deben ser números", parent=self.root)
            return

        subtotal = cant * costo
        
        # Agregar a lista interna
        self.cart.append({
            "id": self.temp_prod[0],
            "nombre": self.temp_prod[1],
            "cantidad": cant,
            "costo": costo,
            "subtotal": subtotal
        })
        
        # Actualizar UI
        self.tree.insert("", tk.END, values=(self.temp_prod[0], self.temp_prod[1], cant, utils.formato_moneda(costo), utils.formato_moneda(subtotal)))
        self.actualizar_total()
        
        # Reset campos
        self.entry_search.delete(0, tk.END)
        self.entry_cant.delete(0, tk.END); self.entry_cant.insert(0, "1")
        self.entry_costo.delete(0, tk.END)
        self.lbl_prod_sel.config(text="Ninguno")
        self.temp_prod = None
        self.entry_search.focus()

    def actualizar_total(self):
        total = sum(i['subtotal'] for i in self.cart)
        self.lbl_total.config(text=f"Total Compra: {utils.formato_moneda(total)}")

    def guardar_compra(self):
        if not self.cart: return
        prov_name = self.combo_prov.get()
        if not prov_name:
            messagebox.showwarning("Error", "Seleccione un proveedor", parent=self.root)
            return
            
        prov_id = self.map_prov[prov_name]
        ref = self.entry_ref.get() or "S/R"
        total = sum(i['subtotal'] for i in self.cart)
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if not messagebox.askyesno("Confirmar", f"¿Registrar compra por {utils.formato_moneda(total)}? Esto aumentará el stock.", parent=self.root):
            return

        conn = self.conectar()
        try:
            # 1. Cabecera
            cursor = conn.execute("INSERT INTO compras (proveedor_id, fecha, total, factura_referencia) VALUES (?, ?, ?, ?)",
                         (prov_id, fecha, total, ref))
            compra_id = cursor.lastrowid
            
            # 2. Detalle y Movimiento de Inventario
            for item in self.cart:
                # Registro detalle
                conn.execute("INSERT INTO detalle_compra (compra_id, producto_id, cantidad, costo_unitario) VALUES (?, ?, ?, ?)",
                             (compra_id, item['id'], item['cantidad'], item['costo']))
                
                # ACTUALIZAR STOCK Y COSTO PROMEDIO/ULTIMO
                conn.execute("UPDATE productos SET stock = stock + ?, precio_compra = ? WHERE id = ?",
                             (item['cantidad'], item['costo'], item['id']))
            
            conn.commit()
            messagebox.showinfo("Éxito", "Compra registrada e inventario actualizado.", parent=self.root)
            self.root.destroy()
            
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Error", str(e), parent=self.root)
        finally:
            conn.close()

def abrir_ventana_compras():
    win = tk.Toplevel()
    app = ComprasWindow(win)
