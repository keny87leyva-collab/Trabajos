import socket
print ("hello world")
hostname= socket.gethostname()
print(f"Hostname: {hostname}")
IPAddr=socket.gethostbyname(hostname)
print(f"IP ADDRESS: {IPAddr}")
for i in range(10):
    print(f"count: {i}")
numero_a = int(input("Dame el primer numero: "))
numero_b = int(input("Dame el segundo numero: "))
suma = numero_a + numero_b
resta = numero_a - numero_b
multiplicacion = numero_a * numero_b
print(f"La suma de los numeros es: {suma}")
print(f"La resta de los numeros es: {resta}")
print(f"La multiplicación de los numeros es: {multiplicacion}")