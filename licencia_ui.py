import tkinter as tk
from tkinter import ttk, messagebox
import licensing
import database
import sys
import os
import utils

class LicenciaWindow:
    def __init__(self, root, on_success):
        self.root = root
        self.on_success = on_success
        self.on_success = on_success
        utils.setup_window(self.root, "Activación de Sistema - DybroCorp", "500x450")
        self.root.resizable(False, False)
        self.root.configure(bg="#f0f2f5")
        
        self.machine_id = licensing.get_machine_id()
        self.build_ui()
        
    def build_ui(self):
        # Header
        header = tk.Frame(self.root, bg="#1a73e8", height=80)
        header.pack(fill="x")
        tk.Label(header, text="BLOQUEO DE SEGURIDAD", font=("Segoe UI", 16, "bold"), fg="white", bg="#1a73e8").pack(pady=20)
        
        # Content
        content = tk.Frame(self.root, bg="#f0f2f5", padx=30, pady=20)
        content.pack(fill="both", expand=True)
        
        tk.Label(content, text="Su licencia ha expirado o no es válida.", font=("Segoe UI", 11, "bold"), bg="#f0f2f5", fg="#d32f2f").pack()
        tk.Label(content, text="Por favor, contacte a DybroCorp para obtener un código.", font=("Segoe UI", 10), bg="#f0f2f5").pack(pady=(0, 20))
        
        # Machine ID Box
        tk.Label(content, text="Machine ID (Proporcionar al administrador):", font=("Segoe UI", 9, "bold"), bg="#f0f2f5").pack(anchor="w")
        mid_frame = tk.Frame(content, bg="white", highlightbackground="#ddd", highlightthickness=1)
        mid_frame.pack(fill="x", pady=(5, 20))
        
        self.mid_entry = tk.Entry(mid_frame, font=("Consolas", 12), bd=0, justify="center")
        self.mid_entry.insert(0, self.machine_id)
        self.mid_entry.config(state="readonly")
        self.mid_entry.pack(fill="x", padx=10, pady=10)
        
        # Serial Entry
        tk.Label(content, text="Código de Activación:", font=("Segoe UI", 9, "bold"), bg="#f0f2f5").pack(anchor="w")
        self.serial_entry = tk.Entry(content, font=("Consolas", 14), justify="center", bd=1, relief="solid")
        self.serial_entry.pack(fill="x", pady=5)
        self.serial_entry.focus()
        
        # Button
        btn_activar = tk.Button(
            content, text="ACTIVAR AHORA", font=("Segoe UI", 11, "bold"),
            bg="#1a73e8", fg="white", relief="flat", cursor="hand2",
            height=2, # Altura en líneas de texto
            command=self.validar_y_guardar
        )
        btn_activar.pack(fill="x", pady=30)
        
        footer = tk.Label(self.root, text="Soporte: WhatsApp +57 123 456 7890", font=("Segoe UI", 8), bg="#f0f2f5", fg="#777")
        footer.pack(side="bottom", pady=10)

    def validar_y_guardar(self):
        serial = self.serial_entry.get().strip().upper()
        if not serial:
            messagebox.showerror("Error", "Por favor ingrese un código.", parent=self.root)
            return
            
        is_valid, info = licensing.validate_serial(self.machine_id, serial)
        
        if is_valid:
            # Guardar en DB
            try:
                conn = database.conectar()
                cursor = conn.cursor()
                cursor.execute("UPDATE configuracion SET valor = ? WHERE clave = ?", (serial, 'licencia_serial'))
                cursor.execute("UPDATE configuracion SET valor = ? WHERE clave = ?", (info, 'licencia_vencimiento'))
                conn.commit()
                conn.close()
                
                messagebox.showinfo("Éxito", f"Sistema activado correctamente hasta {info}.\nGracias por preferir DybroCorp.", parent=self.root)
                self.root.destroy()
                if self.on_success:
                    self.on_success()
            except Exception as e:
                messagebox.showerror("Error DB", f"No se pudo guardar la activación: {e}", parent=self.root)
        else:
            messagebox.showerror("Código Inválido", info, parent=self.root)

def mostrar_ventana_licencia(on_success_callback):
    root = tk.Tk()
    LicenciaWindow(root, on_success_callback)
    root.mainloop()

if __name__ == "__main__":
    def test_start(): print("Licencia cargada con éxito")
    mostrar_ventana_licencia(test_start)
