import tkinter as tk
import utils
from tkinter import ttk, messagebox, simpledialog
import sqlite3
from datetime import datetime
import json

class CierreCajaWindow:
    def __init__(self, root, username, on_close_callback):
        self.root = root
        self.username = username
        self.on_close_callback = on_close_callback
        self.root.title("Cierre de Caja (Turno Actual)")
        self.root.geometry("600x700")
        self.root.configure(bg="#f0f2f5")

        self.fecha_cierre_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        main_frame = ttk.Frame(root, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # Obtener ultimo cierre para mostrar "Desde: ..."
        self.last_cierre = self.get_last_cierre()
        msg_inicio = f"Desde: {self.last_cierre}" if self.last_cierre else "Desde: Inicio del Día"

        ttk.Label(main_frame, text="Cierre de Turno / Caja", style="Header.TLabel", font=("Segoe UI", 16, "bold")).pack(pady=(0,5))
        ttk.Label(main_frame, text=msg_inicio, font=("Segoe UI", 10), foreground="#666").pack(pady=(0,20))

        # 1. Calcular Totales del Sistema (Por Turno)
        self.totales_sistema = self.calcular_totales_sistema()
        
        # Frame de Conteo
        count_frame = ttk.Frame(main_frame, style="Card.TFrame", padding=15)
        count_frame.pack(fill="x", pady=10)

        cols = ("medio", "esperado", "real", "diferencia")
        self.tree = ttk.Treeview(count_frame, columns=cols, show="headings", height=5)
        self.tree.heading("medio", text="Medio Pago")
        self.tree.heading("esperado", text="Sistema (Esperado)")
        self.tree.heading("real", text="Real (Contado)")
        self.tree.heading("diferencia", text="Diferencia")
        
        self.tree.pack(fill="x")
        self.tree.bind("<Double-1>", self.ingresar_real)

        # Cargar datos iniciales
        for medio, monto in self.totales_sistema.items():
            self.tree.insert("", tk.END, values=(medio, utils.formato_moneda(monto), "$0", utils.formato_moneda(-monto)))

        self.lbl_info = ttk.Label(main_frame, text="Doble clic en 'Real' para ingresar el dinero contado.", foreground="blue")
        self.lbl_info.pack(pady=5)

        # Resumen Final
        resumen_frame = ttk.Frame(main_frame, padding=15)
        resumen_frame.pack(fill="x", pady=20)
        
        self.lbl_total_esperado = ttk.Label(resumen_frame, text="Total Esperado: $0", font=("Segoe UI", 12))
        self.lbl_total_esperado.pack(anchor="w")
        
        self.lbl_total_real = ttk.Label(resumen_frame, text="Total Real: $0", font=("Segoe UI", 12))
        self.lbl_total_real.pack(anchor="w")
        
        self.lbl_diferencia_total = ttk.Label(resumen_frame, text="Diferencia Total: $0", font=("Segoe UI", 14, "bold"))
        self.lbl_diferencia_total.pack(anchor="w", pady=10)

        # Botón Cierre (Guarda Timestamp completo)
        ttk.Button(main_frame, text="✅  CERRAR CAJA (RESET VALORES)", style="Primary.TButton", command=self.guardar_cierre).pack(fill="x", pady=20)

        self.actualizar_resumen()

    def conectar(self):
        return sqlite3.connect("ferreteria.db")
    
    def get_last_cierre(self):
        conn = self.conectar()
        # Buscar el ultimo cierre
        c = conn.execute("SELECT MAX(fecha_cierre) FROM cierres_caja")
        res = c.fetchone()
        conn.close()
        return res[0] if res and res[0] else None

    def calcular_totales_sistema(self):
        conn = self.conectar()
        cursor = conn.cursor()
        
        resultados = {"Efectivo": 0, "Tarjeta": 0, "Transferencia": 0, "Crédito": 0}
        
        # Filtro de fecha
        if self.last_cierre:
            # Ventas DESPUES del ultimo cierre
            sql_ventas = "SELECT metodo_pago, SUM(total) FROM ventas WHERE fecha > ? GROUP BY metodo_pago"
            params_ventas = (self.last_cierre,)
            
            # Abonos DESPUES del ultimo cierre
            sql_abonos = "SELECT SUM(monto) FROM abonos WHERE fecha > ?"
            params_abonos = (self.last_cierre,)
        else:
            # Si nunca hubo cierre, asumimos DESDE HOY 00:00 (O desde siempre? Mejor hoy para no traer historial viejo si es first run)
            # Pero el usuario pide "volver a cero". Si es first run, traer todo lo de hoy es correcto.
            hoy_inicio = datetime.now().strftime("%Y-%m-%d 00:00:00")
            sql_ventas = "SELECT metodo_pago, SUM(total) FROM ventas WHERE fecha >= ? GROUP BY metodo_pago"
            params_ventas = (hoy_inicio,) # Ah no, si no hay cierres previos, traer TODO del dia
            
            sql_abonos = "SELECT SUM(monto) FROM abonos WHERE fecha >= ?"
            params_abonos = (hoy_inicio,)

        # Ejecutar Ventas
        cursor.execute(sql_ventas, params_ventas)
        for medio, total in cursor.fetchall():
            if medio in resultados:
                resultados[medio] += (total or 0)
            else:
                 # Backup por si hay medios raros
                 resultados[medio] = total or 0
        
        # Ejecutar Abonos (Suman a Efectivo)
        cursor.execute(sql_abonos, params_abonos)
        abonos = cursor.fetchone()[0] or 0
        resultados["Efectivo"] += abonos

        conn.close()
        return resultados

    def ingresar_real(self, event):
        sel = self.tree.selection()
        if not sel: return
        item = sel[0]
        vals = self.tree.item(item, "values")
        medio = vals[0]
        try:
             # COP format: $1.000.000 -> Remove $ and .
             val_clean = vals[1].replace("$", "").replace(".", "").replace(",", "").strip()
             esperado = float(val_clean)
        except: esperado = 0
        
        nuevo_real = simpledialog.askfloat("Conteo", f"Ingrese total contado para {medio}:", minvalue=0)
        if nuevo_real is not None:
            dif = nuevo_real - esperado
            self.tree.item(item, values=(medio, vals[1], utils.formato_moneda(nuevo_real), utils.formato_moneda(dif)))
            self.actualizar_resumen()

    def actualizar_resumen(self):
        t_esp = 0
        t_real = 0
        for child in self.tree.get_children():
            vals = self.tree.item(child)["values"]
            try: 
                val_esp = vals[1].replace("$", "").replace(".", "").replace(",", "").strip()
                t_esp += float(val_esp)
            except: pass
            try: 
                val_real = vals[2].replace("$", "").replace(".", "").replace(",", "").strip()
                t_real += float(val_real)
            except: pass
        
        dif_total = t_real - t_esp
        
        self.lbl_total_esperado.config(text=f"Total Esperado: {utils.formato_moneda(t_esp)}")
        self.lbl_total_real.config(text=f"Total Real: {utils.formato_moneda(t_real)}")
        
        color = "green" if dif_total >= 0 else "red"
        # Tolerancia pequeña para coma flotante
        if abs(dif_total) < 1: color = "green"
            
        self.lbl_diferencia_total.config(text=f"Diferencia Total: {utils.formato_moneda(dif_total)}", foreground=color)
        
        self.total_esperado_final = t_esp
        self.total_real_final = t_real
        self.diferencia_final = dif_total

    def guardar_cierre(self):
        if messagebox.askyesno("Confirmar Cierre", "¿Cerrar turno? Los contadores se reiniciarán a $0."):
            detalle = {}
            for child in self.tree.get_children():
                vals = self.tree.item(child)["values"]
                detalle[vals[0]] = {"esperado": vals[1], "real": vals[2], "diferencia": vals[3]}
            
            conn = self.conectar()
            try:
                # Guardar Fecha Hora Completa
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                conn.execute("""
                    INSERT INTO cierres_caja (fecha_cierre, usuario, total_esperado, total_real, diferencia, detalle_medios)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (timestamp, self.username, self.total_esperado_final, self.total_real_final, self.diferencia_final, json.dumps(detalle)))
                conn.commit()
                messagebox.showinfo("Cierre Exitoso", f"TURNO CERRADO.\nPróximo arqueo contará desde {timestamp}.\n\nCerrando sesión...")
                self.root.destroy()
                if self.on_close_callback:
                    self.on_close_callback()
            except Exception as e:
                messagebox.showerror("Error", str(e))
            finally:
                conn.close()

def abrir_ventana_cierre(username="Admin", on_close_callback=None):
    win = tk.Toplevel()
    app = CierreCajaWindow(win, username, on_close_callback)
