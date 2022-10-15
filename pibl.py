import socket, os , time, sys
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
        

    
    def run(self):
        self.log(f"[NUEVO THREAD]: {self.name}")
        request = ''
        self.socket_cliente.sendall(bytes("Servidor dice hola",'UTF-8'))
        while True:
            data = self.socket_cliente.recv(2048)
            request = data.decode()
            if request=='exit':
              break
            self.socket_cliente.send(bytes(request,'UTF-8'))#echo para permitir envio continuo
            self.log(f"* REQUEST {self.ip_cliente}* {request}")

        self.log(f"[FINALIZO CONEXION]: {self.ip_cliente}")
        return

    def crearHttp(ip, body): 
        #necesito request, ip_cliente[0]

        pass



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
                    params["hosts"] = p
        return True, params
    except:
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