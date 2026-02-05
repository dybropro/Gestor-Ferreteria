import sys
import os

def get_db_path():
    """ 
    Determina la ruta de la base de datos. 
    En producción (EXE), se guarda en %APPDATA%/DybroCorp/FerreteriaDybro.
    En desarrollo, se usa la carpeta local.
    """
    db_filename = "ferreteria.db"
    
    # Si estamos en modo EXE (PyInstaller)
    if getattr(sys, 'frozen', False):
        appdata = os.environ.get('APPDATA')
        if appdata:
            base_dir = os.path.join(appdata, "DybroCorp", "FerreteriaDybro")
            if not os.path.exists(base_dir):
                os.makedirs(base_dir)
            return os.path.join(base_dir, db_filename)
            
    # Fallback para desarrollo o si falla APPDATA
    return db_filename

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

def set_window_icon(ventana):
    """
    Establece el icono de DybroCorp en la ventana proporcionada para quitar la 'plumita'.
    """
    try:
        from PIL import Image, ImageTk
        icon_path = resource_path("logo_dybrocorp_dark.ico")
        if os.path.exists(icon_path):
            ventana.iconbitmap(icon_path)
        else:
            icon_png = resource_path("logo_dybrocorp_dark.png")
            if os.path.exists(icon_png):
                img = Image.open(icon_png)
                img_icon = ImageTk.PhotoImage(img)
                ventana.iconphoto(False, img_icon)
                ventana._icon_ref = img_icon # Evitar que sea recolectado por el GC
    except Exception as e:
        print(f"Error estableciendo icono: {e}")

def setup_window(ventana, title, geometry=None):
    """
    Configuración estándar para todas las ventanas: título, icono y persistencia.
    """
    ventana.title(title)
    set_window_icon(ventana)
    if geometry:
        ventana.geometry(geometry)
    
    # Asegurar que los diálogos aparezcan encima si se usa esta ventana como padre
    # ventana.lift() # Opcional: traer al frente al abrir
