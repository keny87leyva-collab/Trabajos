import serial
import time
import pandas as pd
import os
import re

# 🔹 Limpiar pantalla según el SO
def clear_console():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

# 🔹 Enviar comando al router (flujo automático)
def send_command(ser, command, delay=1):
    ser.write((command + "\r\n").encode())
    time.sleep(delay)
    output = ""
    while ser.in_waiting > 0:
        output += ser.read(ser.in_waiting).decode(errors="ignore")
        time.sleep(0.1)
    return output

# 🔹 Enviar comando al router (opción manual)
def send_command_manual(ser, command, delay=1):
    ser.write((command + "\r\n").encode())
    time.sleep(delay)
    output = ""
    while ser.in_waiting > 0:
        output += ser.read(ser.in_waiting).decode(errors="ignore")
        time.sleep(0.1)
    return output

# 🔹 Obtener número de serie desde "show inventory"
def get_serial(ser):
    send_command(ser, "terminal length 0")  # evitar paginación
    output = send_command(ser, "show inventory", delay=2)
    match = re.search(r"SN:\s*([A-Z0-9]+)", output)
    if match:
        return match.group(1)
    return None

# 🔹 Configuración de dispositivo
def configure_device(port, hostname, user, password, domain):
    try:
        ser = serial.Serial(port, baudrate=9600, timeout=2)
        time.sleep(2)

        send_command(ser, "enable")
        send_command(ser, "configure terminal")
        send_command(ser, f"hostname {hostname}")
        send_command(ser, f"username {user} privilege 15 secret {password}")
        send_command(ser, f"ip domain-name {domain}")
        send_command(ser, "crypto key generate rsa modulus 1024", delay=3)
        send_command(ser, "line vty 0 4")
        send_command(ser, "login local")
        send_command(ser, "transport input ssh")
        send_command(ser, "transport output ssh")
        send_command(ser, "exit")
        send_command(ser, "ip ssh version 2")
        send_command(ser, "end")
        send_command(ser, "write memory", delay=2)

        print(f"✅ Configuración aplicada correctamente en {hostname}.")
        ser.close()
        return True

    except Exception as e:
        print(f"❌ Error al configurar el dispositivo {hostname}: {e}")
        return False

# 🔹 Menú principal
def mostrar_menu():
    clear_console()
    print("=== MENÚ PRINCIPAL ===")
    print("1. Mandar comandos manualmente")
    print("2. Hacer configuraciones iniciales desde CSV")
    print("0. Salir")

# 🔹 Menú de comandos manuales
def menu_comandos_manual():
    port = input("🔌 Ingresa el puerto serial (ej. COM3): ")
    try:
        ser = serial.Serial(port, baudrate=9600, timeout=2)
        time.sleep(2)
        print(f"\n✅ Conectado al dispositivo en {port}")

        serial_real = get_serial(ser)
        if serial_real:
            print(f"ℹ Serie detectada en el dispositivo: {serial_real}")
        else:
            print("⚠ No se detectó número de serie en el dispositivo.")

        while True:
            cmd = input("📥 Ingresa el comando (o 'exit' para salir): ")
            if cmd.lower() == "exit":
                break
            output = send_command_manual(ser, cmd, delay=1)
            print(f"\n📤 Respuesta:\n{output}")
        ser.close()
    except Exception as e:
        print(f"❌ Error al conectar: {e}")
    input("Presione ENTER para volver al menú...")

# 🔹 Flujo de configuración inicial desde CSV
def flujo_configuracion_csv():
    clear_console()
    df = pd.read_csv("Data.csv")
    print("\n📂 Dispositivos encontrados en el archivo:")
    print(df)

    Hostnames = [str(d).strip()[0] + str(s).strip() for d, s in zip(df['Device'], df['Serie'])]
    list_device = [(p, h, u, pas, dom) for p, u, pas, dom, h in zip(df['Port'], df['User'], df['Password'], df['Ip-domain'], Hostnames)]

    print("\n📋 Lista de dispositivos y sus configuraciones (hostname + serie esperada):")
    for item in list_device:
        print(item)
    input("Presione ENTER para continuar...")

    configured_devices = []
    skipped_devices = []

    for idx, (p, h, u, pas, dom) in enumerate(list_device, start=1):
        clear_console()
        print(f"\n➡️ Conecte ahora el dispositivo {idx}: {h} en el puerto {p}")
        input("Presione ENTER cuando el dispositivo esté conectado...")

        # ⚠ Pedir al usuario desconectar/reconectar antes de abrir el puerto
        input("🔌 Desconecte y vuelva a conectar el cable serial, luego presione ENTER para continuar...")

        # Intentar configurar el dispositivo
        success = configure_device(p, h, u, pas, dom)
        if success:
            configured_devices.append(h)
        else:
            skipped_devices.append(h)

        print("=================================================")
        input("Presione ENTER para continuar...")

    clear_console()
    print("📊 Resumen de la configuración:")
    print(f"✅ Dispositivos configurados ({len(configured_devices)}): {configured_devices}")
    print(f"⚠ Dispositivos saltados ({len(skipped_devices)}): {skipped_devices}")
    input("Presione ENTER para volver al menú...")

# 🔹 Ejecutar menú
if __name__ == "__main__":
    while True:
        mostrar_menu()
        opcion = input("Selecciona una opción: ")
        if opcion == "1":
            menu_comandos_manual()
        elif opcion == "2":
            flujo_configuracion_csv()
        elif opcion == "0":
            print("👋 Saliendo del programa...")
            break
        else:
            print("❌ Opción inválida.")
            input("Presione ENTER para continuar...")
