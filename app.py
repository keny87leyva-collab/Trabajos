import socket
print ("hello world")
hostname= socket.gethostname()
print(f"Hostname: {hostname}")
IPAddr=socket.gethostbyname(hostname)
print(f"IP ADDRESS: {IPAddr}")
for i in range(10):
    print(f"count: {i}")
numero_a= input("dame el primer numero: ")
numero_b=input("dame el segundo numero: ")
resultado=numero_a+numero_b
print (resultado)