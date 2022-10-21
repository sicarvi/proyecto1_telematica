import socket, os , time#TODO, sys
import threading
class ConexionCliente(threading.Thread):
    body = ""
    def log(self,line):
        with open("logPIBL.txt", "a") as f:
            f.write(line+'\n')
        return print(line)

    def __init__(self,ip_cliente,socket_cliente):
        threading.Thread.__init__(self, name=f"CL-{ip_cliente}")
        self.socket_cliente = socket_cliente
        self.ip_cliente = ip_cliente
        self.log(f"[NUEVA CONEXION]: {ip_cliente}")
        #self.log(f"Ip del cliente: {ip_cliente[0]}")
        
    def app_connection(self, request, puerto, ip):
        response = ""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as aplicacion:
            aplicacion.bind((puerto,ip))
            aplicacion.listen()
            socket_app, dir_ip = aplicacion.accept()
            with socket_app:
                print(f"Connected by {dir_ip}")
                socket_app.sendall(request)
                data = socket_app.recv(4096)
                response = data.decode()
                    
        return response
    
    def run(self):
        self.log(f"[NUEVO THREAD]: {self.name}")
        request = ''
        self.socket_cliente.sendall(bytes("Servidor dice hola",'UTF-8'))
        while True:
            data = self.socket_cliente.recv(4096)
            request = data.decode()
            self.log(f"* REQUEST {self.ip_cliente}* {request}")
            if request=='exit':
              break
            ip, puerto = round_robin()
            response = self.app_connection(request,ip,puerto)
            self.socket_cliente.sendall(bytes(response,'UTF-8'))
            self.log(f"* RESPONSE {self.ip_cliente}* {response}")

        self.log(f"[FINALIZO CONEXION]: {self.ip_cliente}")
        return

    

def crear_http_request(ip, body): 
    #necesito request, ip_cliente[0]
    pass

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
                    params["hosts"] = p
        return True, params
    except:
        return False, params


if __name__ == "__main__":

    check, params = setup("serv.config")

    if check:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
            servidor.bind((params["puerto"], params["hosts"]))
            print("Servidor listo y esperando")
            while True:
                servidor.listen()
                socketcliente, dircliente = servidor.accept()
                thread_cliente = ConexionCliente(dircliente, socketcliente)
                thread_cliente.start()
    else:
        print("Por favor ingrese un archivo de configuracion en el directorio establecido.")