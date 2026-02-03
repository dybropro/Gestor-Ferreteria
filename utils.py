import sys
import os

def resource_path(relative_path):
    """ Obtiene la ruta absoluta al recurso, funciona para dev y para PyInstaller """
    try:
        # PyInstaller crea una carpeta temporal y guarda la ruta en _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def formato_moneda(valor):
    """
    Formatea un valor numérico a peso colombiano:
    Ej: 15000 -> $15.000
    Ej: 1000000 -> $1.000.000
    Sin decimales.
    """
    try:
        if valor is None: valor = 0
        valor = float(valor)
        return f"${valor:,.0f}".replace(",", ".")
    except:
        return "$0"
