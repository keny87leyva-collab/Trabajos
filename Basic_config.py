import serial
import time
import pandas as pd

def configure_device(port, baudrate, hostname, username, password, domain):
    try:
        # Abrir conexión serial
        ser = serial.Serial(port, baudrate, timeout=1)
        time.sleep(2)  # Esperar que inicie la conexión

        # Entrar al modo privilegiado y configuración
        ser.write("enable\r\n".encode())
        time.sleep(1)
        ser.write("configure terminal\r\n".encode())
        time.sleep(1)

        # Configuración básica
        ser.write(f"hostname {hostname}\r\n".encode())
        time.sleep(1)
        ser.write(f"username {username} privilege 15 secret {password}\r\n".encode())
        time.sleep(1)
        ser.write(f"ip domain-name {domain}\r\n".encode())
        time.sleep(1)

        # Generación de llaves SSH
        ser.write("crypto key generate rsa modulus 1024\r\n".encode())
        time.sleep(5)  # este proceso tarda más

        # Configuración de acceso remoto
        ser.write("line vty 0 4\r\n".encode())
        time.sleep(1)
        ser.write("login local\r\n".encode())
        ser.write("transport input ssh\r\n".encode())
        ser.write("transport output ssh\r\n".encode())
        ser.write("exit\r\n".encode())

        # Línea de consola
        ser.write("line console 0\r\n".encode())
        time.sleep(1)

        # Cerrar sesión
        ser.write("end\r\n".encode())
        ser.write("write memory\r\n".encode())  # guardar config
        ser.close()

        print(f"[✔] {hostname} configurado correctamente en {port}.")

    except Exception as e:
        print(f"[✘] Error en {hostname} ({port}): {e}")


def cargar_dispositivos_y_configurar(archivo_csv):
    try:
        # Leer archivo CSV
        df = pd.read_csv(archivo_csv)

        for _, fila in df.iterrows():
            nombre = fila["nombre_dispositivo"]
            serie = fila["serie_dispositivo"]   # (opcional, aquí no lo usamos pero está disponible)
            puerto = fila["puerto"]
            baudrate = int(fila["baudrate"])
            usuario = fila["usuario"]
            password = fila["password"]
            domain = fila["domain"]

            print(f"\n>>> Configurando {nombre} en {puerto}...")
            configure_device(puerto, baudrate, nombre, usuario, password, domain)

    except FileNotFoundError:
        print("Error: No se encontró el archivo CSV.")
    except KeyError as e:
        print(f"Error: Falta la columna {e} en el CSV.")


if __name__ == "__main__":
    archivo = "devices.csv"  # 👈 aquí va el nombre real de tu archivo
    cargar_dispositivos_y_configurar(archivo)
