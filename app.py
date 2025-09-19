import socket
print ("hello world")
hostname= socket.gethostname()
print(f"Hostname: {hostname}")
IPAddr=socket.gethostbyname(hostname)
print(f"IP ADDRESS: {IPAddr}")
for i in range(10):
    print(i