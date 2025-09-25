import serial
import time
import pandas as pd

class RouterCisco:
    def __init__(self, puerto, baudios=9600, timeout=1):
        """
        Inicializa la conexión serial con el router Cisco.
        """
        self.puerto = puerto
        self.baudios = baudios
        self.timeout = timeout
        self.conexion = None

    def conectar(self):
        """
        Abre la conexión serial al router.
        """
        try:
            self.conexion = serial.Serial(port=self.puerto, baudrate=self.baudios, timeout=self.timeout)
            time.sleep(2)  # Espera para inicializar la consola
            print(f"[+] Conectado correctamente al router por {self.puerto} a {self.baudios} bps.")
        except serial.SerialException as e:
            print(f"[!] Error al conectar: {e}")
            self.conexion = None

    def enviar_comando(self, comando, espera=1):
        """
        Envía cualquier comando al router y retorna la salida.
        """
        if self.conexion is None:
            print("[!] No hay conexión activa.")
            return None
        
        # Enviar comando
        self.conexion.write((comando + '\n').encode())
        time.sleep(espera)  # Esperar a que el router responda
        
        # Leer toda la respuesta disponible
        salida = self.conexion.read_all().decode(errors='ignore')
        return salida

    def cerrar(self):
        """
        Cierra la conexión serial.
        """
        if self.conexion:
            self.conexion.close()
            print("[+] Conexión cerrada.")


def cargar_dispositivos(archivo_csv):
    """
    Lee el archivo CSV y devuelve una lista de objetos RouterCisco.
    """
    try:
        df = pd.read_csv(archivo_csv)
        routers = []

        for _, fila in df.iterrows():
            puerto = fila["puerto"]
            baudrate = int(fila["baudrate"])
            routers.append(RouterCisco(puerto, baudrate))

        return routers

    except FileNotFoundError:
        print("[!] Error: No se encontró el archivo CSV.")
        return []
    except KeyError as e:
        print(f"[!] Error: Falta la columna {e} en el CSV.")
        return []


if __name__ == "__main__":
    archivo = "devices.csv"  # nombre del archivo con tus dispositivos
    dispositivos = cargar_dispositivos(archivo)

    if not dispositivos:
        print("[!] No se cargaron dispositivos.")
    else:
        for router in dispositivos:
            router.conectar()
            if router.conexion:
                try:
                    while True:
                        comando = input("Ingrese comando (quit para salir): ")
                        if comando.lower() == "quit":
                            print("[*] Saliendo del programa...")
                            break
                        respuesta = router.enviar_comando(comando)
                        print(respuesta)
                finally:
                    router.cerrar()
