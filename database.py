import sqlite3
import utils

def conectar():
    return sqlite3.connect(utils.get_db_path())

def crear_tablas():
    conexion = conectar()
    cursor = conexion.cursor()

    # Tabla de productos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS productos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo TEXT UNIQUE,
        nombre TEXT NOT NULL,
        categoria TEXT,
        precio_compra REAL,
        precio_venta REAL,
        stock INTEGER
    )
    """)

    # Tabla de ventas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ventas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TEXT,
        total REAL,
        cliente TEXT
    )
    """)

    # Migración: Verificar si la columna 'cliente' existe, si no, agregarla
    cursor.execute("PRAGMA table_info(ventas)")
    columnas = [col[1] for col in cursor.fetchall()]
    if "cliente" not in columnas:
        cursor.execute("ALTER TABLE ventas ADD COLUMN cliente TEXT DEFAULT 'Público General'")

    # Detalle de cada venta
    # Tabla de detalle de venta
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS detalle_venta (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        venta_id INTEGER,
        producto_id INTEGER,
        cantidad INTEGER,
        precio_unitario REAL,
        FOREIGN KEY (venta_id) REFERENCES ventas(id),
        FOREIGN KEY (producto_id) REFERENCES productos(id)
    )
    """)

    # Tabla de usuarios
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL
    )
    """)

    # Tabla de clientes
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cedula TEXT UNIQUE,
        nombre TEXT NOT NULL,
        telefono TEXT,
        direccion TEXT,
        email TEXT
    )
    """)

    # Tabla de configuración
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS configuracion (
        clave TEXT PRIMARY KEY,
        valor TEXT
    )
    """)

    # Tabla de créditos (Fiados)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS creditos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id INTEGER,
        venta_id INTEGER,
        fecha_inicio TEXT,
        monto_total REAL,
        saldo_pendiente REAL,
        estado TEXT, -- 'PENDIENTE', 'ABONADO', 'PAGADO'
        FOREIGN KEY (cliente_id) REFERENCES clientes(id),
        FOREIGN KEY (venta_id) REFERENCES ventas(id)
    )
    """)

    # Tabla de abonos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS abonos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        credito_id INTEGER,
        fecha TEXT,
        monto REAL,
        FOREIGN KEY (credito_id) REFERENCES creditos(id)
    )
    """)

    # Tabla de proveedores
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS proveedores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nit TEXT UNIQUE,
        razon_social TEXT NOT NULL,
        telefono TEXT,
        direccion TEXT,
        asesor TEXT,
        email TEXT
    )
    """)

    # Tabla de compras (Cabecera)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS compras (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        proveedor_id INTEGER,
        fecha TEXT,
        total REAL,
        factura_referencia TEXT,
        FOREIGN KEY (proveedor_id) REFERENCES proveedores(id)
    )
    """)

    # Tabla detalle compra
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS detalle_compra (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        compra_id INTEGER,
        producto_id INTEGER,
        cantidad INTEGER,
        costo_unitario REAL,
        FOREIGN KEY (compra_id) REFERENCES compras(id),
        FOREIGN KEY (producto_id) REFERENCES productos(id)
    )
    """)

    # Tabla Ciere de Caja
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cierres_caja (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha_cierre TEXT,
        usuario TEXT,
        total_esperado REAL,
        total_real REAL,
        diferencia REAL,
        detalle_medios TEXT -- JSON o Texto plano con desglose
    )
    """)

    # MIGRACIONES (Para actualizar bases de datos existentes)
    try:
        cursor.execute("ALTER TABLE ventas ADD COLUMN metodo_pago TEXT DEFAULT 'Efectivo'")
    except: pass
    
    try:
        cursor.execute("ALTER TABLE ventas ADD COLUMN impuesto REAL DEFAULT 0")
    except: pass

    try:
        cursor.execute("ALTER TABLE productos ADD COLUMN stock_minimo INTEGER DEFAULT 5")
    except: pass

    # CRM Fields
    crm_fields = [
        ("fecha_nacimiento", "TEXT"), ("ciudad", "TEXT"), 
        ("etiquetas", "TEXT"), ("info_tributaria", "TEXT")
    ]
    for field, type_ in crm_fields:
        try: cursor.execute(f"ALTER TABLE clientes ADD COLUMN {field} {type_}")
        except: pass
    
    try: cursor.execute("ALTER TABLE ventas ADD COLUMN cliente_id INTEGER")
    except: pass

    # Valores por defecto configuración
    defaults = {
        "empresa_nombre": "FERRETERÍA DYBRO",
        "empresa_nit": "NIT: 123456789",
        "empresa_direccion": "Dirección de la ferretería",
        "empresa_telefono": "Tel: 555-0000",
        "impuesto_porcentaje": "19", # IVA por defecto
        "licencia_serial": "DEMO-MODE-0000",
        "licencia_vencimiento": "2026-02-03" # Fecha de hoy para forzar activación si es nuevo
    }
    for k, v in defaults.items():
        cursor.execute("INSERT OR IGNORE INTO configuracion (clave, valor) VALUES (?, ?)", (k, v))

    # Crear usuarios por defecto si no existen
    cursor.execute("SELECT count(*) FROM usuarios")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO usuarios (username, password, role) VALUES (?, ?, ?)", 
                       ("admin", "admin123", "admin"))
        cursor.execute("INSERT INTO usuarios (username, password, role) VALUES (?, ?, ?)", 
                       ("vendedor", "vendedor123", "vendedor"))
        print("Usuarios por defecto creados: admin/admin123, vendedor/vendedor123")

    conexion.commit()
    conexion.close()
