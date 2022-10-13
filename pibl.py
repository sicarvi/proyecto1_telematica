import socket, os , time, sys
import threading

class ConexionCliente(threading.Thread):
    
    def log(self,line):
        with open("logPIBL.txt", "a") as f:
            f.write(line)
        return print(line)

    def __init__(self,ip_cliente,socket_cliente):
        threading.Thread.__init__(self, name=f"CL-{ip_cliente}")
        self.socket_cliente = socket_cliente
        self.ip_cliente = ip_cliente
        self.log(f"[NUEVA CONEXION]: {ip_cliente}")
    
    def run(self):
        self.log(f"[NUEVO THREAD]: {self.name}")
        request = ''
        while True:
            data = self.socket_cliente.recv(2048)
            request = data.decode()
            if request=='exit':
              break
            self.log(f"*REQUEST* {request}")

        self.log(f"[FINALIZO CONEXION]: {self.ip_cliente}")
        return



HOST = "127.0.0.1"
PORT = 8080

def setup(file):
    params = {}
    print(file)
    try:
        with open(file) as conf:
            for line in conf:
                if line.startswith("PUERTO"):
                    p = line[line.index("=")+1:]
                    params["puerto"] = p
                elif line.startswith("HOSTS"):
                    p = line[line.index("=")+1:]
                    p = p.split(",")
                    print(p)
                    params["hosts"] = p
        return True, params
    except:
        print("falsed")
        return False, params

if __name__ == "__main__":

    check, params = setup("serv.config")

    if check:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
            servidor.bind((HOST, PORT))
            print("Servidor listo y esperando")

            while True:
                servidor.listen()
                socketcliente, dircliente = servidor.accept()
                thread_cliente = ConexionCliente(dircliente, socketcliente)
                thread_cliente.start()
    else:
        print("Por favor ingrese un archivo de configuracion en el directorio establecido.")