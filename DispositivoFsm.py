import serial
import time
import csv
import os
import textfsm
import pandas as pd

# === Funciones ===

def send_command(ser, command, delay=2):
    """Envía un comando al dispositivo y devuelve la salida"""
    ser.write((command + "\n").encode())
    time.sleep(delay)
    return ser.read_all().decode(errors="ignore")

def parse_output(template_file, raw_output):
    """Aplica un template de TextFSM a una salida"""
    with open(template_file) as template:
        fsm = textfsm.TextFSM(template)
        parsed_data = fsm.ParseText(raw_output)
    return parsed_data, fsm.header

def process_device(row):
    """Procesa un router: obtiene hostname, serie e interfaces"""
    port = row["Port"]
    baudrate = 9600
    ser = None
    data = row.copy()

    try:
        ser = serial.Serial(port, baudrate, timeout=1)
        print(f"🔗 Conectado a {row['Device']} en {port}")

        # --- Hostname y serie ---
        output = send_command(ser, "show version", delay=3)
        version_data, headers = parse_output("templates/cisco_show_version.tpl", output)
        if version_data:
            data["Serie_detectada"] = version_data[0][1]
            data["Device"] = version_data[0][0]

        # --- Interfaces ---
        output = send_command(ser, "show ip int brief", delay=2)
        int_data, int_headers = parse_output("templates/cisco_show_ip_int_brief.tpl", output)

        # Mapear interfaces a columnas dinámicas
        for i, row_int in enumerate(int_data, start=1):
            data[f"int{i}"] = row_int[0]  # Interface
            data[f"status{i}"] = row_int[4]  # Status
            data[f"protocol{i}"] = row_int[5]  # Protocol

        return data

    except Exception as e:
        print(f"❌ Error con {row['Device']} en {port}: {e}")
        return row
    finally:
        if ser and ser.is_open:
            ser.close()

# === MAIN ===
def main():
    input_csv = "dispositivos.csv"

    if not os.path.exists(input_csv):
        print(f"❌ No existe {input_csv}")
        return

    # Leer CSV original
    df = pd.read_csv(input_csv)

    # Procesar cada dispositivo
    new_rows = []
    for _, row in df.iterrows():
        updated = process_device(row.to_dict())
        new_rows.append(updated)

    # Guardar de nuevo en el CSV
    new_df = pd.DataFrame(new_rows)
    new_df.to_csv(input_csv, index=False)
    print(f"\n✅ CSV actualizado: {input_csv}")

if __name__ == "__main__":
    main()
