import serial
import time
import csv
import os
import textfsm
from serial.tools import list_ports

# ==========================================================
# 🔹 Función para limpiar pantalla
# ==========================================================
def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

# ==========================================================
# 🔹 Buscar y conectar al puerto serial
# ==========================================================
def conectar_serial():
    puertos = list(list_ports.comports())
    if not puertos:
        print("❌ No se detectó ningún puerto COM.")
        return None

    print("🔌 Puertos detectados:")
    for i, p in enumerate(puertos):
        print(f"{i + 1}. {p.device} - {p.description}")

    opcion = int(input("Selecciona el número del puerto: ")) - 1
    puerto = puertos[opcion].device

    try:
        ser = serial.Serial(puerto, 9600, timeout=1)
        time.sleep(2)
        print(f"\n✅ Conectado correctamente al router en {puerto}\n")
        return ser
    except Exception as e:
        print(f"❌ Error al conectar con el puerto: {e}")
        return None

# ==========================================================
# 🔹 Mandar comando manual
# ==========================================================
def enviar_comandos(ser):
    while True:
        comando = input("📥 Ingresa el comando (o 'exit' para salir): ")
        if comando.lower() == 'exit':
            break

        ser.write((comando + '\n').encode())
        time.sleep(2)
        salida = ser.read_all().decode(errors='ignore')
        print(f"\n📤 Respuesta:\n{salida}\n")

# ==========================================================
# 🔹 Leer interfaces y guardar en CSV con TextFSM
# ==========================================================
def leer_interfaces_y_guardar_csv(ser):
    print("\n🔎 Leyendo interfaces del router...\n")

    ser.write(b"show ip interface brief\n")
    time.sleep(3)
    salida = ser.read_all().decode(errors='ignore')

    print(f"📤 Respuesta del router:\n{salida}\n")

    # --- Limpiar salida ---
    salida = salida.replace("\r", "")

    # --- Cargar plantilla TextFSM ---
    template_path = "cisco_show_ip_int_brief.tpl"

    if not os.path.exists(template_path):
        print(f"❌ No se encontró la plantilla en: {template_path}")
        return

    with open(template_path) as template:
        fsm = textfsm.TextFSM(template)
        resultados = fsm.ParseText(salida)

    if not resultados:
        print("⚠️ No se encontraron interfaces válidas.")
        input("Presiona ENTER para volver al menú...")
        return

    # --- Extraer Hostname ---
    lineas = salida.splitlines()
    hostname = "Router"
    for linea in reversed(lineas):
        if "#" in linea:
            hostname = linea.split("#")[0].strip()
            break

    # --- Crear nombre de archivo CSV ---
    archivo_csv = "routers_interfaces.csv"
    archivo_existe = os.path.exists(archivo_csv)

    # --- Crear encabezados (dinámico según cantidad de interfaces) ---
    encabezados = ["Hostname"]
    for i in range(len(resultados)):
        encabezados.extend([
            f"INTERFACE_{i+1}", f"IP_ADDRESS_{i+1}", f"OK_{i+1}",
            f"METHOD_{i+1}", f"STATUS_{i+1}", f"PROTOCOL_{i+1}"
        ])

    # --- Crear fila con los datos ---
    fila = [hostname]
    for r in resultados:
        fila.extend(r)

    # --- Escribir en el CSV ---
    with open(archivo_csv, "a", newline='') as f:
        writer = csv.writer(f)
        if not archivo_existe:
            writer.writerow(encabezados)
        writer.writerow(fila)

    print(f"✅ Datos guardados correctamente en {archivo_csv}")
    input("Presiona ENTER para volver al menú...")

# ==========================================================
# 🔹 Menú principal
# ==========================================================
def main():
    clear_console()
    print("=== MENÚ PRINCIPAL ===")
    print("1. Mandar comandos manualmente")
    print("2. Leer interfaces con IP y guardar en CSV")
    print("0. Salir")

    opcion = input("Selecciona una opción: ")

    if opcion == "1":
        ser = conectar_serial()
        if ser:
            enviar_comandos(ser)
            ser.close()
    elif opcion == "2":
        ser = conectar_serial()
        if ser:
            leer_interfaces_y_guardar_csv(ser)
            ser.close()
    elif opcion == "0":
        print("👋 Saliendo del programa...")
    else:
        print("❌ Opción no válida.")

if __name__ == "__main__":
    main()

