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
