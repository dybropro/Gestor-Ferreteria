import tkinter as tk
import utils
from tkinter import ttk, messagebox, simpledialog
import sqlite3
from datetime import datetime
import csv
import os

class FiadosWindow:
    def __init__(self, root):
        self.root = root
        utils.setup_window(self.root, "Gestión de Créditos y Fiadores", "1100x700")
        self.root.configure(bg="#f0f2f5") # Gris claro

        # Estilos visuales para estados
        style = ttk.Style()
        style.configure("Treeview", rowheight=30)
        self.root.tag_red = "rojo"
        self.root.tag_yellow = "amarillo"
        self.root.tag_green = "verde"

        # Layout
        main_frame = ttk.Frame(root, padding=20)
        main_frame.pack(fill="both", expand=True)

        # Header
        header = ttk.Frame(main_frame)
        header.pack(fill="x", pady=(0, 20))
        ttk.Label(header, text="Cartera de Clientes (Fiados)", font=("Segoe UI", 18, "bold")).pack(side=tk.LEFT)
        
        ttk.Button(header, text="📥 Exportar Excel", command=self.exportar_excel).pack(side=tk.RIGHT)
        ttk.Button(header, text="💰 Registrar Abono", command=self.registrar_abono).pack(side=tk.RIGHT, padx=10)

        # Tabla
        cols = ("id", "cliente", "fecha", "total", "saldo", "estado")
        self.tree = ttk.Treeview(main_frame, columns=cols, show="headings", selectmode="browse")

        self.tree.heading("id", text="ID Crédito")
        self.tree.heading("cliente", text="Cliente")
        self.tree.heading("fecha", text="Fecha Venta")
        self.tree.heading("total", text="Total Deuda")
        self.tree.heading("saldo", text="Saldo Pendiente")
        self.tree.heading("estado", text="Estado")

        self.tree.column("id", width=50, anchor="center")
        self.tree.column("cliente", width=250)
        self.tree.column("fecha", width=120, anchor="center")
        self.tree.column("total", width=120, anchor="e")
        self.tree.column("saldo", width=120, anchor="e")
        self.tree.column("estado", width=100, anchor="center")

        # Configurar colores de filas
        self.tree.tag_configure("rojo", background="#ffcccc")      # No ha pagado nada (o poco)
        self.tree.tag_configure("amarillo", background="#fff4cc")  # Ha abonado (saldo < total)
        self.tree.tag_configure("verde", background="#ccffcc")     # Pagado (saldo 0)

        self.tree.pack(fill="both", expand=True)
        
        self.cargar_datos()

    def conectar(self):
        import database
        return database.conectar()

    def cargar_datos(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        conn = self.conectar()
        cursor = conn.cursor()
        
        query = """
            SELECT cr.id, cl.nombre, cr.fecha_inicio, cr.monto_total, cr.saldo_pendiente, cr.estado
            FROM creditos cr
            JOIN clientes cl ON cr.cliente_id = cl.id
            ORDER BY cr.saldo_pendiente DESC
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        
        for row in rows:
            credito_id, cliente, fecha, total, saldo, estado = row
            
            # Determinar color
            tag = "verde"
            if saldo > 0:
                if saldo == total:
                    tag = "rojo" # Debe todo
                else:
                    tag = "amarillo" # Ha abonado algo
            
            self.tree.insert("", tk.END, values=(
                credito_id, cliente, fecha, 
                utils.formato_moneda(total), utils.formato_moneda(saldo), estado
            ), tags=(tag,))

        conn.close()

    def registrar_abono(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione un crédito para abonar.", parent=self.root)
            return
            
        item = self.tree.item(sel[0])
        vals = item['values']
        credito_id = vals[0]
        cliente = vals[1]
        # Usar el nuevo helper para parsear el saldo de forma segura
        saldo_actual = utils.limpiar_moneda(vals[4])

        if saldo_actual <= 0:
            messagebox.showinfo("Info", "Este crédito ya está pagado.", parent=self.root)
            return

        abono = simpledialog.askfloat("Abonar", f"Cliente: {cliente}\nSaldo: {utils.formato_moneda(saldo_actual)}\n\nIngrese monto a abonar:")
        
        if abono is None: return
        if abono <= 0: return
        
        if abono > saldo_actual:
            messagebox.showerror("Error", "El abono no puede superar el saldo pendiente.", parent=self.root)
            return

        new_saldo = saldo_actual - abono
        new_estado = "PAGADO" if new_saldo == 0 else "ABONADO"

        conn = self.conectar()
        try:
            # Registrar abono
            conn.execute("INSERT INTO abonos (credito_id, fecha, monto) VALUES (?, ?, ?)", 
                         (credito_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), abono))
            
            # Actualizar crédito
            conn.execute("UPDATE creditos SET saldo_pendiente=?, estado=? WHERE id=?", 
                         (new_saldo, new_estado, credito_id))
            
            conn.commit()
            messagebox.showinfo("Éxito", "Abono registrado correctamente.", parent=self.root)
            self.cargar_datos()
            
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=self.root)
        finally:
            conn.close()

    def exportar_excel(self):
        filename = f"Reporte_Fiadores_{datetime.now().strftime('%Y%m%d')}.csv"
        try:
            with open(filename, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file, delimiter=';')
                writer.writerow(["ID", "CLIENTE", "FECHA", "TOTAL DEUDA", "SALDO PENDIENTE", "ESTADO"])
                
                for child in self.tree.get_children():
                    vals = self.tree.item(child)['values']
                    writer.writerow(vals)
                    
            messagebox.showinfo("Exportado", f"Archivo guardado: {filename}", parent=self.root)
            os.startfile(filename)
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=self.root)

def abrir_ventana_fiados():
    win = tk.Toplevel()
    app = FiadosWindow(win)
