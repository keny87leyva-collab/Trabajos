from netmiko import ConnectHandler

cisco_device = {
    'device_type': 'cisco_ios',
    'host': '192.168.1.1',
    'username': 'admin',
    'password': 'password',
}
with ConnectHandler(**cisco_device) as conn:
 parsed = conn.send_command("show ip interface brief",
 use_textfsm=True)                                     
 for row in parsed:
    print(row['intf'], row['ipaddr'])
#hacer un script que diga el nombre del switch, el puerto_device, modelo del dispositivo y la ip del dispositivo y la mac address
#198.168.1.0/24 y que si se cambia la conexion se actualice 
#encontrar el nombre del switch, el puerto_device, modelo del dispositivo y la ip del dispositivo y la mac address