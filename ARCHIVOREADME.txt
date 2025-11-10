Descripcion
Este script en Python permite rastrear en qué puerto de un switch Cisco se encuentra conectado un host, partiendo únicamente de su direccion IP.
Automatiza el proceso que normalmente se realiza manualmente con los comandos:
show ip arp
show mac address-table
show cdp neighbors
El programa se conecta automaticamente al switch Core de la red, busca la MAC address asociada a la IP objetivo, localiza el puerto fisico donde se encuentra, y sigue los enlaces entre switches hasta identificar el dispositivo final.

Requerimientos
Python 3.x
Libreria Netmiko instalada:
pip install netmiko
Credenciales validas para acceder a los switches Cisco.
Conectividad IP con el switch Core y los dispositivos de red.
Como funciona el script
Obtiene las IPs activas de la red local
obtener_ips_arp()
Identifica el switch Core
identificar_switches(ips_encontradas)
Intenta conectarse con Netmiko a la IP del switch Core.
Solicita la IP del host a rastrear
El programa pide al usuario ingresar la IP del dispositivo que se desea ubicar.
Busca la MAC address asociada a la IP
show ip arp <ip_objetivo>
De aqui se obtiene la direccion MAC del host.
Localiza el puerto donde se aprendio esa MAC
show mac address-table address <mac>
Devuelve la VLAN y el puerto fisico donde está registrada la direccion MAC.
Analiza si el puerto esta conectado a otro switch
show cdp neighbors detail
Si detecta un vecino, el script se conecta automaticamente a ese switch y repite el proceso hasta llegar al host final.
Muestra el resultado
Cuando encuentra el dispositivo final, imprime la informacion completa:
HOST DETECTADO:
   Switch: SW1
   Puerto: Fa1/0/2
   VLAN: 10
   MAC: c8a3.62ec.e9c7
   IP: 192.168.1.41

Estructura del codigo
Función	Descripción
obtener_ips_arp()	Escanea las IPs activas de la red local.
identificar_switches()	Detecta la IP del switch Core.
buscar_mac_por_ip()	Obtiene la MAC correspondiente a una IP desde la tabla ARP.
buscar_puerto_por_mac()	Encuentra el puerto donde se aprendió la MAC.
obtener_vecinos()	Lista los vecinos detectados por CDP.
rastrear_dispositivo()	Recorre los switches hasta hallar el host final.
Ejemplo de uso
python rastreo_switches.py
Salida esperada:
Identificando switches Cisco...
Ingresa la IP que deseas localizar: 192.168.1.41
HOST DETECTADO:
   Switch: SW2
   Puerto: Fa1/0/3
   VLAN: 10
   MAC: c8a3.62ec.e9c7
   IP: 192.168.1.41
Conclusion
Este script automatiza completamente la búsqueda manual que normalmente se realiza en los switches, ahorrando tiempo y reduciendo errores humanos.
Resulta util para:
Rastrear dispositivos extraviados en la red.
Verificar conexiones físicas.
Documentar topologías de red de forma rapida y eficiente.