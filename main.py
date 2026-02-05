import fiados
import proveedores
import compras
import ventas
import clientes
import productos
import inventario
import reportes
import configuracion
import cierre_caja
import tkinter as tk
from tkinter import ttk
import database
import login
import licensing
import licencia_ui
import sys
import os
from PIL import Image, ImageTk
import ctypes
import utils

# --- CONTROL DE VERSIONES ---
VERSION = "2.1.0"

# Función que se ejecuta tras el login exitoso
def iniciar_app(username, rol):
    login_window.root.destroy()  # Cerrar ventana de login
    
    # Crear ventana principal
    global ventana
    # --- CONFIGURACIÓN DE VENTANA ---
    utils.setup_window(ventana, f"Ferretería GILPER - Sistema POS/ERP Profesional - {rol.upper()}")
    ventana.state('zoomed') # Maximizar ventana
    ventana.configure(bg="#f0f2f5") 

    # --- TRUCO PARA ICONO EN BARRA DE TAREAS (WINDOWS) ---
    try:
        myappid = u'dybrocorp.ferreteria.pos.1'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except: pass
    # ---- ESTILOS GLOBALES ----
    style = ttk.Style()
    style.theme_use('clam')
    
    # Colores
    bg_color = "#f0f2f5"
    primary_color = "#1a73e8"
    white_color = "#ffffff"
    text_color = "#333333"
    
    style.configure("TFrame", background=bg_color)
    style.configure("Card.TFrame", background=white_color, relief="flat", borderwidth=0)
    
    style.configure("Header.TLabel", background=bg_color, font=("Segoe UI", 26, "bold"), foreground="#202124")
    style.configure("Section.TLabel", background=bg_color, font=("Segoe UI", 14, "bold"), foreground="#5f6368")
    
    # Estilo botones dashboard
    style.configure("Dash.TButton", font=("Segoe UI", 11, "bold"), background=white_color, foreground=text_color)

    # ---- LAYOUT PRINCIPAL ----
    # Header
    header_frame = ttk.Frame(ventana)
    header_frame.pack(fill="x", padx=40, pady=30)
    
    ttk.Label(header_frame, text="Ferretería GILPER", style="Header.TLabel").pack(anchor="w")
    ttk.Label(header_frame, text=f"Panel de Control Profesional | Usuario: {username} ({rol.capitalize()})", font=("Segoe UI", 12)).pack(anchor="w")

    # Restart function
    def reiniciar_login():
        ventana.destroy()
        # Reiniciar script actual
        os.execl(sys.executable, sys.executable, *sys.argv)

    # Contenedor del Dashboard
    dashboard = ttk.Frame(ventana)
    dashboard.pack(fill="both", expand=True, padx=40)

    # Definir secciones visuales
    def create_section(parent, title, row):
        lbl = ttk.Label(parent, text=title, style="Section.TLabel")
        lbl.grid(row=row, column=0, columnspan=4, sticky="w", pady=(20, 10))
    
    def add_card_btn(parent, text, icon, cmd, r, c, bg="#fff"):
        btn = tk.Button(
            parent,
            text=f"{icon}\n{text}",
            font=("Segoe UI", 11, "bold"),
            bg=bg, fg="#333",
            relief="flat",
            cursor="hand2",
            height=4, width=20, # Tamaño fijo tarjeta
            command=cmd
        )
        btn.grid(row=r, column=c, sticky="nsew", padx=10, pady=10)
        btn.bind("<Enter>", lambda e: btn.config(bg="#e8f0fe", fg="#1a73e8"))
        btn.bind("<Leave>", lambda e: btn.config(bg="white", fg="#333"))

    # Configurar Grid
    for i in range(4): dashboard.columnconfigure(i, weight=1)

    # --- SECCIÓN 1: POS / VENTAS (Operación Diaria) ---
    create_section(dashboard, "POS y Facturación", 0)
    add_card_btn(dashboard, "NUEVA VENTA", "🛒", lambda: ventas.abrir_ventana_ventas(rol), 1, 0, bg="#e3f2fd") # Azulito
    add_card_btn(dashboard, "CLIENTES (CRM)", "👥", clientes.abrir_ventana_clientes, 1, 1)
    add_card_btn(dashboard, "CIERRE DE CAJA", "💰", lambda: cierre_caja.abrir_ventana_cierre(username, reiniciar_login), 1, 2)

    # --- SECCIÓN 2: ADMINISTRACIÓN DE INVENTARIO (ERP) ---
    if rol == "admin":
        create_section(dashboard, "Gestión de Inventarios y Compras", 2)
        
        add_card_btn(dashboard, "CATÁLOGO PRODUCTOS", "📦", productos.abrir_ventana_productos, 3, 0)
        add_card_btn(dashboard, "INVENTARIO VALORIZADO", "📋", inventario.abrir_ventana_inventario, 3, 1)
        add_card_btn(dashboard, "COMPRAS / ENTRADAS", "🚛", compras.abrir_ventana_compras, 3, 2)
        add_card_btn(dashboard, "PROVEEDORES", "🏭", proveedores.abrir_ventana_proveedores, 3, 3)

    # --- SECCIÓN 3: ALTA GERENCIA / REPORTES ---
    if rol == "admin":
        create_section(dashboard, "Administración y Finanzas", 4)
        
        add_card_btn(dashboard, "FIADORES Y CRÉDITOS", "📒", fiados.abrir_ventana_fiados, 5, 0)
        add_card_btn(dashboard, "REPORTE VENTAS", "📥", lambda: reportes.exportar_ventas_dia(ventana), 5, 1)
        add_card_btn(dashboard, "CIERRE DE CAJA", "💰", lambda: cierre_caja.abrir_ventana_cierre(username, reiniciar_login), 5, 2)
        add_card_btn(dashboard, "CONFIGURACIÓN / USER", "⚙️", configuracion.abrir_ventana, 5, 3)

    # Footer
    footer_frame = ttk.Frame(ventana)
    footer_frame.pack(side="bottom", fill="x", pady=10)
    ttk.Label(footer_frame, text=f"© 2026 DybroCorp - Sistema Integral v{VERSION}", font=("Segoe UI", 9), foreground="#aaa", anchor="center").pack()

    ventana.mainloop()

# --- LÓGICA DE INICIO Y LICENCIA ---
def on_login_success(user, rol):
    iniciar_app(user, rol)

def iniciar_login_flow():
    root_login = tk.Tk()
    app_login = login.LoginWindow(root_login, on_login_success)
    globals()['login_window'] = app_login
    root_login.mainloop()

def check_licencia():
    mid = licensing.get_machine_id()
    import database
    conn = database.conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT valor FROM configuracion WHERE clave='licencia_serial'")
        res = cursor.fetchone()
        serial = res[0] if res else ""
    except Exception as e:
        print(f"Error accediendo a configuración: {e}")
        serial = ""
    finally:
        conn.close()
    
    is_valid, _ = licensing.validate_serial(mid, serial)
    if not is_valid:
        licencia_ui.mostrar_ventana_licencia(iniciar_login_flow)
    else:
        iniciar_login_flow()

if __name__ == "__main__":
    database.crear_tablas() # Inicializar DB
    check_licencia() # Verificar licencia antes de nada
