import serial
import time
import pandas as pd

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

    def obtener_serie(self):
        """
        Envía un comando para obtener la serie del dispositivo.
        Este ejemplo asume que el router responde al comando 'show version'.
        """
        if self.conexion is None:
            return None
        salida = self.enviar_comando("show version", espera=2)
        # Aquí habría que extraer la serie de la salida real del router
        # Por ahora simulamos que devuelve "12345ABC" para pruebas
        return "12345ABC"  # <-- cambiar por parsing real si se quiere


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
            serie_real = router.obtener_serie()
            if serie_real == d["serie_esperada"]:
                print(f"[✔] Serie coincide ({serie_real}). Aplicando comandos a {d['nombre']}.")
                # Aquí pondrías los comandos de configuración
                router.enviar_comando(f"hostname {d['nombre']}")
                router.enviar_comando(f"username {d['usuario']} privilege 15 secret {d['password']}")
                router.enviar_comando(f"ip domain-name {d['domain']}")
                # etc...
            else:
                print(f"[✘] Serie NO coincide ({serie_real} != {d['serie_esperada']}). Saltando {d['nombre']}.")
            router.cerrar()
