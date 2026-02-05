import tkinter as tk
import utils
from tkinter import ttk, messagebox
import sqlite3

class ConfigWindow:
    def __init__(self, root):
        self.root = root
        utils.setup_window(self.root, "Configuración del Sistema", "900x700")
        self.root.configure(bg="#f0f2f5")
        
        main_frame = ttk.Frame(root, padding=20)
        main_frame.pack(fill="both", expand=True)

        nb = ttk.Notebook(main_frame)
        nb.pack(fill="both", expand=True)

        # Pestaña 1: Datos Empresa
        self.frame_empresa = ttk.Frame(nb, padding=20)
        nb.add(self.frame_empresa, text="Datos de Empresa")
        self.setup_empresa()

        # Pestaña 2: Seguridad (Usuarios)
        self.frame_seguridad = ttk.Frame(nb, padding=20)
        nb.add(self.frame_seguridad, text="Seguridad")
        self.setup_seguridad()

    def conectar(self):
        import database
        return database.conectar()

    def setup_empresa(self):
        ttk.Label(self.frame_empresa, text="Información para Facturas", style="Subheader.TLabel").pack(pady=(0,20))
        
        self.entries_empresa = {}
        campos = [
            ("Nombre Empresa", "empresa_nombre"),
            ("NIT / RUC", "empresa_nit"),
            ("Dirección", "empresa_direccion"),
            ("Teléfono", "empresa_telefono"),
            ("Impuesto % (Ej: 19)", "impuesto_porcentaje")
        ]

        # Cargar valores actuales
        conn = self.conectar()
        cursor = conn.cursor()
        
        for label, key in campos:
            ttk.Label(self.frame_empresa, text=label).pack(anchor="w", pady=(5,0))
            entry = ttk.Entry(self.frame_empresa, font=("Segoe UI", 10))
            entry.pack(fill="x", pady=(0, 10))
            
            cursor.execute("SELECT valor FROM configuracion WHERE clave=?", (key,))
            res = cursor.fetchone()
            if res:
                entry.insert(0, res[0])
            
            self.entries_empresa[key] = entry
            
        conn.close()
        
        ttk.Button(self.frame_empresa, text="Guardar Cambios", style="Primary.TButton", command=self.guardar_empresa).pack(pady=20, fill="x")

    def guardar_empresa(self):
        conn = self.conectar()
        cursor = conn.cursor()
        try:
            for key, entry in self.entries_empresa.items():
                val = entry.get()
                cursor.execute("INSERT OR REPLACE INTO configuracion (clave, valor) VALUES (?, ?)", (key, val))
            conn.commit()
            messagebox.showinfo("Éxito", "Datos de empresa actualizados.", parent=self.root)
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=self.root)
        finally:
            conn.close()

    def setup_seguridad(self):
        # Frame izquierda: Cambiar Contraseña
        f_pass = ttk.Labelframe(self.frame_seguridad, text="Cambiar Contraseña", padding=15)
        f_pass.pack(fill="x", pady=10)

        ttk.Label(f_pass, text="Usuario").pack(anchor="w")
        
        # Cargar usuarios reales
        users = self.get_users()
        self.combo_user = ttk.Combobox(f_pass, values=users, state="readonly")
        self.combo_user.pack(fill="x", pady=(0, 10))
        if users: self.combo_user.current(0)

        ttk.Label(f_pass, text="Nueva Contraseña").pack(anchor="w")
        self.entry_new_pass = ttk.Entry(f_pass, show="●", font=("Segoe UI", 11))
        self.entry_new_pass.pack(fill="x", pady=(0, 20))

        ttk.Button(f_pass, text="Actualizar Contraseña", command=self.guardar_pass).pack(fill="x")

        # Frame derecha/abajo: Crear Usuario
        f_new = ttk.Labelframe(self.frame_seguridad, text="Crear Nuevo Usuario (Vendedor)", padding=15)
        f_new.pack(fill="x", pady=20)

        ttk.Label(f_new, text="Nombre de Usuario").pack(anchor="w")
        self.entry_create_user = ttk.Entry(f_new, font=("Segoe UI", 11))
        self.entry_create_user.pack(fill="x", pady=(0, 10))

        ttk.Label(f_new, text="Contraseña Inicial").pack(anchor="w")
        self.entry_create_pass = ttk.Entry(f_new, show="●", width=40, font=("Segoe UI", 11))
        self.entry_create_pass.pack(fill="x", pady=(0, 10), ipady=3)
        
        ttk.Label(f_new, text="Rol").pack(anchor="w")
        self.combo_role = ttk.Combobox(f_new, values=["vendedor", "admin"], state="readonly")
        self.combo_role.current(0)
        self.combo_role.pack(fill="x", pady=(0, 15))

        ttk.Button(f_new, text="Crear Usuario", command=self.crear_usuario).pack(fill="x")

    def get_users(self):
        conn = self.conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM usuarios")
        users = [r[0] for r in cursor.fetchall()]
        conn.close()
        return users

    def crear_usuario(self):
        new_user = self.entry_create_user.get()
        new_pass = self.entry_create_pass.get()
        role = self.combo_role.get()

        if not new_user or not new_pass:
            messagebox.showwarning("Error", "Complete todos los campos", parent=self.root)
            return

        conn = self.conectar()
        try:
            conn.execute("INSERT INTO usuarios (username, password, role) VALUES (?, ?, ?)", (new_user, new_pass, role))
            conn.commit()
            messagebox.showinfo("Éxito", f"Usuario '{new_user}' creado correctamente.", parent=self.root)
            self.entry_create_user.delete(0, tk.END)
            self.entry_create_pass.delete(0, tk.END)
            # Actualizar lista de usuarios para cambiar pass
            self.combo_user['values'] = self.get_users()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "El nombre de usuario ya existe.", parent=self.root)
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=self.root)
        finally:
            conn.close()

    def guardar_pass(self):
        user = self.combo_user.get()
        new_pass = self.entry_new_pass.get()
        
        if not new_pass:
            messagebox.showwarning("Atención", "La contraseña no puede estar vacía", parent=self.root)
            return

        conn = self.conectar()
        try:
            conn.execute("UPDATE usuarios SET password=? WHERE username=?", (new_pass, user))
            conn.commit()
            messagebox.showinfo("Éxito", f"Contraseña de '{user}' actualizada.", parent=self.root)
            self.entry_new_pass.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=self.root)
        finally:
            conn.close()

def abrir_ventana(parent=None):
    win = tk.Toplevel(parent)
    app = ConfigWindow(win)
