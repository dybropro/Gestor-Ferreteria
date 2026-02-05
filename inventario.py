import tkinter as tk
import utils
from tkinter import ttk
import sqlite3

class InventarioWindow:
    def __init__(self, root):
        self.root = root
        utils.setup_window(self.root, "Inventario Valorizado y Alertas", "1100x700")
        self.root.configure(bg="#f0f2f5")

        # Header Stats
        stats_frame = ttk.Frame(root, padding=15)
        stats_frame.pack(fill="x")
        
        self.card_stock = self.create_stat_card(stats_frame, "Total Items", "0", 0)
        self.card_costo = self.create_stat_card(stats_frame, "Inversión (Costo)", "$0", 1)
        self.card_venta = self.create_stat_card(stats_frame, "Valor Venta (Potencial)", "$0", 2)
        self.card_ganancia = self.create_stat_card(stats_frame, "Ganancia Estimada", "$0", 3)

        # Filtros y Leyenda
        filter_frame = ttk.Frame(root, padding=10)
        filter_frame.pack(fill="x")
        
        ttk.Label(filter_frame, text="Leyenda: ").pack(side=tk.LEFT)
        self.create_legend(filter_frame, "🔴 Agotado (0)", "#ffcdd2")
        self.create_legend(filter_frame, "🟡 Bajo Stock", "#fff9c4")
        self.create_legend(filter_frame, "🟢 Disponible", "#c8e6c9")
        
        ttk.Button(filter_frame, text="Ver Solo Stock Bajo (Alertas)", command=self.filtrar_bajo_stock).pack(side=tk.RIGHT)
        ttk.Button(filter_frame, text="Ver Todo", command=self.cargar_datos).pack(side=tk.RIGHT, padx=10)

        # Tabla
        tree_frame = ttk.Frame(root, padding=10)
        tree_frame.pack(fill="both", expand=True)

        cols = ("codigo", "nombre", "stock", "min", "costo", "precio", "total_costo")
        self.tree = ttk.Treeview(tree_frame, columns=cols, show="headings")
        
        self.tree.heading("codigo", text="Cód")
        self.tree.heading("nombre", text="Producto")
        self.tree.heading("stock", text="Stock Actual")
        self.tree.heading("min", text="Mín (Alerta)")
        self.tree.heading("costo", text="Costo Unit")
        self.tree.heading("precio", text="Precio Venta")
        self.tree.heading("total_costo", text="Total Invertido")
        
        self.tree.column("codigo", width=80)
        self.tree.column("nombre", width=250)
        self.tree.column("stock", width=80, anchor="center")
        self.tree.column("min", width=80, anchor="center")
        
        # Tags de colores
        self.tree.tag_configure("agotado", background="#ffcdd2") # Rojo claro
        self.tree.tag_configure("bajo", background="#fff9c4")    # Amarillo claro
        self.tree.tag_configure("ok", background="#c8e6c9")      # Verde claro

        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", self.abrir_edicion_producto)
        
        self.cargar_datos()

    def abrir_edicion_producto(self, event):
        import productos
        item = self.tree.selection()
        if not item: return
        vals = self.tree.item(item)['values']
        codigo = vals[0] # Column 0 is codigo
        productos.abrir_ventana_productos(filtro_inicial=str(codigo))

    def create_stat_card(self, parent, title, value, col):
        frame = ttk.Frame(parent, style="Card.TFrame", padding=15)
        frame.grid(row=0, column=col, sticky="nsew", padx=10)
        parent.columnconfigure(col, weight=1)
        
        ttk.Label(frame, text=title, font=("Segoe UI", 10), foreground="#666").pack(anchor="w")
        val_lbl = ttk.Label(frame, text=value, font=("Segoe UI", 16, "bold"), foreground="#1a73e8")
        val_lbl.pack(anchor="w")
        return val_lbl

    def create_legend(self, parent, text, color):
        lbl = tk.Label(parent, text=text, bg=color, padx=10, pady=2, font=("Segoe UI", 9))
        lbl.pack(side=tk.LEFT, padx=5)

    def conectar(self): 
        import database
        return database.conectar()

    def cargar_datos(self, solo_bajo=False):
        for item in self.tree.get_children(): self.tree.delete(item)
        
        conn = self.conectar()
        # Traer todo y procesar en python
        # Se asume columnas: codigo, nombre, precio, precio_compra, stock, stock_minimo
        # Ajustar según esquema real
        cursor = conn.execute("SELECT codigo, nombre, precio_venta, precio_compra, stock, stock_minimo FROM productos")
        
        t_items = 0
        t_costo = 0
        t_venta = 0
        
        for row in cursor.fetchall():
            cod, nom, pre, cos, stk, min_stk = row
            stk = stk or 0
            cos = cos or 0
            pre = pre or 0
            min_stk = min_stk or 5 # Default visual
            
            # Calculos
            inversion = stk * cos
            potencial = stk * pre
            
            t_items += stk
            t_costo += inversion
            t_venta += potencial
            
            # Estado
            tag = "ok"
            if stk <= 0: tag = "agotado"
            elif stk <= min_stk: tag = "bajo"
            
            if solo_bajo and tag == "ok": continue
            
            self.tree.insert("", tk.END, values=(
                cod, nom, stk, min_stk, utils.formato_moneda(cos), utils.formato_moneda(pre), utils.formato_moneda(inversion)
            ), tags=(tag,))
            
        conn.close()
        
        # Update Stats
        self.card_stock.config(text=f"{t_items:,.0f}")
        self.card_costo.config(text=utils.formato_moneda(t_costo))
        self.card_venta.config(text=utils.formato_moneda(t_venta))
        self.card_ganancia.config(text=utils.formato_moneda(t_venta - t_costo))

    def filtrar_bajo_stock(self):
        self.cargar_datos(solo_bajo=True)

def abrir_ventana_inventario():
    t = tk.Toplevel()
    app = InventarioWindow(t)
