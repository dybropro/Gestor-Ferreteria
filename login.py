import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime, timedelta, time
from PIL import Image, ImageTk
import os
import ctypes
import utils

class LoginWindow:
    def __init__(self, root, on_login_success):
        self.root = root
        self.on_login_success = on_login_success
        utils.setup_window(self.root, "Acceso al Sistema", "400x600")
        self.root.resizable(False, False)
        self.root.configure(bg="#f0f2f5") # Gris muy suave

        # --- TRUCO PARA ICONO EN BARRA DE TAREAS (WINDOWS) ---
        try:
            myappid = u'dybrocorp.ferreteria.pos.1' # ID único
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except: pass

        # Estilos
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        self.style.configure("Card.TFrame", background="white", relief="flat")
        self.style.configure("TLabel", background="white", font=("Segoe UI", 11), foreground="#333")
        self.style.configure("Title.TLabel", background="white", font=("Segoe UI", 18, "bold"), foreground="#1a73e8")
        self.style.configure("TEntry", fieldbackground="#f1f3f4", borderwidth=0, padding=10)
        
        # Botón primario
        self.style.configure("Primary.TButton", 
            font=("Segoe UI", 11, "bold"), 
            background="#1a73e8", 
            foreground="white", 
            borderwidth=0, 
            focuscolor="none", 
            padding=5
        )
        self.style.map("Primary.TButton", 
            background=[('active', '#1557b0'), ('pressed', '#0d47a1')]
        )

        # Centrar ventana
        self.center_window(400, 600)

        # Contenedor principal "Card"
        self.frame = ttk.Frame(root, style="Card.TFrame", padding=30)
        self.frame.place(relx=0.5, rely=0.5, anchor="center", width=360, height=540)

        # -- UI Elements --

        # Logo DybroCorp
        try:
            logo_path = utils.resource_path("logo_dybrocorp.png")
            if os.path.exists(logo_path):
                img = Image.open(logo_path)
                # Redimensionar logo para el header
                img = img.resize((200, 200), Image.Resampling.LANCZOS)
                self.logo_img = ImageTk.PhotoImage(img)
                lbl_logo = tk.Label(self.frame, image=self.logo_img, bg="white")
                lbl_logo.pack(pady=(0, 20))
            else:
                ttk.Label(self.frame, text="DYBROCORP", style="Title.TLabel", justify="center").pack(pady=(0, 30))
        except Exception as e:
            print(f"Error cargando logo: {e}")
            ttk.Label(self.frame, text="DYBROCORP", style="Title.TLabel", justify="center").pack(pady=(0, 30))

        # Usuario
        ttk.Label(self.frame, text="Usuario").pack(anchor="w", pady=(0, 5))
        self.entry_user = ttk.Entry(self.frame, font=("Segoe UI", 11))
        self.entry_user.pack(fill="x", pady=(0, 15), ipady=3)

        # Contraseña
        ttk.Label(self.frame, text="Contraseña").pack(anchor="w", pady=(0, 5))
        self.entry_pass = ttk.Entry(self.frame, show="●", font=("Segoe UI", 11))
        self.entry_pass.pack(fill="x", pady=(0, 25), ipady=3)
        self.entry_pass.bind("<Return>", lambda e: self.login())

        # Botón
        self.btn_login = ttk.Button(
            self.frame, 
            text="INICIAR SESIÓN", 
            style="Primary.TButton", 
            command=self.login,
            cursor="hand2"
        )
        self.btn_login.pack(fill="x")

        # Footer
        ttk.Label(self.frame, text="v1.0", font=("Segoe UI", 8), foreground="#999").pack(side="bottom", pady=(20, 0))

    def center_window(self, width, height):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def login(self):
        username = self.entry_user.get()
        password = self.entry_pass.get()

        if not username or not password:
            messagebox.showwarning("Atención", "Por favor ingrese usuario y contraseña", parent=self.root)
            return

        conn = sqlite3.connect("ferreteria.db")
        cursor = conn.cursor()
        cursor.execute("SELECT role FROM usuarios WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            role = user[0]
            
            # --- VALIDACIÓN DE RESTRICCIÓN HORARIA (Vendedores) ---
            if role == "vendedor":
                 # Verificar ultimo cierre
                 # Usar database.conectar para consistencia
                 import database
                 conn2 = database.conectar()
                 c2 = conn2.cursor()
                 c2.execute("SELECT MAX(fecha_cierre) FROM cierres_caja WHERE usuario=?", (username,))
                 res = c2.fetchone()
                 conn2.close()
                 
                 if res and res[0]:
                     last_close_str = res[0]
                     try:
                         last_close_dt = datetime.strptime(last_close_str, "%Y-%m-%d %H:%M:%S")
                         
                         # Regla: Hasta el "proximo dia" (fecha cierre + 1) a las 08:00 AM
                         next_day = last_close_dt.date() + timedelta(days=1)
                         allowed_access = datetime.combine(next_day, time(8, 0, 0))
                         
                         if datetime.now() < allowed_access:
                             messagebox.showerror("Acceso Restringido", 
                                                  f"Usted cerró caja recientemente.\n\nAcceso permitido a partir de:\n{allowed_access.strftime('%d/%m/%Y %I:%M %p')}", parent=self.root)
                             return
                     except Exception as e:
                         print(f"Error val fecha: {e}")

            self.on_login_success(username, role)
        else:
            messagebox.showerror("Error", "Credenciales incorrectas", parent=self.root)
