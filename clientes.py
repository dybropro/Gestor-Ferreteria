import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime, timedelta

class ClientesWindow:
    def __init__(self, root):
        self.root = root
        utils.setup_window(self.root, "CRM & Gestión de Clientes 360", "1100x700")
        self.root.configure(bg="#f0f2f5")
        
        self.selected_id = None
        
        # --- TAB CONTROLLER ---
        self.tabs = ttk.Notebook(root)
        self.tabs.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Tab 1: Base de Datos (CRUD)
        self.tab_db = ttk.Frame(self.tabs)
        self.tabs.add(self.tab_db, text="📇 Base de Clientes")
        
        # Tab 2: Inteligencia (RFM & Historial)
        self.tab_crm = ttk.Frame(self.tabs)
        self.tabs.add(self.tab_crm, text="📊 Inteligencia & Historial")
        
        self.setup_tab_db()
        self.setup_tab_crm()
        
        self.cargar_datos()

    # ==========================
    # TAB 1: GESTIÓN DE DATOS
    # ==========================
    def setup_tab_db(self):
        main = ttk.Frame(self.tab_db, padding=10)
        main.pack(fill="both", expand=True)
        
        # Split Panels
        left = ttk.Frame(main, style="Card.TFrame", padding=15)
        left.pack(side=tk.LEFT, fill="y", padx=(0,10))
        
        right = ttk.Frame(main)
        right.pack(side=tk.RIGHT, fill="both", expand=True)
        
        # Formulario
        ttk.Label(left, text="Perfil Cliente", font=("Segoe UI", 12, "bold")).pack(pady=(0,15))
        
        self.entries = {}
        campos = [
            ("Nombre Completo", "nombre"),
            ("Cédula / NIT", "cedula"),
            ("Teléfono", "telefono"),
            ("Dirección", "direccion"),
            ("Ciudad / Ubicación", "ciudad"),
            ("Cumpleaños (DD/MM)", "fecha_nacimiento"),
            ("Info. Tributaria", "info_tributaria"),
            ("Etiquetas (Tags)", "etiquetas")
        ]
        
        for lbl, key in campos:
            ttk.Label(left, text=lbl).pack(anchor="w")
            e = ttk.Entry(left, width=35)
            e.pack(pady=(0, 8))
            self.entries[key] = e
            
        btn_frame = ttk.Frame(left)
        btn_frame.pack(fill="x", pady=20)
        ttk.Button(btn_frame, text="GUARDAR", style="Primary.TButton", command=self.guardar).pack(fill="x", pady=5)
        ttk.Button(btn_frame, text="Limpiar", command=self.limpiar).pack(fill="x")
        ttk.Button(btn_frame, text="Ir a Análisis CRM >>", command=lambda: self.tabs.select(1)).pack(fill="x", pady=(20,0))
        
        # Lista
        cols = ("id", "cedula", "nombre", "telefono", "ciudad", "tags")
        self.tree = ttk.Treeview(right, columns=cols, show="headings")
        self.tree.heading("cedula", text="Doc"); self.tree.column("cedula", width=90)
        self.tree.heading("nombre", text="Nombre Cliente"); self.tree.column("nombre", width=200)
        self.tree.heading("telefono", text="Tel"); self.tree.column("telefono", width=90)
        self.tree.heading("ciudad", text="Ciudad"); self.tree.column("ciudad", width=90)
        self.tree.heading("tags", text="Etiquetas"); self.tree.column("tags", width=120)
        self.tree.column("id", width=0, stretch=False)
        
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.seleccionar)

    # ==========================
    # TAB 2: INTELIGENCIA CRM
    # ==========================
    def setup_tab_crm(self):
        main = ttk.Frame(self.tab_crm, padding=10)
        main.pack(fill="both", expand=True)
        
        # Header Info
        self.crm_header = ttk.Frame(main, style="Card.TFrame", padding=15)
        self.crm_header.pack(fill="x", pady=(0, 15))
        
        self.lbl_crm_name = ttk.Label(self.crm_header, text="Seleccione un cliente...", font=("Segoe UI", 16, "bold"))
        self.lbl_crm_name.pack(side=tk.LEFT)
        
        self.lbl_segmento = ttk.Label(self.crm_header, text="", font=("Segoe UI", 12, "bold"), foreground="white", background="#999")
        self.lbl_segmento.pack(side=tk.RIGHT, padx=10, ipadx=10)
        
        # Stats RFM
        stats = ttk.Frame(main)
        stats.pack(fill="x", pady=10)
        for i in range(3): stats.columnconfigure(i, weight=1)
        
        self.card_r = self.create_crm_card(stats, "Recencia (Última vez)", "-", 0)
        self.card_f = self.create_crm_card(stats, "Frecuencia (Compras)", "-", 1)
        self.card_m = self.create_crm_card(stats, "Monto (Valor de Vida)", "-", 2)
        
        # Historial de Compras
        ttk.Label(main, text="Historial de Ventas", font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(15, 5))
        
        h_cols = ("fecha", "id", "total", "metodo", "items")
        self.hist_tree = ttk.Treeview(main, columns=h_cols, show="headings", height=8)
        self.hist_tree.heading("fecha", text="Fecha")
        self.hist_tree.heading("id", text="# Factura")
        self.hist_tree.heading("total", text="Monto")
        self.hist_tree.heading("metodo", text="Pago")
        self.hist_tree.heading("items", text="Resumen")
        
        self.hist_tree.pack(fill="both", expand=True)

    def create_crm_card(self, parent, title, val, col):
        f = ttk.Frame(parent, style="Card.TFrame", padding=10)
        f.grid(row=0, column=col, sticky="nsew", padx=5)
        ttk.Label(f, text=title, foreground="#555").pack()
        l = ttk.Label(f, text=val, font=("Segoe UI", 14, "bold"), foreground="#1a73e8")
        l.pack()
        return l

    # ==========================
    # LOGICA
    # ==========================
    def conectar(self): return sqlite3.connect("ferreteria.db")
    
    def limpiar(self):
        self.selected_id = None
        for e in self.entries.values(): e.delete(0, tk.END)
        self.lbl_crm_name.config(text="Seleccione un cliente...")
        self.lbl_segmento.config(text="", background="#f0f2f5")
        for i in self.hist_tree.get_children(): self.hist_tree.delete(i)
        
    def cargar_datos(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        conn = self.conectar()
        # Se asume estructura correcta
        c = conn.execute("SELECT id, cedula, nombre, telefono, ciudad, etiquetas FROM clientes")
        for row in c:
            self.tree.insert("", tk.END, values=row)
        conn.close()

    def guardar(self):
        d = {k: v.get() for k, v in self.entries.items()}
        if not d['nombre']: return
        
        conn = self.conectar()
        try:
            if self.selected_id:
                conn.execute("""UPDATE clientes SET nombre=?, cedula=?, telefono=?, direccion=?, 
                                ciudad=?, fecha_nacimiento=?, info_tributaria=?, etiquetas=? WHERE id=?""",
                                (*d.values(), self.selected_id))
            else:
                conn.execute("""INSERT INTO clientes (nombre, cedula, telefono, direccion, ciudad, fecha_nacimiento, info_tributaria, etiquetas) 
                                VALUES (?,?,?,?,?,?,?,?)""", tuple(d.values()))
            conn.commit()
            self.limpiar()
            self.cargar_datos()
            messagebox.showinfo("OK", "Datos guardados", parent=self.root)
        except Exception as e: messagebox.showerror("Error", str(e), parent=self.root)
        finally: conn.close()

    def seleccionar(self, e):
        s = self.tree.selection()
        if not s: return
        
        # Cargar Formulario
        vals = self.tree.item(s[0])['values']
        pid = vals[0]
        self.selected_id = pid
        
        conn = self.conectar()
        r = conn.execute("SELECT * FROM clientes WHERE id=?", (pid,)).fetchone() # Ajustar SELECT * a campos esp. es mejor práctica pero...
        
        # Mapeo manual por seguridad posicional, asumiendo orden de creación tabla
        # id(0), nom(1), ced(2), tel(3), dir(4), email(5), ciudad(6), nac(7), tribut(8), etiq(9)
        # Esto depende de tu schema, hagamos query especifica para evitar errores
        r = conn.execute("""SELECT nombre, cedula, telefono, direccion, ciudad, fecha_nacimiento, info_tributaria, etiquetas 
                            FROM clientes WHERE id=?""", (pid,)).fetchone()
        
        keys = ["nombre", "cedula", "telefono", "direccion", "ciudad", "fecha_nacimiento", "info_tributaria", "etiquetas"]
        for i, k in enumerate(keys):
            self.entries[k].delete(0, tk.END)
            if r[i]: self.entries[k].insert(0, str(r[i]))
            
        # ANALISIS CRM
        self.analizar_rfm(pid, r[0])
        conn.close()

    def analizar_rfm(self, uid, nombre):
        self.lbl_crm_name.config(text=f"{nombre} (ID: {uid})")
        
        conn = self.conectar()
        # Historial
        total_gastado = 0
        freq = 0
        ultima_fecha = None
        
        for item in self.hist_tree.get_children(): self.hist_tree.delete(item)
        
        cursor = conn.execute("SELECT id, fecha, total, metodo_pago FROM ventas WHERE cliente_id=?", (uid,))
        # Si cliente_id es nuevo, puede estar vacio para clientes viejos. Buscar por nombre también?
        # Mejor solo ID para integridad, o nombre legacy
        ventas = cursor.fetchall()
        
        # Fallback nombre si no hay ventas por ID (Migración)
        if not ventas:
             cursor = conn.execute("SELECT id, fecha, total, metodo_pago FROM ventas WHERE cliente=? AND cliente_id IS NULL", (nombre,))
             ventas = cursor.fetchall()

        hoy = datetime.now()
        
        for v in ventas:
            vid, fecha_str, tot, met = v
            freq += 1
            total_gastado += tot
            
            try: f_dt = datetime.strptime(fecha_str, "%Y-%m-%d %H:%M:%S")
            except: f_dt = datetime.min
            
            if ultima_fecha is None or f_dt > ultima_fecha: ultima_fecha = f_dt
            
            self.hist_tree.insert("", tk.END, values=(fecha_str, vid, f"${tot:,.0f}", met or "Efectivo", "Ver Detalle..."))

        # Calculo RFM
        recencia_dias = (hoy - ultima_fecha).days if ultima_fecha else 999
        
        self.card_r.config(text=f"{recencia_dias} días")
        self.card_f.config(text=f"{freq} compras")
        self.card_m.config(text=f"${total_gastado:,.0f}")
        
        # Segmentación
        segmento = "Nuevo / Esporádico"
        color = "#9e9e9e" # Gris
        
        if freq > 10 or total_gastado > 1000000:
            segmento = "💎 CLIENTE VIP"
            color = "#9c27b0" # Purpura
        elif freq > 5:
            segmento = "🌟 Leal / Frecuente"
            color = "#4caf50" # Verde
        elif recencia_dias > 60 and freq > 2:
            segmento = "💤 Dormido (Riesgo)"
            color = "#ff9800" # Naranja
            
        self.lbl_segmento.config(text=segmento, background=color)

def abrir_ventana_clientes():
    t = tk.Toplevel()
    ClientesWindow(t)
