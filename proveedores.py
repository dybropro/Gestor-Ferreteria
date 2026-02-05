import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

class ProveedoresWindow:
    def __init__(self, root):
        self.root = root
        utils.setup_window(self.root, "Gestión de Proveedores", "900x600")
        self.root.configure(bg="#f0f2f5")

        self.selected_id = None
        
        main_container = ttk.Frame(root, padding=10)
        main_container.pack(fill="both", expand=True)
        
        # Formulario
        left_frame = ttk.Frame(main_container, style="Card.TFrame", padding=20)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        ttk.Label(left_frame, text="Datos del Proveedor", style="Subheader.TLabel").pack(pady=(0, 20))
        
        self.entries = {}
        campos = [("NIT / RUT", "nit"), ("Razón Social", "razon_social"), 
                  ("Teléfono", "telefono"), ("Dirección", "direccion"), 
                  ("Nombre Asesor", "asesor"), ("Email", "email")]
        
        for label, key in campos:
            ttk.Label(left_frame, text=label).pack(anchor="w", pady=(5,0))
            entry = ttk.Entry(left_frame, font=("Segoe UI", 10))
            entry.pack(fill="x", pady=(0, 10))
            self.entries[key] = entry

        ttk.Button(left_frame, text="Guardar Proveedor", style="Primary.TButton", command=self.guardar).pack(fill="x", pady=(20, 5))
        ttk.Button(left_frame, text="Limpiar", command=self.limpiar).pack(fill="x", pady=5)
        ttk.Button(left_frame, text="Eliminar", command=self.eliminar).pack(fill="x", pady=5)

        # Lista
        right_frame = ttk.Frame(main_container)
        right_frame.pack(side=tk.RIGHT, fill="both", expand=True)
        
        cols = ("id", "nit", "nombre", "tel", "asesor")
        self.tree = ttk.Treeview(right_frame, columns=cols, show="headings", selectmode="browse")
        
        self.tree.heading("id", text="ID")
        self.tree.heading("nit", text="NIT")
        self.tree.heading("nombre", text="Razón Social")
        self.tree.heading("tel", text="Teléfono")
        self.tree.heading("asesor", text="Asesor")
        
        self.tree.column("id", width=30)
        self.tree.column("nit", width=100)
        self.tree.column("nombre", width=200)
        self.tree.column("tel", width=100)
        self.tree.column("asesor", width=150)
        
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.seleccionar)
        
        self.cargar_datos()

    def conectar(self):
        return sqlite3.connect("ferreteria.db")

    def limpiar(self):
        self.selected_id = None
        for entry in self.entries.values():
            entry.delete(0, tk.END)

    def cargar_datos(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        conn = self.conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nit, razon_social, telefono, asesor FROM proveedores")
        for row in cursor.fetchall():
            self.tree.insert("", tk.END, values=row)
        conn.close()

    def guardar(self):
        data = {k: v.get() for k, v in self.entries.items()}
        
        if not data['razon_social']:
            messagebox.showwarning("Error", "La Razón Social es obligatoria", parent=self.root)
            return

        conn = self.conectar()
        try:
            if self.selected_id:
                conn.execute("""
                    UPDATE proveedores SET nit=?, razon_social=?, telefono=?, direccion=?, asesor=?, email=?
                    WHERE id=?
                """, (*data.values(), self.selected_id))
                messagebox.showinfo("Éxito", "Proveedor actualizado", parent=self.root)
            else:
                conn.execute("""
                    INSERT INTO proveedores (nit, razon_social, telefono, direccion, asesor, email)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, tuple(data.values()))
                messagebox.showinfo("Éxito", "Proveedor registrado", parent=self.root)
                
            conn.commit()
            self.limpiar()
            self.cargar_datos()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "El NIT ya está registrado", parent=self.root)
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=self.root)
        finally:
            conn.close()

    def seleccionar(self, event):
        sel = self.tree.selection()
        if not sel: return
        
        vals = self.tree.item(sel[0])['values']
        self.selected_id = vals[0]
        
        conn = self.conectar()
        row = conn.execute("SELECT nit, razon_social, telefono, direccion, asesor, email FROM proveedores WHERE id=?", (self.selected_id,)).fetchone()
        conn.close()
        
        keys = ["nit", "razon_social", "telefono", "direccion", "asesor", "email"]
        for i, k in enumerate(keys):
            self.entries[k].delete(0, tk.END)
            if row[i]: self.entries[k].insert(0, row[i])

    def eliminar(self):
        if not self.selected_id: return
        if messagebox.askyesno("Confirmar", "¿Eliminar proveedor?", parent=self.root):
            conn = self.conectar()
            conn.execute("DELETE FROM proveedores WHERE id=?", (self.selected_id,))
            conn.commit()
            conn.close()
            self.limpiar()
            self.cargar_datos()

def abrir_ventana_proveedores():
    win = tk.Toplevel()
    app = ProveedoresWindow(win)
