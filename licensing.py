import hashlib
import platform
import subprocess
import os
from datetime import datetime, timedelta

# Salt para mayor seguridad (No compartir este valor)
SECRET_SALT = "DybroCorp_2026_Secure_License_System"

def get_machine_id():
    """Genera un ID único para la máquina basado en hardware (CPU, UUID de disco, etc)."""
    try:
        # En Windows, usamos el ID del procesador y el número de serie de la placa base
        cpu_info = platform.processor()
        system_info = platform.node()
        
        # Intentar obtener UUID del sistema via wmic (puede fallar en Win 11)
        uuid_info = ""
        try:
            cmd = "wmic csproduct get uuid"
            output = subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL).decode()
            uuid_info = output.split('\n')[1].strip()
        except:
            # Fallback a UUID de disco o ID de red
            try:
                import uuid
                uuid_info = str(uuid.getnode())
            except:
                uuid_info = "generic-uuid-123"

        raw_id = f"{cpu_info}-{system_info}-{uuid_info}"
        return hashlib.sha256(raw_id.encode()).hexdigest()[:16].upper()
    except Exception as e:
        print(f"Error generando Machine ID: {e}")
        return "HARDWARE-ERROR-ID"

def generate_serial(machine_id, months):
    """Genera un serial basado en el Machine ID y la cantidad de meses (Uso para KeyGen)."""
    # Formato: SERIAL-HASH(ID + MONTHS + SALT)
    expiration_date = (datetime.now() + timedelta(days=30 * months)).strftime("%Y-%m-%d")
    raw_data = f"{machine_id}-{months}-{expiration_date}-{SECRET_SALT}"
    hashed = hashlib.sha256(raw_data.encode()).hexdigest()[:12].upper()
    
    # El serial codifica la fecha de vencimiento y el hash de seguridad
    return f"{months}M-{hashed}-{expiration_date.replace('-', '')}"

def validate_serial(machine_id, serial):
    """Valida si un serial es válido para esta máquina y no ha expirado."""
    try:
        parts = serial.split('-')
        if len(parts) != 3:
            return False, "Formato de serial inválido"
            
        months_part = parts[0].replace('M', '')
        months = int(months_part)
        hash_part = parts[1]
        date_raw = parts[2] # AAAAMMDD
        
        expiration_date_str = f"{date_raw[:4]}-{date_raw[4:6]}-{date_raw[6:8]}"
        expiration_date = datetime.strptime(expiration_date_str, "%Y-%m-%d")
        
        if datetime.now() > expiration_date:
            return False, "El serial ha expirado"
            
        # Re-generar hash para verificar autenticidad
        raw_data = f"{machine_id}-{months}-{expiration_date_str}-{SECRET_SALT}"
        expected_hash = hashlib.sha256(raw_data.encode()).hexdigest()[:12].upper()
        
        if hash_part == expected_hash:
            return True, expiration_date_str
        else:
            return False, "Serial no válido para esta computadora"
            
    except Exception as e:
        return False, f"Error validando serial: {str(e)}"

if __name__ == "__main__":
    # Prueba local
    mid = get_machine_id()
    print(f"Tu Machine ID: {mid}")
    
    # Simulando generación de serial (esto iría en keygen.py)
    test_serial = generate_serial(mid, 3) 
    print(f"Serial generado (3 meses): {test_serial}")
    
    # Validando
    is_valid, info = validate_serial(mid, test_serial)
    print(f"¿Es válido?: {is_valid}, Info: {info}")
