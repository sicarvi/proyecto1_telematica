import socket, os , time#TODO, sys
import threading

instancia_tracker = 0
servers = []
#Clase que contiene los métodos para implementar y ejecutar el proxy inverso con balanceador de carga y concurrencia.
#Hereda de la clase Thread para crear hilos concurrentes de procesamiento.
class ProxyInverso(threading.Thread):
    #Metodo encargardo de escribir el archivo log con los eventos que registre el proxy.
    #Recibe como argumento el tipo de evento (1=request, 2=response)
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

    #Método constructor del proxy, crea un nuevo hilo de procesamiento y lo asocia a la ip y socket recibidos como argumentos.
    def __init__(self,ip_cliente,socket_cliente):
        threading.Thread.__init__(self, name=f"CL-{ip_cliente}")
        self.socket_cliente = socket_cliente
        self.ip_cliente = ip_cliente
        self.log(f"[NUEVA CONEXION]: {ip_cliente}")
        #self.log(f"Ip del cliente: {ip_cliente[0]}")
    
    #Método responsable de establecer el conexión con el servidor donde está alojada la aplicación web.
    #Establece una conexión con la ip y el puerto indicados, envía el request solicitado por el cliente y retorna el response que da el servidor.
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
    
    #Método responsable de hacer el balanceo de carga por medio de la técnica round-robin. 
    #Retorna la tupla ip,puerto en la que se debe realizar la siguiente petición.
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

    #Método responsable de almacenar un request y su respectivo response en el archivo cache.
    #Usa las etiquetas 'STARTR' y 'ENDR' para saber cuando empieza y termina cada recurso almancenado.
    #Almacena junto a cada entrada el tiempo de creación precedida por '@' para su posterior calculo de TTL.
    def set_cache(self, request, response):
        request = request[:request.index('\n')-1]
        with open("persist.cache", "ab") as f:
            t = time.time()
            f.write(f'STARTR{request} @{t}\n'.encode('utf8'))
            f.write(response)
            f.write('\n'.encode('utf8'))
            f.write('ENDR\n'.encode('utf8'))

    #Método responsable de eliminar los recursos del cache cuyo TTL haya expirado
    #Recibe como argumento el request a eliminar, y elimina el response asociado en el cache.
    def delete_entry_cache(self,target):
        target = f'STARTR{target}'.encode('utf8')
        flag = False
        with open("persist.cache", "rb") as file_input:
            with open("persist.cache", "wb") as output: 
                for line in file_input:
                    if line.rstrip() == target:
                        flag = True
                    elif line.rstrip() == b'ENDR':
                        flag = False
                    
                    if flag is False:
                        output.write(line)

    #Método responsable de consultar el cache y verificar si el request buscado y su response respectivo se encuentran almacenados.
    #Retorna el response previamente almacenado si es encontrado, de lo contrario retorna un objeto vacio.
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
                            t1 = time.time()
                            t0 = float(lineD[lineD.index('@')+1:])
                            delta = t1-t0
                            if delta < limit:
                                flag = True
                            else:
                                self.delete_entry_cache(request.rstrip())
                                break
                if flag:
                    if line.startswith(b'ENDR'):
                        break
                    if line.startswith(b'STARTR'):
                        continue
                    else:
                        responses.append(line)
                    
        if len(responses) > 0:
            response = b''.join(responses)
            return response
        else:
            return responses

    #Método responsable de la creacion de un nuevo hilo de procesamiento, además de invocar los métodos previamente definidos para escuchar las
    #peticiones del cliente y reenviarselas al servidor de aplicacion, retornando su respectiva respuesta. 
    def run(self):
        self.log(f"[NUEVO THREAD]: {self.name}")
        request = ''
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
                    #print('request se hace a ec2')
                    ip, puerto = self.round_robin()
                    response = self.app_connection(request,ip,puerto)
                    responselog = response.decode('utf-8', errors='ignore')
                    self.log(f"* RESPONSE {self.ip_cliente}* {responselog}",protocol=2)
                    self.set_cache(request,response)
                    self.socket_cliente.sendall(response)

        self.log(f"[FINALIZO CONEXION]: {self.ip_cliente}")
        return

#Método responsable de analizar el archivo de configuración definido y parametrizar la dirección IP y el puerto en el que se configura el proxy.
#Además define la lista de direcciones IP de los servidores donde está alojada la apliación web.
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

#Método main que invoca el setup y define un bucle infinito para que el servidor proxy empiece a esuchar peticiones.
if __name__ == "__main__":

    check, params = setup("serv.config")

    if check:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
            
            servidor.bind((params["proxy"].rstrip(), params["puerto"]))
            print("Servidor listo y esperando")
            while True:
                servidor.listen()
                socketcliente, dircliente = servidor.accept()
                thread_cliente = ProxyInverso(dircliente, socketcliente)
                thread_cliente.start()
    else:
        print("Por favor ingrese un archivo de configuracion en el directorio establecido.")