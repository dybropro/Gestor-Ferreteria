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
    Sin decimales.
    """
    try:
        if valor is None: valor = 0
        valor = float(valor)
        # Usamos formato con comas y luego cambiamos coma por punto para estilo COP
        return f"${valor:,.0f}".replace(",", ".")
    except:
        return "$0"

def limpiar_moneda(texto_moneda):
    """
    Convierte un string formateado ($15.000) de vuelta a float (15000.0).
    Maneja el símbolo $ y los puntos de miles.
    """
    try:
        if not texto_moneda: return 0.0
        # Eliminar el signo $, espacios y los puntos (miles en COP)
        limpio = str(texto_moneda).replace("$", "").replace(" ", "").replace(".", "")
        # Si por alguna razón hay comas (decimales), las pasamos a puntos para float()
        limpio = limpio.replace(",", ".")
        return float(limpio)
    except:
        return 0.0
