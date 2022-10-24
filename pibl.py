import socket, os , time#TODO, sys
import threading

instancia_tracker = 0
servers = []
class ConexionCliente(threading.Thread):
    body = ""
    def log(self,line, protocol=0):
        if len(line)>=34:
            if protocol == 1:
                line = line[:line.index('\n')-1] 
            elif protocol == 2:
                line = line[:line.index('\r')]
            t = time.localtime()
            line = f'({time.strftime("%H:%M:%S", t)}) {line}'
                
            with open("logPIBL.txt", "a") as f:
                    f.write(line+'\n')
            print(line)


    def __init__(self,ip_cliente,socket_cliente):
        threading.Thread.__init__(self, name=f"CL-{ip_cliente}")
        self.socket_cliente = socket_cliente
        self.ip_cliente = ip_cliente
        self.log(f"[NUEVA CONEXION]: {ip_cliente}")
        #self.log(f"Ip del cliente: {ip_cliente[0]}")
        
    def app_connection(self, request, ip, puerto):
        response = ""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as aplicacion:
            aplicacion.connect((ip, puerto))
            #print(f"Connected to {ip}")
            aplicacion.sendall(bytes(request,'UTF-8'))
            responses = []
            parciales = aplicacion.recv(4096)
            responses.append(parciales)
            while (len(parciales) > 0):
                parciales = aplicacion.recv(4096)
                responses.append(parciales)
            response = b''.join(responses)
                    
        return response
    
    def round_robin(self):
        global instancia_tracker
        global servers
        with threading.Lock() as lock:      
            ip = servers[instancia_tracker][0]
            puerto = int(servers[instancia_tracker][1])
            if instancia_tracker == 2:
                instancia_tracker = 0
            else:
                instancia_tracker+=1
            self.log(f"[PETICION REALIZADA]: {ip}")
            return ip, puerto

    def set_cache(self, request, response):
        request = request[:request.index('\n')-1]
        with open("persist.cache", "ab") as f:
            t = time.time()
            f.write(f'STARTR{request} @{t}\n'.encode('utf8'))
            f.write(response)
            f.write('\n'.encode('utf8'))
            f.write('ENDR\n'.encode('utf8'))


    def retrieve_cache(self, request):
        limit = 60
        request = request[:request.index('\n')]
        delta = 0
        responses = []
        flag = False
        with open("persist.cache", "rb") as f:
            for line in f:
                if not flag:
                    if line.startswith(b'STARTR'):
                        lineD = line.decode('utf8')
                        if request.rstrip() == lineD[6:lineD.index('@')-1].rstrip():
                            print('SON IGUALES!!')
                            t1 = time.time()
                            t0 = float(lineD[lineD.index('@')+1:])
                            delta = t1-t0
                            if delta < limit:
                                flag = True
                            #TODO else: violentar ese entry
                if flag:
                    if line.startswith(b'ENDR'):
                        break
                    if line.startswith(b'STARTR'):
                        continue
                    else:
                        #print("AGREGUE ALGO!!!")
                        responses.append(line)
                    

        #print("responses:",responses)
        if len(responses) > 0:
            print('habemus cache')
            response = b''.join(responses)
            return response
        else:
            print('no encontro ni mierda')
            return responses


    def run(self):
        self.log(f"[NUEVO THREAD]: {self.name}")
        request = ''
        #self.socket_cliente.sendall(bytes("Servidor dice hola",'UTF-8'))
        while True:
            data = self.socket_cliente.recv(4096)
            request = data.decode()
            self.log(f"* REQUEST {self.ip_cliente}* {request}", protocol=1)
            if request=='exit':
              break
            if len(request) > 1:
                r_cache = self.retrieve_cache(request)
                if len(r_cache) > 0:
                    responselog = r_cache.decode('utf-8', errors='ignore')
                    self.log(f"* RESPONSE CACHE {self.ip_cliente}* {responselog}",protocol=2)
                    self.socket_cliente.sendall(r_cache)
                else:
                    print('request se hace a ec2')
                    ip, puerto = self.round_robin()
                    response = self.app_connection(request,ip,puerto)
                    responselog = response.decode('utf-8', errors='ignore')
                    self.log(f"* RESPONSE {self.ip_cliente}* {responselog}",protocol=2)
                    self.set_cache(request,response)
                    self.socket_cliente.sendall(response)

        self.log(f"[FINALIZO CONEXION]: {self.ip_cliente}")
        return

def setup(file):
    params = {}
    print(file)
    global servers
    try:
        with open(file) as conf:
            for line in conf:
                if line.startswith("PUERTO"):
                    p = line[line.index("=")+1:]
                    params["puerto"] = int(p)
                elif line.startswith("PROXY"):
                    p = line[line.index("=")+1:]
                    params["proxy"] = p
                elif line.startswith("SERVERS"):
                    p = line[line.index("=")+1:]
                    p = p.split(',')
                    for serv in p:
                        servers.append(tuple(serv.split(':')))
        return True, params
    except:
        return False, params


if __name__ == "__main__":

    check, params = setup("serv.config")

    if check:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
            
            servidor.bind((params["proxy"].rstrip(), params["puerto"]))
            print("Servidor listo y esperando")
            while True:
                servidor.listen()
                socketcliente, dircliente = servidor.accept()
                thread_cliente = ConexionCliente(dircliente, socketcliente)
                thread_cliente.start()
    else:
        print("Por favor ingrese un archivo de configuracion en el directorio establecido.")