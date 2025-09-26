import serial
import time
import pandas as pd
import re

class RouterCisco:
    def __init__(self, puerto, baudios=9600, timeout=1):
        self.puerto = puerto
        self.baudios = baudios
        self.timeout = timeout
        self.conexion = None

    def conectar(self):
        try:
            self.conexion = serial.Serial(port=self.puerto, baudrate=self.baudios, timeout=self.timeout)
            time.sleep(2)
            print(f"[+] Conectado a {self.puerto} a {self.baudios} bps.")
        except Exception as e:
            print(f"[!] Error al conectar: {e}")
            self.conexion = None

    def enviar_comando(self, comando, espera=1):
        if self.conexion is None:
            print("[!] No hay conexión activa.")
            return None
        self.conexion.write((comando + '\n').encode())
        time.sleep(espera)
        salida = self.conexion.read_all().decode(errors='ignore')
        return salida

    def cerrar(self):
        if self.conexion:
            self.conexion.close()
            print("[+] Conexión cerrada.")

    def obtener_serie_y_modelo(self):
        """
        Usa 'show inventory' para obtener el modelo (PID) y número de serie (SN).
        """
        if self.conexion is None:
            return None, None

        salida = self.enviar_comando("show inventory", espera=3)

        modelo_match = re.search(r"PID:\s+(\S+)", salida)
        modelo = modelo_match.group(1) if modelo_match else "Desconocido"

        serie_match = re.search(r"SN:\s+(\S+)", salida)
        serie = serie_match.group(1) if serie_match else "Desconocido"

        return serie, modelo


def cargar_dispositivos(archivo_csv):
    try:
        df = pd.read_csv(archivo_csv)
        routers = []
        for _, fila in df.iterrows():
            puerto = fila["puerto"]
            baudrate = int(fila["baudrate"])
            routers.append({
                "router": RouterCisco(puerto, baudrate),
                "serie_esperada": fila["serie_dispositivo"],
                "modelo_esperado": fila["modelo_dispositivo"],
                "nombre": fila["nombre_dispositivo"],
                "usuario": fila["usuario"],
                "password": fila["password"],
                "domain": fila["domain"]
            })
        return routers
    except Exception as e:
        print(f"[!] Error al cargar CSV: {e}")
        return []


if __name__ == "__main__":
    archivo = "devices.csv"
    dispositivos = cargar_dispositivos(archivo)

    for d in dispositivos:
        router = d["router"]
        router.conectar()
        if router.conexion:
            serie_real, modelo_real = router.obtener_serie_y_modelo()
            print(f"[i] Detectado en {d['nombre']}: Modelo={modelo_real}, Serie={serie_real}")

            if serie_real == d["serie_esperada"] and modelo_real == d["modelo_esperado"]:
                print(f"[✔] Coinciden modelo y serie. Aplicando comandos a {d['nombre']}.")
                router.enviar_comando(f"hostname {d['nombre']}")
                router.enviar_comando(f"username {d['usuario']} privilege 15 secret {d['password']}")
                router.enviar_comando(f"ip domain-name {d['domain']}")
            else:
                print(f"[✘] No coinciden -> Esperado: Modelo={d['modelo_esperado']}, Serie={d['serie_esperada']} | Detectado: Modelo={modelo_real}, Serie={serie_real}.")
            router.cerrar()
