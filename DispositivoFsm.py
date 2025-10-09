import serial
import time
import csv
import os
from textfsm import TextFSM

# ==============================
# 🔹 FUNCIONES AUXILIARES
# ==============================

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def conectar_router(puerto, baudrate=9600, timeout=1):
    try:
        ser = serial.Serial(port=puerto, baudrate=baudrate, timeout=timeout)
        time.sleep(2)
        print(f"\n🔗 Conectado a Router en {puerto}")
        return ser
    except Exception as e:
        print(f"❌ Error al conectar al router: {e}")
        return None

def enviar_comando(ser, comando, delay=1):
    ser.write((comando + '\n').encode())
    time.sleep(delay)
    salida = ser.read_all().decode(errors='ignore')
    return salida

# ==============================
# 🔹 LEER INTERFACES Y GUARDAR CSV
# ==============================

def leer_interfaces_y_guardar_csv():
    puerto = "COM9"  # 🔧 ajusta tu puerto si cambia
    archivo_tpl = "cisco_show_ip_int_brief.tpl"
    archivo_csv = "Dispositivosfsm.csv"

    # 🔹 Verifica que el archivo CSV exista o lo crea vacío con encabezados
    if not os.path.exists(archivo_csv):
        print("📄 No existe el archivo CSV. Creando uno nuevo...")
        campos = [
            "Serie","Port","Device","User","Password","Ip-domain","Serie_detectada"
        ]
        for i in range(1, 11):
            campos += [f"int{i}", f"ip{i}", f"status{i}", f"protocol{i}"]

        with open(archivo_csv, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=campos)
            writer.writeheader()
        print(f"✅ CSV creado: {archivo_csv}\n")

    ser = conectar_router(puerto)
    if not ser:
        return

    try:
        # Enviar comando y obtener salida
        enviar_comando(ser, "end", delay=2)  # Asegura que estamos en el prompt
        salida = enviar_comando(ser, "show ip interface brief", delay=2)
        print("\n📤 Respuesta del router:\n")
        print(salida)

        # Cargar y aplicar el template FSM
        with open(archivo_tpl) as template:
            fsm = TextFSM(template)
            result = fsm.ParseText(salida)

        if not result:
            print("⚠️ No se encontraron interfaces con IP asignada.")
        else:
            print("✅ Interfaces detectadas correctamente.\n")

        # Crear diccionario con los datos base
        data = {
            "Serie": "FTX1537827U",
            "Port": puerto,
            "Device": "RFTX1050W1PR",
            "User": "Cisco",
            "Password": "Cisco",
            "Ip-domain": "cisco.local",
            "Serie_detectada": "",
        }

        # Agregar interfaces dinámicamente (máximo 10)
        for i, iface in enumerate(result[:10], start=1):
            data[f'int{i}'] = iface[0]           # INTERFACE
            data[f'ip{i}'] = iface[1]            # IP_ADDRESS
            data[f'status{i}'] = iface[4]        # STATUS
            data[f'protocol{i}'] = iface[5]      # PROTOCOL

        # Guardar datos al CSV
        with open(archivo_csv, "a", newline="", encoding="utf-8") as csvfile:
            campos = [
                "Serie","Port","Device","User","Password","Ip-domain","Serie_detectada"
            ]
            for i in range(1, 11):
                campos += [f"int{i}", f"ip{i}", f"status{i}", f"protocol{i}"]

            writer = csv.DictWriter(csvfile, fieldnames=campos)
            writer.writerow(data)

        print(f"✅ CSV actualizado: {archivo_csv}")

    except Exception as e:
        print(f"❌ Error procesando interfaces: {e}")
    finally:
        ser.close()
        input("Presiona ENTER para volver al menú...")

# ==============================
# 🔹 MENÚ PRINCIPAL
# ==============================

def menu_principal():
    while True:
        clear_console()
        print("=== MENÚ PRINCIPAL ===")
        print("1. Mandar comandos manualmente")
        print("2. Leer interfaces con IP y guardar en CSV")
        print("0. Salir")
        opcion = input("Selecciona una opción: ")

        if opcion == "1":
            comando_manual()
        elif opcion == "2":
            leer_interfaces_y_guardar_csv()
        elif opcion == "0":
            print("👋 Saliendo del programa...")
            break
        else:
            print("⚠️ Opción no válida.")
            time.sleep(1)

# ==============================
# 🔹 MODO MANUAL
# ==============================

def comando_manual():
    puerto = "COM9"
    ser = conectar_router(puerto)
    if not ser:
        return

    try:
        while True:
            comando = input("\n📥 Ingresa el comando (o 'exit' para salir): ")
            if comando.lower() == "exit":
                break
            respuesta = enviar_comando(ser, comando)
            print("\n📤 Respuesta:")
            print(respuesta)
    finally:
        ser.close()

# ==============================
# 🔹 EJECUCIÓN
# ==============================

if __name__ == "__main__":
    menu_principal()
