import os
import re
from netmiko import ConnectHandler

# Credenciales de acceso
usuario_sw = "cisco"
clave_sw = "cisco99"

# ===================================================
# FUNCIONES AUXILIARES
# ===================================================

def obtener_ips_arp():
    """Obtiene las IPs detectadas en la tabla ARP local."""
    salida_comando = os.popen("arp -a").read()
    return sorted(set(re.findall(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b", salida_comando)))

def identificar_switches(ips_encontradas):
    """Identifica los switches Cisco en las IPs detectadas."""
    lista_switches = []
    for direccion in ips_encontradas:
        try:
            conexion = ConnectHandler(
                device_type="cisco_ios",
                host=direccion,
                username=usuario_sw,
                password=clave_sw,
                timeout=3
            )
            respuesta = conexion.send_command("show version", read_timeout=3)
            if "Cisco IOS" in respuesta:
                nombre_disp = re.search(r"hostname (\S+)", conexion.send_command("show run | i hostname"))
                nombre_disp = nombre_disp.group(1) if nombre_disp else direccion
                lista_switches.append({
                    "device_type": "cisco_ios",
                    "host": direccion,
                    "username": usuario_sw,
                    "password": clave_sw,
                    "hostname": nombre_disp
                })
            conexion.disconnect()
        except:
            continue
    return lista_switches

def buscar_mac_por_ip(conexion, ip_busqueda):
    """Busca la dirección MAC asociada a una IP."""
    salida = conexion.send_command(f"show ip arp {ip_busqueda}")
    mac_encontrada = re.search(r"([0-9a-f]{4}\.[0-9a-f]{4}\.[0-9a-f]{4})", salida, re.I)
    return mac_encontrada.group(1) if mac_encontrada else None

def buscar_puerto_por_mac(conexion, mac_objetivo):
    """Busca el puerto y VLAN donde está la MAC encontrada."""
    salida = conexion.send_command(f"show mac address-table address {mac_objetivo}")
    coincidencia = re.search(r"(\d+)\s+([0-9a-f\.]+)\s+\S+\s+(\S+)", salida, re.I)
    if coincidencia:
        return coincidencia.group(1), coincidencia.group(3)
    return None, None

def obtener_vecinos(conexion):
    """Obtiene los vecinos CDP de un switch."""
    salida = conexion.send_command("show cdp neighbors detail", read_timeout=10)
    lista_vecinos = []
    patron = re.compile(
        r"Device ID: (\S+).*?"
        r"IP address: (\d+\.\d+\.\d+\.\d+).*?"
        r"Interface: ([A-Za-z0-9\/]+),\s+Port ID \(outgoing port\): ([A-Za-z0-9\/]+)",
        re.S | re.I
    )
    for coincidencia in patron.finditer(salida):
        lista_vecinos.append({
            "nombre": coincidencia.group(1),
            "ip": coincidencia.group(2),
            "interfaz": coincidencia.group(3).lower().replace("fastethernet", "fa")
        })
    return lista_vecinos

def rastrear_dispositivo(ip_busqueda, switch, ya_visitados=None):
    """Rastrea el host a través de los switches hasta encontrar su puerto final."""
    if ya_visitados is None:
        ya_visitados = set()
    if switch['host'] in ya_visitados:
        return None
    ya_visitados.add(switch['host'])

    try:
        conexion = ConnectHandler(
            device_type="cisco_ios",
            host=switch['host'],
            username=switch['username'],
            password=switch['password']
        )
        conexion.enable()

        mac = buscar_mac_por_ip(conexion, ip_busqueda)
        if mac:
            vlan, puerto = buscar_puerto_por_mac(conexion, mac)
            if puerto:
                vecinos = obtener_vecinos(conexion)
                for v in vecinos:
                    if puerto.lower() in v["interfaz"].lower() and v["ip"] not in ya_visitados:
                        conexion.disconnect()
                        nuevo_switch = {
                            "device_type": "cisco_ios",
                            "host": v["ip"],
                            "username": usuario_sw,
                            "password": clave_sw,
                            "hostname": v["nombre"].split('.')[0]
                        }
                        return rastrear_dispositivo(ip_busqueda, nuevo_switch, ya_visitados)
                conexion.disconnect()
                return {
                    "puerto": puerto,
                    "vlan": vlan,
                    "mac": mac,
                    "ip": ip_busqueda
                }
        else:
            vecinos = obtener_vecinos(conexion)
            for v in vecinos:
                if v["ip"] not in ya_visitados:
                    conexion.disconnect()
                    nuevo_switch = {
                        "device_type": "cisco_ios",
                        "host": v["ip"],
                        "username": usuario_sw,
                        "password": clave_sw,
                        "hostname": v["nombre"].split('.')[0]
                    }
                    resultado = rastrear_dispositivo(ip_busqueda, nuevo_switch, ya_visitados)
                    if resultado:
                        return resultado

        conexion.disconnect()
        return None

    except:
        return None

# ===================================================
# PROGRAMA PRINCIPAL
# ===================================================
if __name__ == "__main__":
    while True:
        ip_objetivo = input("Ingresa la IP que deseas localizar (o escribe 'salir' para terminar): ").strip()
        if ip_objetivo.lower() == "salir":
            break

        ips_disponibles = obtener_ips_arp()
        lista_switches = identificar_switches(ips_disponibles)

        resultado = None
        for sw in lista_switches:
            resultado = rastrear_dispositivo(ip_objetivo, sw)
            if resultado:
                break

        if resultado:
            print("\nHOST DETECTADO:")
            print(f"   Puerto: {resultado['puerto']}")
            print(f"   VLAN: {resultado['vlan']}")
            print(f"   MAC: {resultado['mac']}")
            print(f"   IP: {resultado['ip']}\n")
        else:
            print("No se encontró la IP en ningún switch.\n")
